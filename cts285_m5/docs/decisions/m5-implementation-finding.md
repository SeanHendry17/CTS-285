# M5 Implementation Finding: Answer Flow in Flask

**Product slice:** Answer Flow, the two-attempt rule for one practice problem (carried forward from the Module 4 Answer Flow Lab).

## Module 4 decisions carried forward

| Decision | M4 choice | Where it lives in Flask |
|---|---|---|
| Where the two-attempt rule is decided | Reusable business logic service | `m5/answer_flow/logic.py` (`evaluate`, `outcome_for`) |
| How attempts are represented | Separate Attempt records with `try_number` | `attempt` table in `m5/answer_flow/store.py` |
| What survives interruption | Attempt/result state through a data boundary | `AttemptStore` (SQLite). No Flask globals, no cookie state |
| How the interface knows what to show | Business logic returns outcome/state; UI renders it | Routes in `m5/app.py` pass an `Outcome` to `templates/problem.html` |

## Acceptance criterion tested (AC-AF-1)

> A learner gets at most two tries per problem. Every try is saved as its own Attempt with a try number. The answer stays hidden until the problem is resolved and is revealed after two wrong tries. Progress survives a reload, and missed problems can be retrieved after the session.

Tests: `m5/tests/test_flask_acceptance.py` (runs the real Flask routes and SQLite store), plus `m5/tests/test_logic.py` (rule only, no Flask).

| AC part | Test | Result |
|---|---|---|
| Wrong → correct saves try 1 and try 2 | `test_wrong_then_correct` | Pass |
| Two wrong tries reveal the answer | `test_wrong_wrong_reveals_answer` | Pass |
| Progress survives reload/restart | `test_progress_survives_reload` | Pass |
| No third attempt after resolution | `test_resubmit_after_resolved_does_not_add_attempt` | **Failed first, passes after fix** |
| Missed problems retrievable later | `test_curator_can_see_missed_problems` | Pass |

## Finding

**What Flask exposed:** In the Module 4 simulation, a learner could only act through the lab's buttons, so nobody could answer a problem that was already finished. In Flask, every answer is an HTTP POST, and a browser can send the same POST again (back button and resubmit, or a double click). The M4 scenarios never covered that case.

**Evidence:** My first `submit_answer` route called `logic.evaluate()` and saved the result without handling the case where the problem was already resolved. The resubmission test failed:

```
FAILED tests/test_flask_acceptance.py::test_resubmit_after_resolved_does_not_add_attempt
answer_flow.logic.ProblemAlreadyResolved: 1
```

Outside test mode, the same request returned **HTTP 500**, and the store still held **2 attempts**:

```
status of resubmission: 500 | attempts stored: 2
```

**What this confirmed:** The M4 decision to keep the two-attempt rule in a reusable logic service held up. The rule refused the third attempt by itself, and the try number came from stored Attempt records, not from the form, so no bad data was saved.

**What it exposed:** The boundary between the logic and the route was incomplete. The logic could say "already resolved," but the route had no plan for that answer, so the learner saw a server error. I classify this as a **weak implementation choice / coding defect in the route**, not a design assumption that failed.

**Revision:**
1. The route now catches `ProblemAlreadyResolved`, does not save anything, and shows "This problem is already finished. That answer was not recorded."
2. The route uses Post/Redirect/Get, so refreshing the page repeats a harmless GET instead of the POST.
3. The `attempt` table has `UNIQUE (session_id, problem_id, try_number)` as a backstop at the data boundary.

After the revision, all 10 tests pass (`python -m pytest` in `m5/`).

## What I would carry forward

Every rule in the logic layer needs a defined "no" answer that the route knows how to show. Testing only the happy paths from M4 would have missed this. The HTTP-specific scenario (repeated POST) is what found it.
