from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi.staticfiles import StaticFiles
import pandas as pd
from visualization.app import run_app

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
    top_k: int = 3

# Define source finder parameters 
domain_index = 5 # Index of the Nitter domain to use, change if one domain is down
claim = "Masks don't work against viruses - government lies to control us"
max_keywords = 5 # Maximum number of keywords extracted
n_keywords_dropped = 1 # No advanced search if n_keywords_dropped = 0
excludes={"nativeretweets", "replies"}
top_n_tweeters = 3 # Top usernames with more tweets about a topic

source_finder = SourceFinder(domain_index=domain_index, 
                             max_keywords=max_keywords, 
                             n_keywords_dropped=n_keywords_dropped, 
                             excludes=excludes)

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        if req.mode == "find_source":
            result = source_finder.find_source(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )
        elif req.mode == "find_all":
            file_name, tweet_list = source_finder.find_all(
                claim=req.text,
                initial_date=req.initial_date,
                final_date=req.final_date,
            )

            if file_name is not None:
                df = pd.read_csv(file_name) if tweet_list is None else tweet_list

                df["text"] = (
                    df["text"]
                    .str.replace(r"\\n", "\n", regex=True)   # turn \n into newline
                    .str.strip('"\'')                        # remove wrapping quotes
                )

                # Create and run the visualization app
                run_app(df, claim, debug=False)

        else:
            return {"error": f"Unknown mode: {req.mode}"}

        return result[0] # TODO: check if we want to return more
    except Exception as e:
        return {"error": str(e)}

# Mount index.html
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")