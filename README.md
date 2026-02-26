# 🤖 VisionAssist

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_AI-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Aplikasi desktop asisten AI lokal & manajemen tugas untuk mahasiswa.**  
Privasi terjaga · Berjalan 100% offline · Tanpa biaya berlangganan.

</div>

---

## 📋 Tentang Proyek

**VisionAssist** adalah aplikasi desktop yang menggabungkan dua fitur utama:

1. **💬 Chat AI Offline** — Tanya jawab materi kuliah menggunakan model AI lokal via [Ollama](https://ollama.ai). Tidak ada data yang dikirim ke server luar.
2. **✅ Manajemen Tugas** — Catat, pantau, dan kelola tenggat waktu tugas kuliah yang tersimpan di database MySQL lokal.

---

## 👥 Tim Pengembang

| Nama | Peran | File yang Dikerjakan |
|------|-------|----------------------|
| [Nama 1] | UI/UX & Frontend Developer | `src/ui/` |
| [Nama 2] | Backend & Database Developer | `src/modules/db_connector.py`, `database/` |
| [Nama 3] | AI Integration Developer | `src/modules/ai_connector.py`, `src/modules/config.py` |

---

## 🛠️ Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Bahasa | Python 3.12+ |
| GUI | PyQt6 |
| AI Engine | Ollama (Local LLM) |
| Database | MySQL 8.0+ |
| DB Connector | mysql-connector-python |
| HTTP | requests |
| Config | python-dotenv |

---

## 🚀 Instalasi & Cara Menjalankan

### Prasyarat

Pastikan sudah terinstall:
- [Python 3.12+](https://www.python.org/downloads/)
- [MySQL 8.0+](https://dev.mysql.com/downloads/mysql/)
- [Ollama](https://ollama.ai/download)

---

### 1 — Clone Repository

```bash
https://github.com/Bilalalfa/PersonalAssistantAI.git
cd PersonalAssistantAI
```

### 2 — Buat Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 — Setup Database MySQL

```bash
mysql -u root -p < database/setup.sql
```

### 5 — Konfigurasi Environment

```bash
cp .env.example .env
# Buka .env dan isi password MySQL serta model Ollama yang dipakai
```

### 6 — Download & Jalankan Ollama

```bash
# Download model AI (hanya sekali, ukuran ~4GB)
ollama pull llama3

# Jalankan server Ollama (biarkan terminal ini terbuka)
ollama serve
```

### 7 — Jalankan Aplikasi

```bash
python src/main.py
```

---

## 📁 Struktur Proyek

```
VisionAssist/
│
├── assets/                    # Gambar, logo, dan tangkapan layar UI
│
├── database/
│   └── setup.sql              # Script SQL — jalankan sekali untuk setup tabel
│
├── docs/                      # Dokumentasi tambahan, desain Figma, manual user
│
├── src/                       # Kode sumber utama
│   │
│   ├── ui/                    # Tampilan antarmuka (Frontend Developer)
│   │   ├── main_window.py     # Jendela utama — menyatukan semua panel
│   │   ├── chat_panel.py      # Panel chat dengan AI
│   │   ├── task_panel.py      # Panel daftar tugas + dialog tambah
│   │   └── style.qss          # Stylesheet dark mode (Catppuccin Mocha)
│   │
│   ├── modules/               # Logika inti aplikasi
│   │   ├── config.py          # Pembaca konfigurasi .env (AI Developer)
│   │   ├── db_connector.py    # Koneksi & CRUD MySQL (Database Developer)
│   │   ├── ai_connector.py    # Koneksi Ollama + QThread worker (AI Developer)
│   │   └── helpers.py         # Fungsi pembantu (format tanggal, ikon, dll)
│   │
│   └── main.py                # ▶ Entry point — jalankan file ini
│
├── .env.example               # Template konfigurasi (aman di-commit)
├── .gitignore                 # Mengabaikan .env, venv, __pycache__
├── README.md                  # Dokumentasi utama proyek
└── requirements.txt           # Daftar library Python yang dibutuhkan
```

---

## 🌿 Alur Kerja Git (Kolaborasi Tim)

```
main
├── feature/ui          → UI/UX & Frontend Developer
├── feature/database    → Backend & Database Developer
└── feature/ai          → AI Integration Developer
```

### Perintah dasar

```bash
# Buat branch baru
git checkout -b feature/nama-fitur

# Simpan perubahan
git add .
git commit -m "feat: deskripsi perubahan"

# Push ke GitHub
git push origin feature/nama-fitur
```

### Konvensi commit

| Prefix | Digunakan untuk |
|--------|----------------|
| `feat:` | Fitur baru |
| `fix:` | Perbaikan bug |
| `style:` | Perubahan UI/QSS |
| `refactor:` | Refactoring kode |
| `docs:` | Pembaruan dokumentasi |

---

## 📅 Jadwal Pengembangan

| Minggu | Tahap | Output | Status |
|--------|-------|--------|--------|
| 1 | Analisis & Desain | Prototipe Figma | ✅ |
| 2 | Setup Lingkungan | Environment Siap | ✅ |
| 3 | Arsitektur Database | Koneksi DB Berhasil | 🔄 |
| 4 | Dasar GUI | Kerangka Antarmuka | ⏳ |
| 5 | Inti AI | Mesin Chat Berfungsi | ⏳ |
| 6 | Manajemen Tugas | Panel Tugas Berfungsi | ⏳ |
| 7 | Optimasi Sistem | Prototipe Stabil | ⏳ |
| 8 | Uji Coba & Final | Proyek Selesai | ⏳ |

---

## ❓ Troubleshooting

**🔴 Indikator "Ollama Offline"?**
```bash
ollama serve          # Jalankan dulu di terminal terpisah
# Cek: http://localhost:11434
```

**🔴 Koneksi MySQL gagal?**
```bash
# Windows:  net start mysql
# Linux:    sudo systemctl start mysql
# Pastikan isi .env sudah benar
```

**🔴 ModuleNotFoundError saat menjalankan?**
```bash
# Aktifkan virtual environment dulu!
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

---

## 📄 Lisensi

[MIT License](LICENSE) — bebas digunakan dan dimodifikasi.

---

<div align="center">
Dibuat dengan ❤️ sebagai proyek mata kuliah<br>
<sub>Python · PyQt6 · Ollama · MySQL</sub>
</div>
