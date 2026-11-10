"""Stubbed data layer.

STUB: everything lives in Python dictionaries and is lost when the program
closes. The rest of the program only talks to the methods below, so this
class can be replaced by a real database (SQLite in Module 5) without
changing the interface or the business logic.
"""
from itertools import count

from .logic import Attempt, Problem

# STUB: a fixed problem library instead of curator-created Practice Sets.
_PROBLEMS = [
    Problem(1, "7 × 8", 56),
    Problem(2, "9 × 4", 36),
    Problem(3, "12 ÷ 3", 4),
]


class InMemoryStore:
    def __init__(self):
        self._problems = {p.problem_id: p for p in _PROBLEMS}
        self._sessions: dict[int, str] = {}          # session_id -> learner name
        self._attempts: dict[int, list[Attempt]] = {}  # session_id -> attempts
        self._ids = count(1)

    # Problems
    def problem_ids(self) -> list[int]:
        return sorted(self._problems)

    def get_problem(self, problem_id: int) -> Problem:
        return self._problems[problem_id]

    # Sessions
    def start_session(self, learner: str) -> int:
        session_id = next(self._ids)
        self._sessions[session_id] = learner
        self._attempts[session_id] = []
        return session_id

    def learner_for(self, session_id: int) -> str:
        return self._sessions[session_id]

    # Attempts
    def save_attempt(self, session_id: int, attempt: Attempt) -> None:
        self._attempts[session_id].append(attempt)

    def attempts_for(self, session_id: int, problem_id: int) -> list[Attempt]:
        return [a for a in self._attempts[session_id] if a.problem_id == problem_id]

    def session_attempts(self, session_id: int) -> list[Attempt]:
        return list(self._attempts[session_id])
