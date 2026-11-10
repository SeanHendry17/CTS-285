"""Business logic layer.

Owns the two-try rule and the reveal gate. It does not print, read input,
or know where data is stored, so the same functions can be reused by Flask
in Module 5.

Event sequence (from Design Studio Round 2B):
  1. Display problem
  2. Accept submitted answer
  3. Decide whether answer is correct
  4. Record try number
  5. If wrong and try 1: show EEE and allow retry
  6. If wrong and try 2: show EEE, then reveal
"""
from dataclasses import dataclass

MAX_TRIES = 2
ERROR_SYMBOL = "EEE"


@dataclass(frozen=True)
class Problem:
    problem_id: int
    prompt: str
    answer: int


@dataclass(frozen=True)
class Attempt:
    problem_id: int
    try_number: int
    submitted_answer: int
    correct: bool


@dataclass(frozen=True)
class Feedback:
    """What happened, in a form any interface can display."""
    status: str               # "correct", "retry", or "revealed"
    try_number: int
    message: str
    reveal_answer: int | None = None


class ProblemAlreadyFinished(Exception):
    """An answer arrived for a problem that is already correct or revealed."""


def is_finished(attempts: list[Attempt]) -> bool:
    return any(a.correct for a in attempts) or len(attempts) >= MAX_TRIES


def next_try_number(attempts: list[Attempt]) -> int:
    """The try number comes from saved attempts, never from the screen."""
    return len(attempts) + 1


def check_answer(problem: Problem, prior_attempts: list[Attempt],
                 submitted: int) -> tuple[Attempt, Feedback]:
    """Apply the two-try rule. Returns the Attempt to save and the Feedback to show."""
    if is_finished(prior_attempts):
        raise ProblemAlreadyFinished(problem.problem_id)

    try_number = next_try_number(prior_attempts)
    correct = submitted == problem.answer
    attempt = Attempt(problem.problem_id, try_number, submitted, correct)

    if correct:
        fb = Feedback("correct", try_number, "Correct!")
    elif try_number < MAX_TRIES:
        fb = Feedback("retry", try_number, f"{ERROR_SYMBOL} · Not quite. Try again.")
    else:
        fb = Feedback("revealed", try_number,
                      f"{ERROR_SYMBOL} · Out of tries. The answer is {problem.answer}.",
                      reveal_answer=problem.answer)
    return attempt, fb


def missed_problems(attempts: list[Attempt]) -> list[int]:
    """Problem IDs with at least one wrong try (for later curator retrieval)."""
    return sorted({a.problem_id for a in attempts if not a.correct})
