# Climate disinformation tracker

This project is part of the Joint Interdisciplinary Project (JIP), organized by TU Delft. JIP brings together students from different faculties
to work in a two-months project in collaboration with a company. Our client was the Dutch National Police and the team combined the following expertise:
- Amir Niknam (Supervisor): Policeman, with background in Applied Cognitive Psychology
- César Hernando de la Fuente: Quantum Information Science and Technology
- Kasper Trouwee: Management of Technology
- María Paula Jiménez Moreno: Quantum Information Science and Technology
- Manya Atul Narkar: Computer Science
- Shirley Li: Data Science
- Vincent van Vliet: Computer Science
 



## Project Overview
This project detects the origins and spread of climate-related disinformation on Twitter/X by:
- Extracting keywords from claims using KeyBERT
- Generating advanced search queries
- Scraping tweets from Nitter (a privacy-focused Twitter frontend) using Playwright
- Aligning/contradicting tweets to claims using a transformer-based model (mDeBERTa-v3-base-mnli-xnli)
- Identifying the oldest aligned tweet as the likely source

It further has the option to analyze all tweets and create a visualization.

## Key Components
- `main.py`: Entry point. Demonstrates end-to-end pipeline for a sample claim.
- `source_finder_nitter.py`: Orchestrates the pipeline. Key class: `SourceFinder`.
- `scrapper_nitter.py`: Scrapes tweets from Nitter using Playwright. Handles search URL construction and domain selection.
- `query_generator.py`: Extracts keywords from claims (KeyBERT) and builds search queries.
- `alignment.py`: Loads and applies a transformer model to classify tweet alignment (entailment/neutral/contradiction).
- `results/`: Stores CSVs of scraped tweets/results.
- `visualization/`: Contains files to create visualization of tweets using Dash

## Developer Workflows
- **Requirements:**
  ```
  python >= 3.11
  ```
- **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  python -m playwright install
  playwright install
  ```
- **Run pipeline:**
  Edit parameters in `main.py` and run:
  ```bash
  python main.py
  ```

**Run tool with UI**
```bash
# On Linux/macOS:
uvicorn app:app --reload

# On Windows:
uvicorn app:app
```
  Then the user interface should be accessible at `http://127.0.0.1:8000`
- **Environment:**
  - Uses Playwright for browser automation (Firefox by default).

## Examples
- To add a new claim, modify the `claim` variable in `main.py`.
- To change the alignment model, update the `model_name` in `alignment.py`.
- To adjust scraping filters, edit the `excludes`/`filters` in `SourceFinder` or `ScraperNitter`.

---
For questions or unclear conventions, review the orchestrator (`SourceFinder`), or ask for clarification. Further information on the frontend can be found in `/frontend`
