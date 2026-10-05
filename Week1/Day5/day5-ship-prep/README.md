# Day 5: ship prep

Your increment, ready to package. `reconcile` and `worst_line` are both implemented
and all three gates are green before you start.

## Set up

```bash
uv venv .venv --python 3.12
```
```
Mac/Linux:  uv pip install --python .venv/bin/python -r requirements.txt
Windows:    uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

## Confirm you are starting from green

```
ruff check .          -> All checks passed!
mypy src tests        -> Success: no issues found in 2 source files
pytest -q             -> 8 passed
bash smoke.sh         -> smoke OK, exits 0
```

Prefix the first three with `.venv/Scripts/python.exe -m` on Windows, or
`.venv/bin/python -m` on Mac and Linux.

## What you ship

| File | State |
|---|---|
| `src/reconcile.py` | done |
| `tests/test_reconcile.py` | done |
| `smoke.sh` | a starting point. Add one assertion of your own |
| `RUNBOOK.md` | **you write this** |

## Done looks like

Gate green from a clean state, and your neighbour ran `smoke.sh` on your machine
and it passed first time.
