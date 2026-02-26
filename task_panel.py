"""
task_panel.py — Panel daftar dan manajemen tugas kuliah
Tanggung jawab: UI/UX & Frontend Developer
             + Backend Developer (koneksi ke DatabaseConnector)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QDialog, QLineEdit, QDateEdit, QComboBox,
    QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate

from src.modules.db_connector import DatabaseConnector
from src.modules.helpers import format_deadline, priority_icon, status_icon


class TaskPanel(QWidget):
    def __init__(self, db: DatabaseConnector):
        super().__init__()
        self.db = db
        self._build_ui()
        self.refresh()

    # ── UI (Frontend Developer) ──────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_row = QHBoxLayout()
        header = QLabel("📋 Daftar Tugas")
        header.setObjectName("panelHeader")
        add_btn = QPushButton("＋ Tambah")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self._open_add_dialog)
        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Daftar tugas
        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        layout.addWidget(self.task_list)

        # Tombol aksi
        btn_row = QHBoxLayout()
        self.done_btn = QPushButton("✅ Selesai")
        self.done_btn.setObjectName("doneButton")
        self.done_btn.clicked.connect(self._mark_done)

        self.delete_btn = QPushButton("🗑️ Hapus")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.clicked.connect(self._delete_task)

        btn_row.addWidget(self.done_btn)
        btn_row.addWidget(self.delete_btn)
        layout.addLayout(btn_row)

    # ── Logic (Backend + Frontend Developer) ────────────────────
    def refresh(self):
        self.task_list.clear()
        for task in self.db.get_all_tasks():
            s_icon = status_icon(task["status"])
            p_icon = priority_icon(task["priority"])
            dl     = format_deadline(task["deadline"])
            label  = f"{s_icon} {p_icon}  {task['title']}\n      📅 {dl}"
            item   = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, task["id"])
            self.task_list.addItem(item)

    def _selected_id(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Pilih Tugas", "Pilih tugas terlebih dahulu.")
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _mark_done(self):
        tid = self._selected_id()
        if tid:
            self.db.update_task_status(tid, "done")
            self.refresh()

    def _delete_task(self):
        tid = self._selected_id()
        if tid:
            ok = QMessageBox.question(
                self, "Konfirmasi Hapus", "Yakin ingin menghapus tugas ini?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if ok == QMessageBox.StandardButton.Yes:
                self.db.delete_task(tid)
                self.refresh()

    def _open_add_dialog(self):
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.db.add_task(**dialog.get_data())
            self.refresh()


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Tugas Baru")
        self.setMinimumWidth(360)
        self._build_ui()

    def _build_ui(self):
        layout = QFormLayout(self)

        self.title_input    = QLineEdit()
        self.title_input.setPlaceholderText("Contoh: Tugas Algoritma Bab 3")

        self.desc_input     = QLineEdit()
        self.desc_input.setPlaceholderText("Deskripsi singkat (opsional)")

        self.deadline_input = QDateEdit(QDate.currentDate())
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("dd MMMM yyyy")

        self.priority_input = QComboBox()
        self.priority_input.addItems(["low", "medium", "high"])
        self.priority_input.setCurrentText("medium")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Contoh: Kuliah, Kompetisi")

        layout.addRow("Judul Tugas *", self.title_input)
        layout.addRow("Deskripsi",     self.desc_input)
        layout.addRow("Deadline",      self.deadline_input)
        layout.addRow("Prioritas",     self.priority_input)
        layout.addRow("Kategori",      self.category_input)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._validate)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def _validate(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Validasi", "Judul tugas tidak boleh kosong!")
            return
        self.accept()

    def get_data(self) -> dict:
        d = self.deadline_input.date()
        return {
            "title":       self.title_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "deadline":    f"{d.year()}-{d.month():02d}-{d.day():02d}",
            "priority":    self.priority_input.currentText(),
            "category":    self.category_input.text().strip(),
        }
