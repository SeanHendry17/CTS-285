# CTS-285 Module 5 – Answer Flow in Flask

Minimal Flask implementation of the **Answer Flow** slice (two-attempt rule) from Module 4.

## Run in Codespaces

```bash
cd m5
pip install -r requirements.txt
flask --app app run --debug
```

Open the forwarded port (5000), enter a name, and answer the problems.

## Run the tests

```bash
cd m5
python -m pytest -v
```

## Where things are

| What | File |
|---|---|
| Flask entry point and routes | `app.py` |
| Business logic (two-attempt rule) | `answer_flow/logic.py` |
| Data/state boundary (SQLite) | `answer_flow/store.py` |
| Templates | `templates/` |
| Acceptance criterion AC-AF-1 tests | `tests/test_flask_acceptance.py` |
| Logic unit tests | `tests/test_logic.py` |
| Implementation finding | `../docs/decisions/m5-implementation-finding.md` |

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Start page |
| POST | `/sessions` | Start a practice session |
| GET | `/sessions/<id>/problems/<pid>` | Show the problem and its current state |
| POST | `/sessions/<id>/problems/<pid>` | Submit an answer (then redirect) |
| GET | `/sessions/<id>/summary` | Missed problems and all attempts |

## User path

Start → answer 7 × 8 → (wrong → try again → correct, or wrong twice → answer revealed) → next problem → results page showing missed problems.
