from fastapi import APIRouter, UploadFile, File
import pandas as pd
from io import StringIO
from backend.db import db

router = APIRouter()

@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode('utf-8')))
    df.dropna(how="all", inplace=True)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["user_id"] = "demo_user"
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    db.transactions.insert_many(df.to_dict(orient="records"))
    return {"message": f"{len(df)} records uploaded successfully"}
