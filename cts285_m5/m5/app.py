"""Flask entry point for the Module 5 Answer Flow slice.

Routes only translate HTTP <-> business logic. They do not decide whether an
answer is right, which try it is, or when to reveal the answer.

Run:  flask --app app run --debug
"""
import os

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from answer_flow import logic
from answer_flow.store import AttemptStore


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only")
    if db_path is None:
        os.makedirs(app.instance_path, exist_ok=True)
        db_path = os.path.join(app.instance_path, "dataman.db")
    store = AttemptStore(db_path)
    app.extensions["attempt_store"] = store

    @app.get("/")
    def start():
        return render_template("start.html")

    @app.post("/sessions")
    def create_session():
        learner = request.form.get("learner", "").strip() or "Learner"
        session_id = store.start_session(learner)
        first = min(logic.PROBLEMS)
        return redirect(url_for("show_problem", session_id=session_id, problem_id=first))

    def load(session_id: int, problem_id: int):
        problem = logic.get_problem(problem_id)
        learner = store.get_learner(session_id)
        if problem is None or learner is None:
            abort(404)
        return problem, learner

    @app.get("/sessions/<int:session_id>/problems/<int:problem_id>")
    def show_problem(session_id: int, problem_id: int):
        problem, learner = load(session_id, problem_id)
        attempts = store.attempts_for(session_id, problem_id)
        outcome = logic.outcome_for(problem, attempts)
        return render_template(
            "problem.html", problem=problem, learner=learner, outcome=outcome,
            session_id=session_id, next_id=logic.next_problem_id(problem_id))

    @app.post("/sessions/<int:session_id>/problems/<int:problem_id>")
    def submit_answer(session_id: int, problem_id: int):
        problem, _ = load(session_id, problem_id)
        try:
            submitted = int(request.form["answer"])
        except (KeyError, ValueError):
            flash("Enter a whole number.")
            return redirect(url_for("show_problem", session_id=session_id, problem_id=problem_id))

        attempts = store.attempts_for(session_id, problem_id)
        try:
            attempt = logic.evaluate(problem, attempts, submitted)
        except logic.ProblemAlreadyResolved:
            flash("This problem is already finished. That answer was not recorded.")
        else:
            store.save_attempt(session_id, attempt)
        # Post/Redirect/Get: a browser refresh repeats the GET, not the POST.
        return redirect(url_for("show_problem", session_id=session_id, problem_id=problem_id))

    @app.get("/sessions/<int:session_id>/summary")
    def summary(session_id: int):
        learner = store.get_learner(session_id)
        if learner is None:
            abort(404)
        attempts = store.all_attempts(session_id)
        missed = sorted({a.problem_id for a in attempts if not a.correct})
        return render_template(
            "summary.html", learner=learner, attempts=attempts,
            missed=[logic.PROBLEMS[i] for i in missed], problems=logic.PROBLEMS)

    return app


app = create_app()
