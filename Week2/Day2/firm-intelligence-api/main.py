from fastapi import FastAPI

from routers import firms, insights, knowledge, people, reports

app = FastAPI(title="Firm Intelligence API")
app.include_router(firms.router)
app.include_router(people.router)
app.include_router(reports.router)
app.include_router(knowledge.router)
app.include_router(insights.router)

# http://127.0.0.1:8000
@app.get("/health")
def health():
    return {"status": "OK"}