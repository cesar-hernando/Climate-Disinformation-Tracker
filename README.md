# Climate disinformation tracker

## Project Overview
This project detects the origins and spread of climate-related disinformation on Twitter/X by:
- Extracting keywords from claims using KeyBERT
- Generating advanced search queries
- Scraping tweets from Nitter (a privacy-focused Twitter frontend) using Playwright
- Aligning/contradicting tweets to claims using a transformer-based model (mDeBERTa-v3-base-mnli-xnli)
- Identifying the oldest aligned tweet as the likely source

## Key Components
- `main.py`: Entry point. Demonstrates end-to-end pipeline for a sample claim.
- `source_finder_nitter.py`: Orchestrates the pipeline. Key class: `SourceFinder`.
- `scrapper_nitter.py`: Scrapes tweets from Nitter using Playwright. Handles search URL construction and domain selection.
- `query_generator.py`: Extracts keywords from claims (KeyBERT) and builds search queries.
- `alignment.py`: Loads and applies a transformer model to classify tweet alignment (entailment/neutral/contradiction).
- `results/`: Stores CSVs of scraped tweets/results.

## Developer Workflows
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
- **Environment:**
  - Uses Playwright for browser automation (Firefox by default).

## Project-Specific Patterns
- **Keyword Extraction:** Uses KeyBERT with a multilingual model (`AIDA-UPM/mstsb-paraphrase-multilingual-mpnet-base-v2`).
- **Tweet Alignment:** Uses `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` for claim/tweet classification.
- **Nitter Domains:** Scraper fetches a list of Nitter instances and selects one at random for scraping.
- **CSV Normalization:** All tweet data is normalized to a standard dict format for downstream processing.
- **Batch Processing:** Alignment and filtering are performed in batches for efficiency.

## Integration Points
- **External APIs:**
  - Nitter (via Playwright scraping)
  - HuggingFace Transformers (for alignment and KeyBERT)
- **Data Flow:**
  1. Claim → Query → Scrape Tweets → Align/Filter → Find Oldest Source
  2. Results are saved as CSVs in `results/`

## Examples
- To add a new claim, modify the `claim` variable in `main.py`.
- To change the alignment model, update the `model_name` in `alignment.py`.
- To adjust scraping filters, edit the `excludes`/`filters` in `SourceFinder` or `ScraperNitter`.

---
For questions or unclear conventions, review the orchestrator (`SourceFinder`), or ask for clarification.
