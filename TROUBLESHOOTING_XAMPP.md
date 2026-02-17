# 🔧 Troubleshooting XAMPP MySQL - Agreement Management System

## Masalah: XAMPP MySQL Tidak Stabil

Jika Anda mengalami error seperti:
```
An existing connection was forcibly closed by the remote host
OperationalError: (2013, 'Lost connection to MySQL server')
```

---

## ✅ Solusi yang Sudah Diterapkan

### 1. Database Connection Pooling
File `database.py` sudah di-update dengan:
- **`pool_pre_ping=True`** - Test koneksi sebelum digunakan
- **`pool_recycle=3600`** - Recycle koneksi setiap 1 jam
- **`pool_size=10`** - Pool size untuk handle multiple requests
- **`max_overflow=20`** - Extra connections saat traffic tinggi

Ini akan **otomatis reconnect** jika koneksi terputus!

---

## 🛠️ Perbaikan XAMPP

### Opsi 1: Konfigurasi MySQL di XAMPP

1. **Buka XAMPP Control Panel**
2. **Stop MySQL**
3. **Klik "Config" → "my.ini"**
4. **Tambahkan/Update** konfigurasi berikut:

```ini
[mysqld]
# Connection Settings
max_connections = 200
connect_timeout = 60
wait_timeout = 28800
interactive_timeout = 28800

# Buffer Settings
innodb_buffer_pool_size = 256M
key_buffer_size = 128M

# Log Settings (optional, untuk debugging)
log_error = "mysql_error.log"
```

5. **Save** file
6. **Start MySQL** lagi

### Opsi 2: Restart MySQL Secara Berkala

Jika masih tidak stabil, restart MySQL setiap kali sebelum menjalankan aplikasi:

```powershell
# Di XAMPP Control Panel:
# 1. Stop MySQL
# 2. Start MySQL
# 3. Tunggu sampai status "Running"
# 4. Baru jalankan aplikasi
```

### Opsi 3: Gunakan MySQL Standalone

Jika XAMPP terlalu tidak stabil, install MySQL standalone:

1. **Download MySQL Community Server**: https://dev.mysql.com/downloads/mysql/
2. **Install** dengan default settings
3. **Update** `database.py`:
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@127.0.0.1:3306/db_perjanjian"
```

---

## 🔄 Alternatif: Gunakan SQLite (Development Only)

Untuk development yang lebih stabil, gunakan SQLite:

### 1. Update `database.py`:
```python
# Ganti MySQL dengan SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./legaldoc.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Untuk SQLite
    pool_pre_ping=True
)
```

### 2. Update `requirements.txt`:
```
# Tidak perlu pymysql untuk SQLite
# Hapus atau comment: pymysql
```

### 3. Reset Database:
```powershell
# Hapus file database lama (jika ada)
Remove-Item legaldoc.db -ErrorAction SilentlyContinue

# Jalankan reset
python reset_db_full.py
```

**⚠️ Catatan**: SQLite hanya untuk development. Untuk production, tetap gunakan MySQL/PostgreSQL.

---

## 🧪 Test Koneksi Database

Buat file `test_connection.py`:

```python
import pymysql
import time

def test_mysql_connection():
    try:
        print("Testing MySQL connection...")
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='db_perjanjian'
        )
        print("✅ Connection successful!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agreements")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} documents in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test 5 kali dengan interval
    for i in range(5):
        print(f"\n--- Test {i+1}/5 ---")
        test_mysql_connection()
        if i < 4:
            time.sleep(2)
```

Jalankan:
```powershell
python test_connection.py
```

---

## 📊 Monitoring Koneksi

Untuk melihat status koneksi MySQL:

```sql
-- Buka phpMyAdmin atau MySQL client
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';
SHOW VARIABLES LIKE 'max_connections';
```

---

## 🚀 Best Practices

### 1. Selalu Restart MySQL Sebelum Development
```powershell
# Script otomatis (buat file restart_mysql.ps1):
Write-Host "Restarting MySQL..."
# Adjust path sesuai instalasi XAMPP Anda
& "C:\xampp\mysql\bin\mysqladmin.exe" -u root shutdown
Start-Sleep -Seconds 2
& "C:\xampp\mysql_start.bat"
Write-Host "MySQL restarted!"
```

### 2. Monitor Log Errors
Cek file: `C:\xampp\mysql\data\mysql_error.log`

### 3. Gunakan Connection Pooling (Sudah Diterapkan)
File `database.py` sudah menggunakan pooling yang optimal.

---

## 🆘 Jika Masih Bermasalah

### Quick Fix:
```powershell
# 1. Stop semua
# Di terminal aplikasi: Ctrl+C

# 2. Restart MySQL di XAMPP
# Stop → Start

# 3. Jalankan lagi
uvicorn main:app --reload
```

### Permanent Fix:
Pertimbangkan migrasi ke:
- **PostgreSQL** (lebih stabil)
- **MySQL Standalone** (bukan XAMPP)
- **Docker MySQL** (isolated environment)

---

## 📞 Support

Jika masih mengalami masalah, cek:
1. XAMPP version (gunakan versi terbaru)
2. Windows Firewall settings
3. Antivirus yang mungkin block MySQL
4. Port 3306 tidak digunakan aplikasi lain

---

**Update Terakhir**: 17 Februari 2026
