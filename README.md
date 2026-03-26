# Ollama Vision - Personal Assistant AI 🤖📸

**Ollama Vision** adalah aplikasi asisten pribadi modern yang menggabungkan kekuatan *Large Language Model* (LLM) dari Ollama dengan kemampuan *Computer Vision*. Aplikasi ini dibangun menggunakan Python dan PyQt6 untuk antarmuka pengguna yang responsif dan estetis, serta terintegrasi dengan MySQL untuk manajemen tugas.

---

## ✨ Fitur Utama

- **💬 AI Chat Assistant**: Berinteraksi dengan berbagai model LLM lokal melalui Ollama.
- **👁️ Vision Support**: Unggah gambar (PNG, JPG, WEBP) untuk dianalisis oleh model vision AI.
- **📅 Task Manager**: Kelola tugas harian Anda dengan fitur CRUD (Create, Read, Update, Delete).
- **🗓️ Academic Calendar**: Dashboard kalender untuk memantau tenggat waktu (deadline) tugas.
- **🗂️ Chat History**: Simpan dan akses kembali sesi obrolan sebelumnya melalui sidebar.
- **🎨 Modern UI**: Antarmuka gelap (*Dark Mode*) yang elegan dengan desain berbasis kartu dan animasi typing.

---

## 🛠️ Teknologi & Library

Proyek ini dibangun menggunakan teknologi berikut:

- **Bahasa Pemrograman**: [Python 3.10+](https://www.python.org/)
- **Framework UI**: [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- **Integrasi LLM**: [LangChain Ollama](https://python.langchain.com/docs/integrations/llms/ollama/)
- **Local LLM Runner**: [Ollama](https://ollama.com/)
- **Database**: [MySQL](https://www.mysql.com/) (via `mysql-connector-python`)

---

## 🚀 Persiapan & Instalasi

### 1. Prasyarat
Pastikan Anda sudah menginstal:
- **Python**: [Unduh di sini](https://www.python.org/downloads/)
- **Ollama**: [Unduh di sini](https://ollama.com/download)
- **XAMPP / MySQL Server**: Pastikan MySQL berjalan di `localhost:3306`.

### 2. Instalasi Dependensi
Jalankan perintah berikut di terminal Anda:
```bash
pip install pyqt6 langchain_ollama mysql-connector-python
```

### 3. Konfigurasi Database
Aplikasi akan secara otomatis mencoba membuat database `ollama_assistant` dan tabel `tasks` saat pertama kali dijalankan. Namun, pastikan MySQL Anda aktif dengan akun `root` tanpa password (default XAMPP).

### 4. Menjalankan Aplikasi
```bash
python app.py
```

---

## 📁 Struktur Proyek

```text
PersonalAssistantAI/
├── app.py              # Logika utama aplikasi & antarmuka PyQt6
├── style.py           # Konfigurasi CSS/QSS dan tema warna
├── requirements.txt   # Daftar dependensi library
└── README.md          # Dokumentasi proyek
```

---

## 📋 Fitur Task Manager
- **Add Task**: Tambahkan tugas baru dengan memilih tanggal di kalender sebagai deadline.
- **Mark Completed**: Tandai tugas yang sudah selesai dengan status hijau.
- **Delete Task**: Hapus tugas yang sudah tidak diperlukan.
- **Filter**: Klik tanggal pada kalender untuk melihat tugas spesifik pada hari tersebut.

---

## 📝 Catatan Penggunaan
- Pastikan servis **Ollama** sedang berjalan di latar belakang agar fitur AI dapat berfungsi.
- Gunakan model seperti `llava` atau `moondream` untuk fitur analisis gambar (Vision).

---

Developed for **Gorsel Programlama II** - Semester 6.
