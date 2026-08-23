import sqlite3
from datetime import datetime, timezone
from app.config import settings

def init_db():
    with sqlite3.connect(settings.sqlite_path) as con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS questions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "question TEXT NOT NULL,"
            "answer TEXT NOT NULL,"
            "route TEXT NOT NULL,"
            "created_at TEXT NOT NULL)"
        )

def save_question(question: str, answer: str, route: str):
    with sqlite3.connect(settings.sqlite_path) as con:
        con.execute(
            "INSERT INTO questions(question, answer, route, created_at) VALUES (?, ?, ?, ?)",
            (question, answer, route, datetime.now(timezone.utc).isoformat()),
        )

def list_questions(limit: int = 100, offset: int = 0):
    with sqlite3.connect(settings.sqlite_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM questions ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    return [dict(r) for r in rows], total
