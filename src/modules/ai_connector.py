"""
ai_connector.py — Koneksi ke Ollama API & QThread worker
Tanggung jawab: AI Integration Developer
"""
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from src.modules.config import Config


class AIConnector:
    """Mengirim pesan ke Ollama dan mendapatkan respons."""

    def __init__(self, config: Config):
        self.base_url = config.OLLAMA_BASE_URL
        self.model    = config.OLLAMA_MODEL

    def is_running(self) -> bool:
        """Cek apakah Ollama server aktif."""
        try:
            r = requests.get(self.base_url, timeout=3)
            return r.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def chat(self, messages: list) -> str:
        """Kirim pesan dan dapatkan respons teks dari AI."""
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Tidak dapat terhubung ke Ollama.\n"
                "Pastikan sudah menjalankan: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama timeout. Coba lagi atau ganti model yang lebih ringan.")


class ChatWorker(QThread):
    """
    QThread — Menjalankan permintaan AI di background.
    Ini KRITIS agar UI tidak freeze saat AI sedang memproses.
    """
    response_ready   = pyqtSignal(str)   # Respons AI siap
    error_occurred   = pyqtSignal(str)   # Terjadi error
    thinking_started = pyqtSignal()      # AI mulai berpikir
    thinking_stopped = pyqtSignal()      # AI selesai berpikir

    def __init__(self, ai: AIConnector, messages: list):
        super().__init__()
        self.ai       = ai
        self.messages = messages

    def run(self):
        self.thinking_started.emit()
        try:
            result = self.ai.chat(self.messages)
            self.response_ready.emit(result)
        except (ConnectionError, TimeoutError) as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"Error tidak terduga: {e}")
        finally:
            self.thinking_stopped.emit()
