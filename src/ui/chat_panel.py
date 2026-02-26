"""
chat_panel.py — Panel antarmuka chat dengan AI
Tanggung jawab: UI/UX & Frontend Developer
             + AI Integration Developer (koneksi ChatWorker)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt

from src.modules.ai_connector import AIConnector, ChatWorker


class ChatPanel(QWidget):
    def __init__(self, ai: AIConnector):
        super().__init__()
        self.ai           = ai
        self.chat_history = []  # Riwayat percakapan untuk konteks AI
        self._worker      = None

        self._build_ui()

    # ── UI (Frontend Developer) ──────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("💬 Chat AI Assistant")
        header.setObjectName("panelHeader")
        layout.addWidget(header)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setPlaceholderText(
            "Mulai percakapan — tanya apa saja seputar materi kuliah kamu!"
        )
        layout.addWidget(self.chat_display)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setObjectName("chatInput")
        self.input_field.setPlaceholderText("Ketik pertanyaanmu di sini...")
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("Kirim →")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.clicked.connect(self.send_message)

        input_row.addWidget(self.input_field)
        input_row.addWidget(self.send_btn)
        layout.addLayout(input_row)

    # ── Logic (AI Integration Developer) ────────────────────────
    def send_message(self):
        text = self.input_field.text().strip()
        if not text or (self._worker and self._worker.isRunning()):
            return

        self.input_field.clear()
        self._append_bubble("Kamu", text, is_user=True)
        self.chat_history.append({"role": "user", "content": text})

        self._worker = ChatWorker(self.ai, self.chat_history)
        self._worker.response_ready.connect(self._on_response)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.thinking_started.connect(self._on_thinking_start)
        self._worker.thinking_stopped.connect(self._on_thinking_stop)
        self._worker.start()

    def _on_response(self, text: str):
        self.chat_history.append({"role": "assistant", "content": text})
        self._append_bubble("AI", text, is_user=False)

    def _on_error(self, msg: str):
        self._append_bubble("⚠️ Error", msg, is_user=False)

    def _on_thinking_start(self):
        self.status_label.setText("🤔 AI sedang berpikir...")
        self.send_btn.setEnabled(False)

    def _on_thinking_stop(self):
        self.status_label.setText("")
        self.send_btn.setEnabled(True)

    def _append_bubble(self, sender: str, text: str, is_user: bool):
        css = "user-bubble" if is_user else "ai-bubble"
        html = f'<div class="{css}"><b>{sender}:</b><br>{text}</div><br>'
        self.chat_display.append(html)
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())
