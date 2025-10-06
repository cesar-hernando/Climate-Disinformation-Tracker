from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

# Import backend pipeline
from source_finder_nitter import SourceFinder

app = FastAPI(title="Climate Disinformation Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class AnalyzeRequest(BaseModel):
    text: str
    mode: str = "find_source"  # "find_source" or "find_all", see if necessary
    initial_date: str = ""  
    final_date: str = ""    
    max_keywords: int = 5
    max_tweets: int = 200
    domain_index: int = 5 # Index of the Nitter domain to use, change if one domain is down
    n_keywords_dropped: int = 1 # No advanced search if n_keywords_dropped = 0
    excludes: set = {"nativeretweets", "replies"}

# Define source finder parameters 
claim = "Masks don't work against viruses - government lies to control us"

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        # Initialize SourceFinder with request parameters
        source_finder = SourceFinder(
            domain_index=req.domain_index, 
            max_keywords=req.max_keywords,
            n_keywords_dropped=req.n_keywords_dropped,
            excludes=req.excludes
        )

        if req.mode == "find_source":
            result = await source_finder.find_source(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        elif req.mode == "find_all":
            result = await source_finder.find_all(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        else:
            return {"error": f"Unknown mode: {req.mode}"}

        return result[0] # TODO: check if we want to return more
    except Exception as e:
        return {"error": str(e)}

# Mount index.html
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")