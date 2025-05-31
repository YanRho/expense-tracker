from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from backend.db import db

router = APIRouter()

@router.get("/transactions/")
def get_transactions(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    query = {"user_id": "demo_user"}

    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date)

    if category:
        query["category"] = category

    results = list(db.transactions.find(query, {"_id": 0}))
    return results
