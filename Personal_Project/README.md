# Personal Project

## Run locally

Run the API and UI in separate terminals from the project root. These commands
use the project's backend and frontend virtual environments.

### API

```bash
cd backend
source .venv/bin/activate
cd src
python -m uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

### UI

```bash
cd frontend
source .venv/bin/activate
streamlit run app.py
```

The Streamlit UI connects to the API at `http://127.0.0.1:8000`.

### Backend environment

The backend loads its environment from `backend/src/.env`. Set the relevance
floor and model name there:

```dotenv
RELEVANCE_FLOOR=0.4
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
ANTHROPIC_API_KEY=<your-anthropic-api-key>
VOYAGE_API_KEY=<your-voyage-api-key>
```

Also set `ANTHROPIC_API_KEY` and `VOYAGE_API_KEY` in that local environment
file.
