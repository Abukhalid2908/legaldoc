from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="user")  # 'admin' or 'user'
    
    agreements = relationship("Agreement", back_populates="uploader")

class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content_summary = Column(Text)
    signers = Column(Text)
    document_hash = Column(String(64), unique=True, index=True)
    file_path = Column(String(255))
    qr_code_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Versioning & Audit
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("agreements.id"), nullable=True) # Versi sebelumnya
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True) # Untuk soft delete atau hide old versions
    
    uploader = relationship("User", back_populates="agreements")
    versions = relationship("Agreement", backref="parent", remote_side=[id])
