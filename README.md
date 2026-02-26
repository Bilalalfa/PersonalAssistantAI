# 🤖 PersonalAssistantAI: Sistem Asisten Pribadi Berbasis AI Lokal & Manajemen Tugas

VisionAssist adalah aplikasi desktop berbasis Python yang dirancang untuk membantu mahasiswa mengelola aktivitas harian dan kebutuhan akademik secara mandiri. Proyek ini merupakan implementasi dari mata kuliah **Görsel Programlama** (Pemrograman Visual).

## 🌟 Fitur Utama
- **Local AI Chatbot**: Asisten cerdas untuk tanya jawab materi perkuliahan secara offline menggunakan **Ollama** (menjaga privasi data).
- **Task Management**: Sistem pencatatan tugas kuliah dan proyek kompetisi terintegrasi dengan database **MySQL**.
- **Modern UI**: Antarmuka desktop yang responsif dan estetis menggunakan **PyQt6**.
- **Smooth Performance**: Implementasi *asynchronous programming* (QThread) agar aplikasi tidak membeku saat AI memproses data.

---

## 👥 Anggota Tim & Tanggung Jawab

| Nama | Peran | Fokus Utama |
| :--- | :--- | :--- |
| **Bilal** | UI/UX & Frontend | Desain Figma, Implementasi PyQt6, & QSS Styling |
| **Asyraf** | Backend & Database | Arsitektur MySQL & Logika CRUD Tugas |
| **Afif** | AI Integration | Koneksi Ollama API & Multithreading (QThread) |

### Detail Tugas:
* **Bilal (@bilalalfa_)**: Merancang antarmuka di Figma, mengubah desain menjadi kode PyQt6, dan memastikan pengalaman pengguna (UX) yang mulus dan modern.
* **Asyraf**: Merancang skema database tugas, memastikan konektivitas Python ke MySQL, dan menangani penyimpanan data jangka panjang.
* **Afif**: Menghubungkan aplikasi ke AI engine (Ollama), mengelola logika pengiriman pesan, dan memastikan UI tetap responsif dengan multithreading.

---

## 🛠️ Teknologi & Peralatan
* **Bahasa Pemrograman**: Python 3.12+
* **GUI Framework**: PyQt6
* **AI Engine**: Ollama (Llama 3 / Mistral)
* **Database**: MySQL
* **Library Utama**: `mysql-connector-python`, `requests`, `PyQt6`

---

## 📅 Jadwal Pengembangan (8 Minggu)
1.  **Minggu 1**: Analisis kebutuhan & Desain UI/UX di Figma.
2.  **Minggu 2**: Setup lingkungan kerja (Python, PyQt6, MySQL, Ollama).
3.  **Minggu 3**: Perancangan database dan tabel tugas di MySQL.
4.  **Minggu 4**: Pembuatan kerangka utama antarmuka (Main Window) PyQt6.
5.  **Minggu 5**: Integrasi koneksi API Ollama ke dalam modul Chat.
6.  **Minggu 6**: Implementasi fungsi CRUD (Tambah/Hapus Tugas) pada UI.
7.  **Minggu 7**: Optimasi sistem menggunakan QThread & styling akhir (QSS).
8.  **Minggu 8**: Pengujian akhir, perbaikan bug, dan dokumentasi.

---

## 🚀 Cara Menjalankan Proyek

1.  **Clone Repositori**:
    ```bash
    https://github.com/Bilalalfa/PersonalAssistantAI.git
    cd PersonalAssistantAI
    ```

2.  **Instal Dependensi**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Database**:
    * Pastikan MySQL berjalan.
    * Impor file `database/schema.sql` (jika tersedia) ke dalam MySQL Anda.

4.  **Jalankan AI**:
    * Pastikan Ollama sudah terinstal dan berjalan.
    * Unduh model: `ollama run llama3`

5.  **Jalankan Aplikasi**:
    ```bash
    python src/main.py
    ```

---
© 2026 VisionAssist Team - Computer Science Project
