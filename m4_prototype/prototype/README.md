# DataMan Text Prototype – Check an Answer + Two-Try Feedback

**Product slice:** ST-1.1 / ST-1.2 – Learner checks an answer and gets two-try feedback.
**Design question carried forward from M4:** Where does the try state live, and which layer decides retry vs. reveal, so the same rule can be reused when the interface changes to Flask?

## Run it

```bash
cd m4/prototype
python app.py              # text interface
python -m unittest -v      # acceptance-criteria checks (no interface)
```

`sample_run.txt` shows one complete recorded path.

## Three layers

| Layer | File | Responsibility |
|---|---|---|
| Text interface | `app.py` | Reads input, prints output and feedback. Makes no rule decisions. |
| Business logic | `dataman/logic.py` | Two-try rule, correctness check, EEE feedback, reveal gate, missed-problem report. No `input()`/`print()`. |
| Stubbed data | `dataman/store.py` | Problems, sessions, and Attempt records behind replaceable methods. |

## State represented on purpose

- **Attempt** (`problem_id`, `try_number`, `submitted_answer`, `correct`) is saved for every try (Design Studio 3B: separate Attempt record).
- **Try number** is calculated from the saved attempts (`logic.next_try_number`), not kept in a screen variable. This answers the critique question "where does Try 2 of 2 come from if the screen is reopened?"
- **Session** links attempts to a learner so results can be reported later (Design Studio 4C: Learner → session → problem attempts).

## Acceptance criteria demonstrated

| AC | Behavior | Shown in |
|---|---|---|
| AC1 | Correct on try 1 → "Correct!" and Attempt saved with try 1 | `test_ac1_…`, sample run (7 × 8) |
| AC2 | Wrong on try 1 → EEE, retry allowed, answer stays hidden | `test_ac2_…`, sample run (9 × 4) |
| AC3 | Wrong on try 2 → EEE, then answer revealed | `test_ac3_…`, sample run (12 ÷ 3) |
| AC4 | Every try is kept so missed problems can be reported later | `test_ac4_…`, results section of sample run |

## Intentionally stubbed

- Data lives in Python dictionaries (`InMemoryStore`) and is **lost when the program closes**.
- Three fixed problems stand in for curator-built Practice Sets.
- No Curator, Practice Set, or 10-problem limit yet. They are outside this slice.
- No login. The learner just types a name.

## Revisions caused by testing the prototype

1. **Try number is not a screen variable.** Design Studio 5B asked where "Try 2 of 2" comes from if the screen is reopened. Building the loop made this concrete: a `tries` counter in `app.py` would have put the rule in the interface. The try number is calculated in `logic.py` from saved attempts instead.
2. **Invalid input is not an attempt.** Typing `abc` raised a question the design never answered: does a non-number use up a try? I decided it does not. The interface rejects it before the logic is called (see `ask_number`). This needs to be confirmed with the product owner.
3. **No third try.** `check_answer` raises `ProblemAlreadyFinished` if called after a problem is correct or revealed, so the rule can't be bypassed by a different interface.

## Unresolved uncertainty (carried into Module 5)

- **Resume after closing (Design Studio 5A):** chose **Split the story**. Basic two-try behavior is built. Resume/persistence is deferred, but the store boundary is ready for it. Open question: must a learner be able to resume mid-problem, or only see history later?
- **Curator visibility:** can two curators see the same learner's history? The design can't answer this yet. It needs a product decision.
- **Invalid input rule** (Revision 2) needs confirmation.

## What carries into Module 5

`dataman/logic.py` as-is, the Attempt/Session state model, AC1–AC4, and replacing `InMemoryStore` with a persistent store behind the same methods.
