📜 Agreement Management System (AMS)

Sistem manajemen dokumen perjanjian dengan fitur Hashing SHA-256 untuk integritas data dan QR Code untuk verifikasi instan.
🚀 Fitur Utama

    Registrasi Perjanjian: Simpan judul, ringkasan isi, dan daftar penandatangan.

    Digital Fingerprint: Otomatis membuat hash unik (SHA-256) untuk setiap file yang diunggah.

    QR Code Generator: Membuat QR code unik yang merujuk pada hash dokumen.

    Storage Management: Menyimpan file fisik secara terorganisir.

    Local MySQL Integration: Menggunakan database relasional untuk persistensi data.

🏗️ Arsitektur Blueprint

Sistem ini bekerja dengan memisahkan antara metadata (di MySQL) dan file fisik (di Folder Storage).
Struktur Folder
Plaintext

/ams-project
├── main.py              # Entry point FastAPI & Endpoints
├── database.py          # Konfigurasi koneksi MySQL (SQLAlchemy)
├── models.py            # Skema tabel database
├── utils.py             # Fungsi logika (Hashing & QR Generator)
├── static/
│   ├── docs/            # Folder penyimpanan file PDF asli
│   └── qr/              # Folder penyimpanan file gambar QR
└── requirements.txt     # Daftar library yang dibutuhkan

🛠️ Persiapan Instalasi
1. Prasyarat

    Python 3.8+

    XAMPP / Laragon (untuk MySQL)

    Browser (untuk akses Swagger UI)

2. Instalasi Library

Jalankan perintah berikut di terminal Anda:
Bash

pip install fastapi uvicorn sqlalchemy pymysql python-multipart hashlib qrcode[pil]

📋 Skema Data (MySQL)

Tabel agreements dirancang untuk menampung detail kontrak secara lengkap:
Kolom	Tipe Data	Deskripsi
id	Integer (PK)	Auto-increment ID
title	Varchar(255)	Judul dokumen/perjanjian
content_summary	Text	Ringkasan singkat isi kontrak
signers	Text	Nama-nama penandatangan
document_hash	Varchar(64)	Hash SHA-256 (Unique)
file_path	Varchar(255)	Lokasi file PDF di server
qr_code_path	Varchar(255)	Lokasi file gambar QR
created_at	Datetime	Stempel waktu pendaftaran
🛠️ Cara Menjalankan

    Nyalakan MySQL: Pastikan MySQL di XAMPP/Laragon dalam status Started.

    Buat Database: Buat database bernama db_perjanjian.

    Running App:
    Bash

    uvicorn main:app --reload

    Akses Web Dashboard: Buka http://127.0.0.1:8000/ untuk menggunakan antarmuka grafis.
    
    Akses Dokumentasi API: Buka http://127.0.0.1:8000/docs jika ingin melihat detail endpoint.

🛡️ Keamanan & Integritas

Sistem ini memastikan bahwa jika file PDF diubah sedikit saja (bahkan satu spasi), maka Hash yang dihasilkan saat verifikasi tidak akan cocok dengan yang ada di database. Ini menjamin keaslian dokumen perjanjian Anda.

    Note: Jangan lupa untuk menambahkan file .gitignore agar folder static/docs tidak ikut terunggah ke repositori publik jika berisi dokumen sensitif.