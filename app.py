import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import pandas as pd
from visualization.app import create_app
from typing import List, Set, Optional
from query_builder_synonyms import SynonymQueryBuilder

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
    n_keywords_dropped: int = 1 # No advanced search if n_keywords_dropped = 0
    excludes: set = {"nativeretweets", "replies"}

    # Synonym-related parameters
    synonyms: bool = False
    model_name: Optional[str] = "en_core_web_md"
    top_n_syns: Optional[int] = 4
    threshold: Optional[float] = 0.1
    max_syns_per_kw: Optional[int] = 2
    selected_synonyms: dict = {}
    keywords: Optional[list] = []
    earliest_k: int = 0

# Request schema for visualization
class VisualizationRequest(BaseModel):
    filename: str
    claim: str

# Define source finder parameters 
claim = "Masks don't work against viruses - government lies to control us"

builders = {}

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        # Initialize SourceFinder with request parameters
        source_finder = SourceFinder(
            max_keywords=req.max_keywords,
            n_keywords_dropped=req.n_keywords_dropped,
            excludes=req.excludes,
        )

        if req.mode == "find_source":
            result = await source_finder.find_source(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
                synonyms=req.synonyms,
                model_name=req.model_name,
                top_n_syns=req.top_n_syns,
                threshold=req.threshold,
                max_syns_per_kw=req.max_syns_per_kw,
                user_choices=req.selected_synonyms,
                keywords=req.keywords,
                earliest_k=req.earliest_k,
            )
        elif req.mode == "find_all":
            file_name, tweet_list = await source_finder.find_all(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
                synonyms=req.synonyms,
                model_name=req.model_name,
                top_n_syns=req.top_n_syns,
                threshold=req.threshold,
                max_syns_per_kw=req.max_syns_per_kw,
                user_choices=req.selected_synonyms,
                keywords=req.keywords
            )
            if file_name is not None:
                return file_name
            else:
                return {"error": "No tweets found"}

        else:
            return {"error": f"Unknown mode: {req.mode}"}

        earliest_batch = result[2] if result[2] is not None else []

        return result[0], earliest_batch # TODO: check if we want to return more
    except Exception as e:
        return {"error": str(e)}

# Endpoint to serve the Dash visualization app
@app.post("/api/visualization")
def serve_dashboard(req: VisualizationRequest):
    path = req.filename.split("data/", maxsplit=1)[-1].replace(".csv", "")
    dash_app = create_app(req.filename, req.claim, requests_pathname_prefix=f"/visualization/{path}/")
    # Only mount if not already mounted
    if not any(route.path == f"/visualization/{path}/" for route in app.routes):
        app.mount(f"/visualization/{path}", WSGIMiddleware(dash_app.server))
    return {"redirect_url": f"/visualization/{path}"}

@app.post("/api/synonyms")
async def get_synonyms(request: Request):
    data = await request.json()
    claim = data["text"]
    params = data.get("params", {})

    builder = SynonymQueryBuilder(
        sentence=claim,
        max_keywords=params.get("max_keywords", 5),
        n_keywords_dropped=params.get("n_keywords_dropped", 1),
        model_name=params.get("model_name", "en_core_web_md"),
        top_n_syns=params.get("top_n_syns", 5),
        threshold=params.get("threshold", 0.1),
        max_syns_per_kw=params.get("max_syns_per_kw", 2)
    )

    synonyms = builder.get_contextual_synonyms()
    builders[claim] = builder  # store to use later for query building

    return {"keywords": builder.keywords, "synonyms": synonyms}

# Root endpoint serves the frontend
@app.get("/")
def root():
    return FileResponse(os.path.join("frontend", "index.html"))

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")
