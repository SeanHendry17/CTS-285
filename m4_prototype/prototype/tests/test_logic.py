"""Acceptance-criteria checks for the business logic, with no interface.

Run from the prototype folder:  python -m unittest -v
"""
import unittest

from dataman import logic
from dataman.logic import Attempt

P = logic.Problem(1, "7 × 8", 56)


class TwoTryRule(unittest.TestCase):
    def test_ac1_correct_first_try(self):
        a, fb = logic.check_answer(P, [], 56)
        self.assertEqual((a.try_number, a.correct, fb.status), (1, True, "correct"))

    def test_ac2_wrong_first_try_shows_EEE_and_allows_retry(self):
        a, fb = logic.check_answer(P, [], 54)
        self.assertEqual(fb.status, "retry")
        self.assertIn("EEE", fb.message)
        self.assertIsNone(fb.reveal_answer)          # answer stays hidden

    def test_ac3_wrong_twice_shows_EEE_then_reveals(self):
        first, _ = logic.check_answer(P, [], 1)
        second, fb = logic.check_answer(P, [first], 2)
        self.assertEqual((second.try_number, fb.status, fb.reveal_answer), (2, "revealed", 56))
        self.assertIn("EEE", fb.message)

    def test_ac4_each_try_is_kept_for_reporting(self):
        first, _ = logic.check_answer(P, [], 54)
        second, _ = logic.check_answer(P, [first], 56)
        self.assertEqual([(a.try_number, a.correct) for a in (first, second)],
                         [(1, False), (2, True)])
        self.assertEqual(logic.missed_problems([first, second]), [1])

    def test_no_third_try(self):
        done = [Attempt(1, 1, 1, False), Attempt(1, 2, 2, False)]
        with self.assertRaises(logic.ProblemAlreadyFinished):
            logic.check_answer(P, done, 56)


if __name__ == "__main__":
    unittest.main()
