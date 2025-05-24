from fastapi import FastAPI, UploadFile, File
import pandas as pd 
from io import StringIO

app = FastAPI() 



@app.post("/upload-csv/") # Endpoint to upload a CSV file
async def upload_csv(file: UploadFile = File(...)):
    try:

        contents = await file.read()
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        return {"rows": df.to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e)}