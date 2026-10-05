from fastapi import FastAPI
from endpoints import assessment, borrower


app = FastAPI(title="Firm Intelligence API")

# http://127.0.0.1:8000
@app.get("/health")
def health():
    return {"status": "OK"}