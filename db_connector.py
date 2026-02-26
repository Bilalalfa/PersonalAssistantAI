"""
db_connector.py — Koneksi & operasi CRUD ke MySQL
Tanggung jawab: Backend & Database Developer
"""
import mysql.connector
from mysql.connector import Error
from src.modules.config import Config


class DatabaseConnector:
    def __init__(self, config: Config):
        self.config = config
        self._conn = None

    # ── Koneksi ──────────────────────────────────────────────────
    def connect(self):
        try:
            self._conn = mysql.connector.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
            )
            print("[DB] Koneksi berhasil.")
        except Error as e:
            print(f"[DB] Koneksi gagal: {e}")
            raise

    def disconnect(self):
        if self._conn and self._conn.is_connected():
            self._conn.close()

    def _get_conn(self):
        if not self._conn or not self._conn.is_connected():
            self.connect()
        return self._conn

    # ── CREATE ───────────────────────────────────────────────────
    def add_task(self, title: str, description: str = "",
                 deadline: str = None, priority: str = "medium",
                 category: str = "") -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        sql = """INSERT INTO tasks (title, description, deadline, priority, category)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (title, description, deadline, priority, category))
        conn.commit()
        return cursor.lastrowid

    # ── READ ─────────────────────────────────────────────────────
    def get_all_tasks(self) -> list:
        conn = self._get_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM tasks
            ORDER BY
                CASE status WHEN 'done' THEN 1 ELSE 0 END,
                deadline ASC
        """)
        return cursor.fetchall()

    # ── UPDATE ───────────────────────────────────────────────────
    def update_task_status(self, task_id: int, status: str):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = %s WHERE id = %s", (status, task_id)
        )
        conn.commit()

    # ── DELETE ───────────────────────────────────────────────────
    def delete_task(self, task_id: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
