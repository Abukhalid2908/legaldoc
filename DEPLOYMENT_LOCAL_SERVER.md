# 🖥️ Panduan Deploy ke Server Lokal (PC Lain di Jaringan)

Panduan lengkap untuk menjalankan Agreement Management System di PC server lokal dan mengaksesnya dari PC/HP lain dalam jaringan yang sama.

---

## 📋 Skenario Deployment

**PC Server** (tempat aplikasi berjalan):
- IP: Misalnya `192.168.1.100`
- Menjalankan aplikasi + MySQL

**PC Client** (mengakses aplikasi):
- IP: Misalnya `192.168.1.101`, `192.168.1.102`, dll
- Akses via browser: `http://192.168.1.100:8000`

---

## 🚀 Setup di PC Server

### 1. Clone Repository dari GitHub

```powershell
# Pilih lokasi untuk project
cd C:\

# Clone dari GitHub
git clone https://github.com/Abukhalid2908/legaldoc.git
cd legaldoc
```

### 2. Install Dependencies

```powershell
# Buat virtual environment
python -m venv .venv

# Aktivasi
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup MySQL Database

#### a. Install XAMPP
- Download: https://www.apachefriends.org/download.html
- Install dan start **MySQL**

#### b. Initialize Database
```powershell
python reset_db_full.py
```

### 4. Konfigurasi untuk Akses LAN

#### a. Cek IP Address PC Server
```powershell
ipconfig
```
Cari **IPv4 Address**, contoh: `192.168.1.100`

#### b. Update `main.py` untuk QR Code URL

Edit file `main.py`, ganti `localhost` dengan IP server:

```python
# Cari baris ini (ada 2 tempat):
verification_url = f"http://localhost:8000/verify/{file_hash}"

# Ganti dengan IP server Anda:
verification_url = f"http://192.168.1.100:8000/verify/{file_hash}"
```

**Lokasi yang perlu diganti:**
- Line ~124: Saat upload dokumen baru
- Line ~179: Saat upload versi baru

### 5. Jalankan Aplikasi untuk Akses LAN

```powershell
# Jalankan dengan bind ke semua network interface
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Penting:** `--host 0.0.0.0` membuat aplikasi bisa diakses dari PC lain!

### 6. Konfigurasi Windows Firewall

#### Opsi 1: Buka Port Secara Manual
```powershell
# Jalankan sebagai Administrator
New-NetFirewallRule -DisplayName "Agreement Management System" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

#### Opsi 2: Via GUI
1. Buka **Windows Defender Firewall**
2. Klik **Advanced Settings**
3. Klik **Inbound Rules** → **New Rule**
4. Pilih **Port** → Next
5. **TCP**, **Specific local ports**: `8000` → Next
6. **Allow the connection** → Next
7. Centang semua (Domain, Private, Public) → Next
8. Name: `AMS Port 8000` → Finish

---

## 📱 Akses dari PC/HP Lain

### Dari PC Client (Windows/Mac/Linux)

1. Buka browser
2. Akses: `http://192.168.1.100:8000`
   - Ganti `192.168.1.100` dengan IP server Anda
3. Login dengan: `admin` / `admin123`

### Dari HP/Tablet (Android/iOS)

1. Pastikan HP terhubung ke **WiFi yang sama**
2. Buka browser (Chrome/Safari)
3. Akses: `http://192.168.1.100:8000`
4. Login dan gunakan seperti biasa

### Test Koneksi

Dari PC client, test koneksi:
```powershell
# Test ping
ping 192.168.1.100

# Test port (PowerShell)
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
```

---

## 🔧 Troubleshooting

### Problem 1: Tidak Bisa Akses dari PC Lain

**Cek:**
1. Firewall Windows sudah dibuka untuk port 8000?
2. Aplikasi berjalan dengan `--host 0.0.0.0`?
3. PC Server dan Client di network yang sama?

**Solusi:**
```powershell
# Matikan firewall sementara untuk test
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Jika berhasil, berarti masalah di firewall
# Aktifkan lagi dan buka port 8000
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

### Problem 2: QR Code Mengarah ke localhost

**Penyebab:** Belum update IP di `main.py`

**Solusi:** Update kedua baris di `main.py` seperti dijelaskan di atas.

### Problem 3: Database Connection Error

**Penyebab:** MySQL tidak bisa diakses dari network

**Solusi:** 
1. Edit `C:\xampp\mysql\bin\my.ini`
2. Cari `bind-address = 127.0.0.1`
3. Ganti dengan `bind-address = 0.0.0.0`
4. Restart MySQL di XAMPP

---

## 🌐 Setup Static IP (Opsional tapi Direkomendasikan)

Agar IP server tidak berubah-ubah:

### Windows:
1. **Control Panel** → **Network and Sharing Center**
2. Klik adapter network Anda
3. **Properties** → **Internet Protocol Version 4 (TCP/IPv4)**
4. Pilih **Use the following IP address**:
   - IP address: `192.168.1.100` (sesuaikan)
   - Subnet mask: `255.255.255.0`
   - Default gateway: `192.168.1.1` (IP router)
   - DNS: `8.8.8.8` (Google DNS)

---

## 🔒 Keamanan untuk LAN

### 1. Ganti Password Default
```powershell
python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['pbkdf2_sha256']); print(pwd_context.hash('password_baru_anda'))"
```

Update di database atau buat user baru via script.

### 2. Batasi Akses (Opsional)

Edit `main.py`, tambahkan middleware untuk IP whitelist:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

ALLOWED_IPS = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]

@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        return JSONResponse(
            status_code=403,
            content={"detail": "Access denied"}
        )
    return await call_next(request)
```

---

## 📊 Monitoring & Maintenance

### 1. Auto-Start saat PC Nyala

Buat file `start_ams.bat`:
```batch
@echo off
cd C:\legaldoc
call .venv\Scripts\activate.bat
uvicorn main:app --host 0.0.0.0 --port 8000
```

Tambahkan ke **Task Scheduler** atau **Startup folder**.

### 2. Monitoring Log

```powershell
# Jalankan dengan logging
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info > logs.txt 2>&1
```

### 3. Backup Database Berkala

Buat script `backup_db.bat`:
```batch
@echo off
set BACKUP_DIR=C:\backups\ams
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

C:\xampp\mysql\bin\mysqldump.exe -u root db_perjanjian > %BACKUP_DIR%\backup_%TIMESTAMP%.sql
```

Jalankan via Task Scheduler setiap hari.

---

## 🎯 Checklist Deployment

- [ ] Clone repository dari GitHub
- [ ] Install Python dependencies
- [ ] Setup MySQL database
- [ ] Update IP di `main.py` (2 tempat)
- [ ] Jalankan dengan `--host 0.0.0.0`
- [ ] Buka port 8000 di firewall
- [ ] Test akses dari PC lain
- [ ] Test scan QR code dari HP
- [ ] Setup static IP (opsional)
- [ ] Ganti password default
- [ ] Setup auto-start (opsional)
- [ ] Setup backup database (opsional)

---

## 📞 Quick Reference

### Akses Aplikasi
```
http://[IP_SERVER]:8000
Contoh: http://192.168.1.100:8000
```

### Login Default
```
Username: admin
Password: admin123
```

### Command untuk Start
```powershell
cd C:\legaldoc
.venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Cek IP Server
```powershell
ipconfig | findstr IPv4
```

---

**Versi Dokumentasi**: 1.0  
**Terakhir Diupdate**: 17 Februari 2026
