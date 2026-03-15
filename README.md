# 🤖 Ollama + Streamlit Chatbot (Local AI Chatbot)

Demo Chatbot lokal menggunakan [Ollama](https://ollama.com/) dan [Streamlit](https://streamlit.io/).

---

## 🚀 **Fitur**

✅ Chatbot AI lokal (no API Key, no internet untuk inference)  
✅ UI interaktif dengan Streamlit  
✅ Pilih model langsung dari Ollama  
✅ Bisa dijalankan di Windows, Mac, dan Linux

---

## 🔧 **Cara Menjalankan**

### 1. **Install Ollama**

- Download dan install Ollama sesuai OS kamu dari [https://ollama.com/download](https://ollama.com/download).

### 2. **Pull Model AI**

Contoh pull model TinyLLaMA 1.1B:

```bash
ollama pull tinyllama:1.1b
```

💡 Kamu juga bisa menggunakan model lain seperti llama3:8b atau mistral:7b sesuai kebutuhan dan spesifikasi laptop.

### 3. **Clone Repository**

```bash
git clone https://github.com/username/ollama-streamlit-chatbot.git
cd ollama-streamlit-chatbot
```

### 4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 5. **Jalankan Chatbot**

```bash
streamlit run app.py
```

---

### 📝 Struktur Project

```bash
ollama-streamlit-chatbot/
├── app.py
├── requirements.txt
└── README.md
```

- app.py : Script utama Streamlit + Ollama
- requirements.txt : Daftar dependencies Python

---

### 💻 Contoh Penggunaan

1. Jalankan server chatbot dengan

```bash
streamlit run app.py
```

2. Pilih model AI di sidebar
3. Tanyakan apa saja sesuai konteks model yang digunakan

---

### 🤝 Lisensi

MIT License.
