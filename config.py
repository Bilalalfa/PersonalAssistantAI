"""
config.py — Membaca konfigurasi dari file .env
Tanggung jawab: AI Integration Developer
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str    = os.getenv("OLLAMA_MODEL", "llama3")

    # MySQL
    DB_HOST: str     = os.getenv("DB_HOST", "localhost")
    DB_PORT: int     = int(os.getenv("DB_PORT", 3306))
    DB_NAME: str     = os.getenv("DB_NAME", "visionassist_db")
    DB_USER: str     = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
