from fastapi import FastAPI
from backend.routes import upload, transactions, insights

app = FastAPI()

app.include_router(upload.router)
app.include_router(transactions.router)
app.include_router(insights.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
