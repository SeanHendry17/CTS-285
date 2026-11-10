"""Acceptance tests run against the working Flask app (real routes, real SQLite).

AC-AF-1 (carried forward from Module 4, Answer Flow Lab):
  A learner gets at most two tries per problem. Every try is saved as its own
  Attempt with a try number. The answer stays hidden until the problem is
  resolved, and is revealed after two wrong tries. Progress survives a reload,
  and missed problems can be retrieved after the session.
"""
import re

import pytest

from app import create_app


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def client(db_path):
    app = create_app(db_path)
    app.config["TESTING"] = True
    return app.test_client()


def start(client, name="Maya"):
    r = client.post("/sessions", data={"learner": name})
    assert r.status_code == 302
    m = re.search(r"/sessions/(\d+)/problems/(\d+)", r.headers["Location"])
    return int(m.group(1))


def answer(client, sid, pid, value):
    return client.post(f"/sessions/{sid}/problems/{pid}", data={"answer": value},
                       follow_redirects=True)


def stored(client, sid, pid):
    return client.application.extensions["attempt_store"].attempts_for(sid, pid)


def test_wrong_then_correct(client):
    sid = start(client)
    page = answer(client, sid, 1, "54").get_data(as_text=True)
    assert "Try: 2" in page and "Answer hidden" in page
    page = answer(client, sid, 1, "56").get_data(as_text=True)
    assert "Correct!" in page
    assert [(a.try_number, a.correct) for a in stored(client, sid, 1)] == [(1, False), (2, True)]


def test_wrong_wrong_reveals_answer(client):
    sid = start(client)
    answer(client, sid, 1, "1")
    page = answer(client, sid, 1, "2").get_data(as_text=True)
    assert "Answer: 56" in page and "Out of tries" in page


def test_progress_survives_reload(db_path, client):
    sid = start(client)
    answer(client, sid, 1, "54")
    # Simulate a server restart / page reload: brand new app, same data store.
    fresh = create_app(db_path).test_client()
    page = fresh.get(f"/sessions/{sid}/problems/1").get_data(as_text=True)
    assert "Try: 2" in page


def test_resubmit_after_resolved_does_not_add_attempt(client):
    """Browser back button / double-click sends the POST again after the problem is done."""
    sid = start(client)
    answer(client, sid, 1, "1")
    answer(client, sid, 1, "2")           # resolved: answer revealed
    r = answer(client, sid, 1, "56")      # resubmitted form
    assert r.status_code == 200
    assert "already finished" in r.get_data(as_text=True)
    assert len(stored(client, sid, 1)) == 2


def test_curator_can_see_missed_problems(client):
    sid = start(client)
    answer(client, sid, 1, "56")          # right first try
    answer(client, sid, 2, "30")          # wrong, then right
    answer(client, sid, 2, "36")
    answer(client, sid, 3, "1")           # wrong twice
    answer(client, sid, 3, "2")
    page = client.get(f"/sessions/{sid}/summary").get_data(as_text=True)
    missed = page.split("<h2>Missed problems</h2>")[1].split("<h2>")[0]
    assert "9 × 4" in missed and "12 ÷ 3" in missed and "7 × 8" not in missed
