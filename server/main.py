from fastapi import FastAPI, UploadFile, File, Query
from typing import Optional
from datetime import datetime
import pandas as pd
from io import StringIO
from pymongo import MongoClient

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_budget"]

# 📤 Upload CSV Endpoint
@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        df.dropna(how="all", inplace=True)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["user_id"] = "demo_user"
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        db.transactions.insert_many(df.to_dict(orient="records"))
        return {"message": f"{len(df)} records uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

# 📄 Get Transactions with Filters
@app.get("/transactions/")
def get_transactions(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
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

# 📊 Summary Totals
@app.get("/insights/summary/")
def get_insights_summary():
    user_id = "demo_user"
    transactions = list(db.transactions.find({"user_id": user_id}, {"_id": 0}))

    total_income = sum(txn["amount"] for txn in transactions if txn["amount"] > 0)
    total_expense = sum(txn["amount"] for txn in transactions if txn["amount"] < 0)
    net = total_income + total_expense

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net": round(net, 2)
    }

# 🧾 Category Totals
@app.get("/insights/category-totals/")
def get_totals_per_category():
    pipeline = [
        {
            "$match": {
                "user_id": "demo_user",
                "category": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }
        },
        {"$sort": {"total": -1}}
    ]
    results = list(db.transactions.aggregate(pipeline))
    return [{"category": r["_id"], "total": round(r["total"], 2)} for r in results]

# 📅 Daily Spending Summary
@app.get("/insights/daily/")
def get_daily_spending():
    pipeline = [
        {"$match": {"user_id": "demo_user"}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
            "total_spent": {"$sum": "$amount"}
        }},
        {"$sort": {"_id": 1}}
    ]
    results = list(db.transactions.aggregate(pipeline))
    return [{"date": r["_id"], "total_spent": round(r["total_spent"], 2)} for r in results]

# 🧠 Summary in Plain Text
@app.get("/insights/summary-text/")
def get_summary_text(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    user_id = "demo_user"
    query = {"user_id": user_id}

    if start_date or end_date:
        query["date"] = {}
        if start_date:
            query["date"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["date"]["$lte"] = datetime.fromisoformat(end_date)

    transactions = list(db.transactions.find(query))
    if not transactions:
        return {"summary": "No transactions available for this period."}

    total_income = sum(txn["amount"] for txn in transactions if txn["amount"] > 0)
    total_expense = abs(sum(txn["amount"] for txn in transactions if txn["amount"] < 0))
    net = total_income - total_expense

    category_totals = {}
    for txn in transactions:
        cat = txn.get("category") or "Uncategorized"
        category_totals[cat] = category_totals.get(cat, 0) + txn["amount"]

    top_spent = sorted(
        [(cat, amt) for cat, amt in category_totals.items() if amt < 0],
        key=lambda x: x[1]
    )
    top_category = top_spent[0][0] if top_spent else "None"

    summary = (
        f"You earned ${total_income:.2f}, spent ${total_expense:.2f}, "
        f"and your net balance is ${net:.2f}. "
        f"Top spending category: {top_category}."
    )

    return {"summary": summary}

# 🔁 Health Check (Optional)
@app.get("/health")
def health_check():
    return {"status": "ok"}
