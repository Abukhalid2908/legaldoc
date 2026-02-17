# 📋 Agreement Management System (AMS)
## Dokumentasi Deployment & Penggunaan

Sistem manajemen dokumen perjanjian dengan fitur verifikasi menggunakan QR Code dan SHA-256 hashing.

---

## 📑 Daftar Isi

1. [Persyaratan Sistem](#persyaratan-sistem)
2. [Instalasi & Setup](#instalasi--setup)
3. [Deployment](#deployment)
4. [Cara Penggunaan](#cara-penggunaan)
5. [Fitur Utama](#fitur-utama)
6. [Troubleshooting](#troubleshooting)
7. [API Endpoints](#api-endpoints)

---

## 🖥️ Persyaratan Sistem

### Software yang Dibutuhkan:
- **Python 3.11+**
- **MySQL Server** (XAMPP/standalone)
- **Web Browser** modern (Chrome, Firefox, Edge)

### Python Dependencies:
```
fastapi
uvicorn
sqlalchemy
pymysql
python-multipart
qrcode[pil]
python-jose[cryptography]
passlib
```

---

## 🚀 Instalasi & Setup

### 1. Clone/Download Project
```bash
cd C:\xampp\htdocs
# Pastikan folder legaldoc sudah ada dengan semua file
```

### 2. Buat Virtual Environment
```powershell
cd C:\xampp\htdocs\legaldoc
python -m venv .venv
```

### 3. Aktivasi Virtual Environment
```powershell
.venv\Scripts\Activate.ps1
```

Jika ada error execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Setup Database

#### a. Start MySQL Server
- Buka XAMPP Control Panel
- Start **Apache** dan **MySQL**

#### b. Reset & Initialize Database
```powershell
python reset_db_full.py
```

Output yang benar:
```
Resetting database...
Database 'db_perjanjian' recreated.
Tables created successfully.
Default admin created: admin / admin123
```

### 6. Verifikasi Struktur Folder

Pastikan folder berikut ada:
```
legaldoc/
├── static/
│   ├── docs/          # Untuk file PDF dokumen
│   ├── qr/            # Untuk QR code images
│   ├── index.html
│   ├── login.html
│   ├── admin_dashboard.html
│   └── verify.html
├── .venv/
├── main.py
├── models.py
├── database.py
├── utils.py
├── requirements.txt
└── reset_db_full.py
```

---

## 🌐 Deployment

### Development Mode (Local)

1. **Aktivasi Virtual Environment**
```powershell
cd C:\xampp\htdocs\legaldoc
.venv\Scripts\Activate.ps1
```

2. **Start Server**
```powershell
uvicorn main:app --reload
```

3. **Akses Aplikasi**
- **Homepage**: http://localhost:8000
- **Login**: http://localhost:8000/login
- **Admin Dashboard**: http://localhost:8000/admin

### Production Mode

Untuk production, gunakan Gunicorn (Linux) atau Waitress (Windows):

#### Windows (Waitress):
```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 main:app
```

#### Linux (Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Deployment ke Server

#### 1. Update Configuration

Edit `main.py` untuk production:
```python
# Ganti SECRET_KEY dengan nilai random
SECRET_KEY = "your-super-secret-key-here-use-secrets.token_urlsafe()"

# Update QR Code URL untuk production
verification_url = f"https://yourdomain.com/verify/{file_hash}"
```

#### 2. Setup Database Production

Update `database.py`:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@host/db_perjanjian"
```

#### 3. Setup Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/legaldoc/static;
    }
}
```

#### 4. Setup Systemd Service (Linux)

Create `/etc/systemd/system/ams.service`:
```ini
[Unit]
Description=Agreement Management System
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/legaldoc
Environment="PATH=/path/to/legaldoc/.venv/bin"
ExecStart=/path/to/legaldoc/.venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable dan start:
```bash
sudo systemctl enable ams
sudo systemctl start ams
```

---

## 📖 Cara Penggunaan

### A. Login Admin

1. Buka browser, akses: http://localhost:8000/login
2. Masukkan kredensial default:
   - **Username**: `admin`
   - **Password**: `admin123`
3. Klik **Login**

### B. Upload Dokumen Baru (v1)

1. Setelah login, Anda akan masuk ke **Admin Dashboard**
2. Di tab **"Upload Baru"**:
   - **Judul Perjanjian**: Masukkan judul (contoh: "Sewa Ruko Tahun 2026")
   - **Ringkasan**: Deskripsi singkat dokumen
   - **Penandatangan**: Nama pihak yang menandatangani (contoh: "PT ABC & PT XYZ")
   - **File PDF**: Pilih file PDF dokumen
3. Klik **Upload Document**
4. Sistem akan otomatis:
   - Generate hash SHA-256
   - Generate QR Code
   - Simpan ke database sebagai v1

### C. Melihat & Mengelola Dokumen

1. Klik tab **"Manajemen Dokumen"**
2. Tabel akan menampilkan:
   - **ID**: Nomor urut dokumen
   - **Judul & Versi**: Nama dokumen dan versi (v1, v2, dst)
   - **Info**: Hash (dipotong) dan tanggal upload
   - **QR Code**: Gambar QR code (klik untuk perbesar)
   - **Aksi**: Tombol View dan + Versi Baru

#### Copy Hash Dokumen:
- **Hover** mouse di atas hash untuk lihat nilai lengkap
- Klik **icon clipboard** untuk copy hash ke clipboard
- Hash akan di-copy dan muncul alert konfirmasi

### D. Upload Versi Baru Dokumen

1. Di tabel dokumen, klik tombol **"+ Versi Baru"**
2. Modal akan muncul:
   - **Catatan Revisi**: Jelaskan perubahan (contoh: "Revisi klausul pembayaran")
   - **File Baru**: Pilih file PDF versi baru
3. Klik **Upload Revisi**
4. Sistem akan:
   - Generate hash baru
   - Generate QR code baru
   - Increment versi (v2, v3, dst)
   - Link ke dokumen parent

### E. Verifikasi Dokumen (End User)

#### Metode 1: Scan QR Code
1. Buka kamera HP atau aplikasi QR scanner
2. Scan QR code pada dokumen fisik/digital
3. Browser akan otomatis membuka halaman verifikasi
4. Lihat detail dokumen:
   - Status validitas (✓ Valid / ✗ Tidak Valid)
   - Judul dokumen
   - Versi
   - Tanggal upload
   - Hash SHA-256 lengkap

#### Metode 2: Manual Verification
1. Buka: http://localhost:8000/verify/{hash}
2. Ganti `{hash}` dengan hash dokumen (64 karakter)
3. Contoh: http://localhost:8000/verify/9c4cb1b249d5c796cf96cf08d1cba8d450cf61e6c130ea79eaa8b4d635dc8e9c

### F. Logout
Klik tombol **Logout** di pojok kanan atas navbar

---

## ✨ Fitur Utama

### 1. **Authentication & Authorization**
- Login dengan username/password
- Role-based access (Admin/User)
- JWT token authentication
- Session management

### 2. **Document Management**
- Upload dokumen PDF
- Auto-generate SHA-256 hash
- Auto-generate QR Code
- Versioning system (v1, v2, v3...)
- Duplicate detection (berdasarkan hash)

### 3. **QR Code System**
- QR code berisi URL verifikasi lengkap
- Format: `http://domain.com/verify/{hash}`
- Scannable dengan kamera HP
- Redirect ke halaman verifikasi

### 4. **Verification Page**
- Responsive design (mobile-friendly)
- Real-time validation
- Tampilan detail dokumen
- Copy hash functionality
- Status indicator (Valid/Invalid)

### 5. **Hash Management**
- SHA-256 hashing
- Tooltip untuk lihat hash lengkap
- One-click copy to clipboard
- Fallback untuk browser lama

---

## 🔧 Troubleshooting

### Problem 1: ModuleNotFoundError: No module named 'jose'
**Solusi:**
```powershell
.venv\Scripts\Activate.ps1
pip install python-jose[cryptography]
```

### Problem 2: Database Connection Error
**Solusi:**
1. Pastikan MySQL running di XAMPP
2. Cek kredensial di `database.py`
3. Reset database:
```powershell
python reset_db_full.py
```

### Problem 3: QR Code Tidak Muncul
**Solusi:**
1. Pastikan folder `static/qr/` ada
2. Cek permission folder (harus writable)
3. Upload dokumen baru untuk generate QR code baru

### Problem 4: Hash Tidak Ditemukan
**Penyebab:** Database di-reset tapi QR code lama masih ada

**Solusi:**
```powershell
# Hapus QR code lama
Remove-Item C:\xampp\htdocs\legaldoc\static\qr\*.png
# Upload dokumen baru
```

### Problem 5: Port 8000 Already in Use
**Solusi:**
```powershell
# Gunakan port lain
uvicorn main:app --reload --port 8001
```

### Problem 6: Execution Policy Error (PowerShell)
**Solusi:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | Login dan dapatkan token | No |
| GET | `/login` | Halaman login HTML | No |

### Documents
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Homepage | No |
| GET | `/admin` | Admin dashboard | Yes (Admin) |
| POST | `/agreements/` | Upload dokumen baru (v1) | Yes (Admin) |
| GET | `/agreements/` | List semua dokumen | No |
| POST | `/agreements/{id}/version` | Upload versi baru | Yes (Admin) |

### Verification
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/verify/{hash}` | Halaman verifikasi HTML | No |
| GET | `/api/verify/{hash}` | API verifikasi (JSON) | No |

### Request Examples

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "admin"
}
```

#### Upload Document
```bash
curl -X POST "http://localhost:8000/agreements/" \
  -H "Authorization: Bearer {token}" \
  -F "title=Sewa Ruko" \
  -F "content_summary=Perjanjian sewa ruko 2026" \
  -F "signers=PT ABC & PT XYZ" \
  -F "file=@document.pdf"
```

#### Verify Document
```bash
curl "http://localhost:8000/api/verify/9c4cb1b249d5c796cf96cf08d1cba8d450cf61e6c130ea79eaa8b4d635dc8e9c"
```

Response:
```json
{
  "status": "Valid",
  "agreement": {
    "title": "Sewa Ruko",
    "version": 1,
    "timestamp": "2026-02-16T08:11:05",
    "is_latest": true
  }
}
```

---

## 📝 Catatan Penting

### Keamanan
1. **Ganti SECRET_KEY** di production
2. Gunakan **HTTPS** untuk production
3. Jangan commit `.env` file ke git
4. Update password admin default
5. Implement rate limiting untuk API

### Backup
1. Backup database secara berkala:
```bash
mysqldump -u root db_perjanjian > backup.sql
```

2. Backup folder `static/docs/` dan `static/qr/`

### Maintenance
1. Monitor disk space (folder `static/docs/` dan `static/qr/`)
2. Clean up old QR codes jika perlu
3. Update dependencies secara berkala:
```powershell
pip install --upgrade -r requirements.txt
```

---

## 👥 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

⚠️ **PENTING**: Ganti password default setelah deployment pertama!

---

## 📞 Support

Untuk pertanyaan atau issue, hubungi administrator sistem.

---

**Versi Dokumentasi**: 1.0  
**Terakhir Diupdate**: 16 Februari 2026
