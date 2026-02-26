"""
main_window.py — Jendela utama aplikasi VisionAssist
Tanggung jawab: UI/UX & Frontend Developer
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QSplitter, QLabel
)
from PyQt6.QtCore import Qt

from src.modules.config import Config
from src.modules.db_connector import DatabaseConnector
from src.modules.ai_connector import AIConnector
from src.ui.chat_panel import ChatPanel
from src.ui.task_panel import TaskPanel


class MainWindow(QMainWindow):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

        # Inisialisasi koneksi layanan
        self.db = DatabaseConnector(config)
        self.ai = AIConnector(config)

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.setWindowTitle("VisionAssist — AI Assistant & Task Manager")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 780)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top Bar ──────────────────────────────────────────────
        topbar = QWidget()
        topbar.setObjectName("topBar")
        topbar.setFixedHeight(52)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("🤖 VisionAssist")
        title.setObjectName("appName")
        tb_layout.addWidget(title)
        tb_layout.addStretch()

        status_text = "🟢 Ollama Online" if self.ai.is_running() else "🔴 Ollama Offline"
        self.ai_status = QLabel(status_text)
        self.ai_status.setObjectName("statusIndicator")
        tb_layout.addWidget(self.ai_status)

        root.addWidget(topbar)

        # ── Panel Utama (Chat kiri | Tugas kanan) ───────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("mainSplitter")

        self.chat_panel = ChatPanel(self.ai)
        self.task_panel = TaskPanel(self.db)

        splitter.addWidget(self.chat_panel)
        splitter.addWidget(self.task_panel)
        splitter.setSizes([700, 420])   # Rasio 60:40

        root.addWidget(splitter)

    def closeEvent(self, event):
        self.db.disconnect()
        super().closeEvent(event)
