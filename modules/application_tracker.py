import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    application_date TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT
);
"""

STATUSES = ["Applied", "Interview", "Rejected", "Offer"]


class ApplicationTracker:
    def __init__(self, db_path: str = "database/applications.db"):
        self.db_path = db_path
        self._create_database()

    def _create_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(DB_SCHEMA)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_application(self, company: str, role: str, application_date: str, status: str, notes: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO applications (company, role, application_date, status, notes) VALUES (?, ?, ?, ?, ?)",
                (company.strip(), role.strip(), application_date.strip(), status.strip(), notes.strip()),
            )
            conn.commit()
            return cursor.lastrowid

    def get_applications(self) -> List[Dict[str, str]]:
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM applications ORDER BY application_date DESC, id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def update_application(self, entry_id: int, company: str, role: str, application_date: str, status: str, notes: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE applications SET company = ?, role = ?, application_date = ?, status = ?, notes = ? WHERE id = ?",
                (company.strip(), role.strip(), application_date.strip(), status.strip(), notes.strip(), entry_id),
            )
            conn.commit()

    def delete_application(self, entry_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM applications WHERE id = ?", (entry_id,))
            conn.commit()

    def summary(self) -> Dict[str, int]:
        apps = self.get_applications()
        return {
            "total": len(apps),
            "applied": sum(1 for app in apps if app["status"] == "Applied"),
            "interview": sum(1 for app in apps if app["status"] == "Interview"),
            "rejected": sum(1 for app in apps if app["status"] == "Rejected"),
            "offer": sum(1 for app in apps if app["status"] == "Offer"),
        }
