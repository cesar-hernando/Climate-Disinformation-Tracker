from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi.staticfiles import StaticFiles

# Import backend pipeline
from source_finder_nitter import SourceFinder

app = FastAPI(title="Climate Disinformation Detector API")
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] if serving via VSCode Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class AnalyzeRequest(BaseModel):
    text: str
    mode: str = "find_source"  # "find_source" or "find_all", see if necessary
    initial_date: Optional[str] = None  
    final_date: Optional[str] = None    
    max_keywords: int = 5
    max_tweets: int = 200
    top_k: int = 3

sf = SourceFinder()

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        if req.mode == "find_source":
            result = sf.find_source(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        elif req.mode == "find_all":
            result = sf.find_all(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        else:
            return {"error": f"Unknown mode: {req.mode}"}

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}