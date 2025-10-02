from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# Import your backend pipeline
from source_finder_nitter import find_source, find_all

app = FastAPI(title="Climate Disinformation Detector API")

# Request schema
class AnalyzeRequest(BaseModel):
    text: str
    mode: str = "find_source"  # "find_source" or "find_all", see if necessary
    initial_date: Optional[str] = None  
    final_date: Optional[str] = None    
    max_keywords: int = 5
    max_tweets: int = 200
    top_k: int = 3

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        if req.mode == "find_source":
            result = find_source(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        elif req.mode == "find_all":
            result = find_all(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        else:
            return {"error": f"Unknown mode: {req.mode}"}

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
