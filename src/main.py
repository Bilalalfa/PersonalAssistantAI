"""
VisionAssist — Entry Point
Jalankan: python src/main.py
"""
import sys
import os

# Pastikan root project ada di path agar import modul berjalan
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.modules.config import Config
from src.ui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("VisionAssist")
    app.setApplicationVersion("1.0.0")

    # Load stylesheet
    qss_path = os.path.join(os.path.dirname(__file__), "ui", "style.qss")
    try:
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("[WARNING] style.qss tidak ditemukan.")

    config = Config()
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
