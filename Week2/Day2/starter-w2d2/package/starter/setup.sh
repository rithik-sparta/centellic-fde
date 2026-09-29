pip install --break-system-packages fastapi==0.115.6 httpx==0.28.1
cd starter
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m pip list
PYTHONPATH=src .venv/bin/python -m uvicorn api:app --reload
