"""
helpers.py — Fungsi pembantu yang dipakai di seluruh aplikasi
Tanggung jawab: Backend & Database Developer
"""
from datetime import date, datetime


def format_deadline(deadline) -> str:
    """Ubah objek date/string menjadi format tampilan yang mudah dibaca."""
    if deadline is None:
        return "Tidak ada deadline"
    if isinstance(deadline, str):
        try:
            deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
        except ValueError:
            return deadline

    today     = date.today()
    delta     = (deadline - today).days

    formatted = deadline.strftime("%d %b %Y")

    if delta < 0:
        return f"{formatted}  ⚠️ Terlambat {abs(delta)} hari"
    elif delta == 0:
        return f"{formatted}  🔥 Hari ini!"
    elif delta <= 3:
        return f"{formatted}  ⏰ {delta} hari lagi"
    else:
        return f"{formatted}  ({delta} hari lagi)"


def priority_icon(priority: str) -> str:
    """Mengembalikan ikon berdasarkan level prioritas."""
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")


def status_icon(status: str) -> str:
    """Mengembalikan ikon berdasarkan status tugas."""
    return {"done": "✅", "in_progress": "🔄", "pending": "🔵"}.get(status, "⚪")
