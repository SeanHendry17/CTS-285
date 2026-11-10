"""Business logic for the Answer Flow slice.

This module owns the two-attempt rule. It knows nothing about Flask, HTML,
or SQLite. Routes ask it what happened; they never decide it themselves.
(Module 4 decision: "Reusable business logic service" +
"Business logic returns outcome/state; UI renders it".)
"""
from dataclasses import dataclass

MAX_TRIES = 2


@dataclass(frozen=True)
class Problem:
    id: int
    prompt: str
    answer: int


@dataclass(frozen=True)
class Attempt:
    problem_id: int
    try_number: int
    submitted: int
    correct: bool


@dataclass(frozen=True)
class Outcome:
    """What the interface should show for one problem right now."""
    status: str            # "open", "correct", or "revealed"
    next_try: int | None   # which try the learner is on, None once resolved
    reveal_answer: int | None
    message: str


# Problem library for this slice (kept tiny on purpose).
PROBLEMS = {
    1: Problem(1, "7 × 8", 56),
    2: Problem(2, "9 × 4", 36),
    3: Problem(3, "12 ÷ 3", 4),
}


def get_problem(problem_id: int) -> Problem | None:
    return PROBLEMS.get(problem_id)


def next_problem_id(problem_id: int) -> int | None:
    ids = sorted(PROBLEMS)
    i = ids.index(problem_id)
    return ids[i + 1] if i + 1 < len(ids) else None


def outcome_for(problem: Problem, attempts: list[Attempt]) -> Outcome:
    """Work out the current state from the stored attempts alone."""
    if any(a.correct for a in attempts):
        return Outcome("correct", None, None, "Correct!")
    if len(attempts) >= MAX_TRIES:
        return Outcome("revealed", None, problem.answer,
                       f"Out of tries. The answer is {problem.answer}.")
    if attempts:
        return Outcome("open", len(attempts) + 1, None, "Not quite. Try again.")
    return Outcome("open", 1, None, "Enter answer.")


class ProblemAlreadyResolved(Exception):
    """Raised when an answer arrives for a problem that is already finished."""


def evaluate(problem: Problem, attempts: list[Attempt], submitted: int) -> Attempt:
    """Apply the two-attempt rule to a new answer and return the Attempt to save.

    The try number comes from the stored attempts, never from the request.
    """
    if outcome_for(problem, attempts).status != "open":
        raise ProblemAlreadyResolved(problem.id)
    return Attempt(
        problem_id=problem.id,
        try_number=len(attempts) + 1,
        submitted=submitted,
        correct=(submitted == problem.answer),
    )
