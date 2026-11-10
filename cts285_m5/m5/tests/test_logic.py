"""Unit tests for the two-attempt rule (no Flask involved)."""
import pytest

from answer_flow import logic
from answer_flow.logic import Attempt

P = logic.PROBLEMS[1]  # 7 x 8 = 56


def test_correct_first_try():
    a = logic.evaluate(P, [], 56)
    assert a.try_number == 1 and a.correct
    assert logic.outcome_for(P, [a]).status == "correct"


def test_wrong_then_correct_keeps_both_attempts():
    first = logic.evaluate(P, [], 54)
    second = logic.evaluate(P, [first], 56)
    assert (first.try_number, first.correct) == (1, False)
    assert (second.try_number, second.correct) == (2, True)
    assert logic.outcome_for(P, [first, second]).status == "correct"


def test_wrong_wrong_reveals_answer():
    first = logic.evaluate(P, [], 1)
    second = logic.evaluate(P, [first], 2)
    out = logic.outcome_for(P, [first, second])
    assert out.status == "revealed" and out.reveal_answer == 56


def test_answer_hidden_while_open():
    first = logic.evaluate(P, [], 1)
    out = logic.outcome_for(P, [first])
    assert out.status == "open" and out.next_try == 2 and out.reveal_answer is None


def test_no_third_attempt():
    done = [Attempt(1, 1, 1, False), Attempt(1, 2, 2, False)]
    with pytest.raises(logic.ProblemAlreadyResolved):
        logic.evaluate(P, done, 56)
