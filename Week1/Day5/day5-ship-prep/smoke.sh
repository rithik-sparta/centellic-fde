#!/usr/bin/env bash
# Smoke test: proves the increment is alive. Exits 0 on success.
set -eu
PY=".venv/Scripts/python.exe"
[ -f "$PY" ] || PY=".venv/bin/python"

PYTHONPATH=src "$PY" -c "
from reconcile import reconcile, worst_line
r = reconcile(['38.70', '22.97', '33.32'], '94.99')
assert r.matched is True, 'reconcile failed'
assert worst_line(['10.00', '-42.50', '33.00']) == '-42.50', 'worst_line failed'
assert worst_line([]) is None, 'empty case failed'
print('smoke OK: reconcile matched, worst_line correct, empty handled')
"
