from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from database import engine, get_db, Base
from models import Agreement, User
import utils

# Buat tabel database jika belum ada
Base.metadata.create_all(bind=engine)

# AUTH CONFIG
SECRET_KEY = "supersecretkey" # Ganti dengan env var di production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

app = FastAPI(title="Agreement Management System")

# Mount folder static untuk akses file
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/auth/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.get("/login")
async def read_login():
    return FileResponse('static/login.html')

@app.get("/admin")
async def read_admin():
    return FileResponse('static/admin_dashboard.html')

@app.post("/agreements/")
async def create_agreement(
    title: str = Form(...),
    content_summary: str = Form(...),
    signers: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. Simpan file fisik sementara/permanen
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = f"static/docs/{unique_filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Hitung Hash File
    file_hash = utils.calculate_file_hash(file_location)
    
    # Cek apakah hash sudah ada (mencegah duplikasi dokumen yang sama persis)
    existing_agreement = db.query(Agreement).filter(Agreement.document_hash == file_hash).first()
    if existing_agreement:
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="Document with this content already exists.")

    # 3. Generate QR Code with verification URL
    qr_filename = f"{file_hash}.png"
    qr_location = f"static/qr/{qr_filename}"
    verification_url = f"http://localhost:8000/verify/{file_hash}"
    utils.generate_qr_code(verification_url, qr_location)
    
    # 4. Simpan ke Database (v1)
    new_agreement = Agreement(
        title=title,
        content_summary=content_summary,
        signers=signers,
        document_hash=file_hash,
        file_path=file_location,
        qr_code_path=qr_location,
        uploaded_by=current_user.id,
        version=1,
        parent_id=None
    )
    
    db.add(new_agreement)
    db.commit()
    db.refresh(new_agreement)
    
    return {"message": "Agreement v1 registered successfully", "data": new_agreement}

@app.post("/agreements/{id}/version")
async def create_new_version(
    id: int,
    file: UploadFile = File(...),
    content_summary: str = Form(...), # Optional update summary
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    parent_agreement = db.query(Agreement).filter(Agreement.id == id).first()
    if not parent_agreement:
        raise HTTPException(status_code=404, detail="Parent agreement not found")

    # 1. Simpan file baru
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = f"static/docs/{unique_filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Hitung Hash
    file_hash = utils.calculate_file_hash(file_location)
    
    existing_agreement = db.query(Agreement).filter(Agreement.document_hash == file_hash).first()
    if existing_agreement:
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="This specific version already exists.")

    # 3. QR Code with verification URL
    qr_filename = f"{file_hash}.png"
    qr_location = f"static/qr/{qr_filename}"
    verification_url = f"http://localhost:8000/verify/{file_hash}"
    utils.generate_qr_code(verification_url, qr_location)
    
    # 4. Determine Version Number & Root Parent
    # Jika parent_id None, berarti dia Root. Jika tidak, ikut parent_id nya.
    root_id = parent_agreement.parent_id if parent_agreement.parent_id else parent_agreement.id
    
    # Cari versi terakhir dari root ini
    last_version = db.query(Agreement).filter(
        (Agreement.id == root_id) | (Agreement.parent_id == root_id)
    ).order_by(Agreement.version.desc()).first()
    
    new_version_number = last_version.version + 1
    
    new_agreement = Agreement(
        title=parent_agreement.title, # Judul sama dengan parent
        content_summary=content_summary, # Summary bisa beda (changelog)
        signers=parent_agreement.signers, # Asumsi signer sama, atau bisa diupdate via Form user
        document_hash=file_hash,
        file_path=file_location,
        qr_code_path=qr_location,
        uploaded_by=current_user.id,
        version=new_version_number,
        parent_id=root_id
    )
    
    db.add(new_agreement)
    db.commit()
    
    return {"message": f"Agreement v{new_version_number} registered successfully", "data": new_agreement}

@app.get("/agreements/")
def read_agreements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Return all for now. Frontend can filter.
    # In production, we might want to return nested JSON.
    agreements = db.query(Agreement).order_by(Agreement.created_at.desc()).offset(skip).limit(limit).all()
    return agreements

@app.get("/verify/{document_hash}")
async def verify_agreement(document_hash: str, db: Session = Depends(get_db)):
    agreement = db.query(Agreement).filter(Agreement.document_hash == document_hash).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Document not found or invalid hash")
    
    # Return HTML page for browser, JSON for API
    return FileResponse('static/verify.html')

@app.get("/api/verify/{document_hash}")
def verify_agreement_api(document_hash: str, db: Session = Depends(get_db)):
    agreement = db.query(Agreement).filter(Agreement.document_hash == document_hash).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Document not found or invalid hash")
    
    return {
        "status": "Valid",
        "agreement": {
            "title": agreement.title,
            "version": agreement.version,
            "timestamp": agreement.created_at,
            "is_latest": True # Simplification, logic to check if new version exists is complex
        }
    }

