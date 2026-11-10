"""Data/state boundary for the Answer Flow slice.

Everything that must survive a reload or a new request goes through here and
into SQLite. Nothing is kept in Flask globals or only in the browser.
(Module 4 decisions: "Separate Attempt records with try_number" +
"Attempts/result state through a data boundary".)
"""
import sqlite3

from .logic import Attempt

SCHEMA = """
CREATE TABLE IF NOT EXISTS practice_session (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    learner TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS attempt (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES practice_session(id),
    problem_id  INTEGER NOT NULL,
    try_number  INTEGER NOT NULL,
    submitted   INTEGER NOT NULL,
    correct     INTEGER NOT NULL,
    UNIQUE (session_id, problem_id, try_number)
);
"""


class AttemptStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def start_session(self, learner: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO practice_session (learner) VALUES (?)", (learner,))
            return cur.lastrowid

    def get_learner(self, session_id: int) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT learner FROM practice_session WHERE id = ?",
                (session_id,)).fetchone()
        return row[0] if row else None

    def attempts_for(self, session_id: int, problem_id: int) -> list[Attempt]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT problem_id, try_number, submitted, correct FROM attempt "
                "WHERE session_id = ? AND problem_id = ? ORDER BY try_number",
                (session_id, problem_id)).fetchall()
        return [Attempt(p, t, s, bool(c)) for p, t, s, c in rows]

    def all_attempts(self, session_id: int) -> list[Attempt]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT problem_id, try_number, submitted, correct FROM attempt "
                "WHERE session_id = ? ORDER BY problem_id, try_number",
                (session_id,)).fetchall()
        return [Attempt(p, t, s, bool(c)) for p, t, s, c in rows]

    def save_attempt(self, session_id: int, attempt: Attempt) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO attempt (session_id, problem_id, try_number, submitted, correct) "
                "VALUES (?, ?, ?, ?, ?)",
                (session_id, attempt.problem_id, attempt.try_number,
                 attempt.submitted, int(attempt.correct)))
