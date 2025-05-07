from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.analyzer import analyze_journeys
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile):
    try:
        data = json.loads(await file.read())
        if not isinstance(data, list):
            raise ValueError("Uploaded file must contain a list of sessions.")
        insights = analyze_journeys(data)
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
