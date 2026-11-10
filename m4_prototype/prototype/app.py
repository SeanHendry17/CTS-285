"""Text interface layer: reads input and prints output only.

It never decides whether an answer is right, which try it is, or when to
reveal. It asks dataman.logic and displays the Feedback it gets back.

Run:  python app.py
"""
from dataman import logic
from dataman.store import InMemoryStore


def ask_number(prompt: str, input_fn=input) -> int:
    """Keep asking until the learner types a whole number.
    Invalid input is NOT counted as an attempt (see README, Revision 2)."""
    while True:
        raw = input_fn(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number. (This did not use a try.)")


def run_problem(store, session_id, problem_id, input_fn=input):
    problem = store.get_problem(problem_id)
    print(f"\nProblem: {problem.prompt}")
    while True:
        attempts = store.attempts_for(session_id, problem_id)
        if logic.is_finished(attempts):
            return
        try_no = logic.next_try_number(attempts)
        print(f"Try {try_no} of {logic.MAX_TRIES}")
        submitted = ask_number("Your answer: ", input_fn)
        attempt, feedback = logic.check_answer(problem, attempts, submitted)
        store.save_attempt(session_id, attempt)
        print(feedback.message)


def show_summary(store, session_id):
    attempts = store.session_attempts(session_id)
    print(f"\n--- Results for {store.learner_for(session_id)} ---")
    for a in attempts:
        p = store.get_problem(a.problem_id)
        mark = "correct" if a.correct else "wrong"
        print(f"{p.prompt:<8} try {a.try_number}: {a.submitted_answer:<4} {mark}")
    missed = logic.missed_problems(attempts)
    names = ", ".join(store.get_problem(i).prompt for i in missed) or "none"
    print(f"Problems missed at least once: {names}")


def main(input_fn=input, store=None):
    store = store or InMemoryStore()
    print("DataMan – Check an Answer")
    learner = input_fn("Your name: ").strip() or "Learner"
    session_id = store.start_session(learner)
    for problem_id in store.problem_ids():
        run_problem(store, session_id, problem_id, input_fn)
    show_summary(store, session_id)
    return store, session_id


if __name__ == "__main__":
    main()
