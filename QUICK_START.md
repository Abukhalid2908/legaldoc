# 🚀 Quick Start Guide - Agreement Management System

Panduan cepat untuk menjalankan aplikasi dalam 5 menit!

---

## ⚡ Setup Cepat (5 Menit)

### 1. Persiapan
```powershell
# Masuk ke folder project
cd C:\xampp\htdocs\legaldoc

# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Start MySQL
- Buka **XAMPP Control Panel**
- Klik **Start** pada **MySQL**

### 4. Setup Database
```powershell
python reset_db_full.py
```

### 5. Jalankan Aplikasi
```powershell
uvicorn main:app --reload
```

### 6. Akses Aplikasi
Buka browser: **http://localhost:8000**

---

## 🔑 Login

**Username:** `admin`  
**Password:** `admin123`

---

## 📤 Upload Dokumen (3 Langkah)

1. **Login** ke admin dashboard
2. **Isi form** di tab "Upload Baru":
   - Judul Perjanjian
   - Ringkasan
   - Penandatangan
   - File PDF
3. **Klik** "Upload Document"

✅ **Selesai!** QR Code otomatis ter-generate.

---

## 📱 Verifikasi Dokumen

### Cara 1: Scan QR Code
1. Buka kamera HP
2. Scan QR code
3. Lihat detail dokumen

### Cara 2: Manual
1. Copy hash dokumen (klik icon clipboard)
2. Buka: `http://localhost:8000/verify/{hash}`
3. Lihat detail dokumen

---

## 🛠️ Troubleshooting Cepat

### Error: Module 'jose' not found
```powershell
pip install python-jose[cryptography]
```

### Error: Database connection failed
```powershell
# Pastikan MySQL running, lalu:
python reset_db_full.py
```

### Error: Port 8000 sudah digunakan
```powershell
uvicorn main:app --reload --port 8001
```

---

## 📚 Dokumentasi Lengkap

Lihat **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** untuk:
- Deployment production
- API endpoints lengkap
- Troubleshooting detail
- Security best practices

---

**Selamat Menggunakan! 🎉**
