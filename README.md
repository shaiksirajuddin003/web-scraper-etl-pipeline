# Web Scraper & Clean Data Pipeline (ETL)

A modular, production-ready ETL pipeline written in pure Python. It crawls multi-page web content, extracts unstructured text, cleans and derives statistical features, and persists the results into both a SQLite database and CSV format.

## Architecture
- **Extract (`scraper_etl/extract.py`)**: Crawls pages using `requests` and `BeautifulSoup4`, handles pagination, and saves raw extraction snapshots.
- **Transform (`scraper_etl/transform.py`)**: Normalizes text, eliminates duplicate records, and computes derived metrics (word count, character length, tag counts).
- **Load (`scraper_etl/load.py`)**: Persists structured output to SQLite tables and flat CSV files.

## Setup & Running
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run pipeline
python main.py

# Run tests
pytest