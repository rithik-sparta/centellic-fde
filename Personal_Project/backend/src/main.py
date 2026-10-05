from fastapi import FastAPI
from endpoints import assessment, borrower, document_store


app = FastAPI(title="Firm Intelligence API")
app.include_router(assessment.router)
app.include_router(borrower.router)
app.include_router(document_store.router)


# http://127.0.0.1:8000
@app.get("/health")
def health():
    return {"status": "OK"}