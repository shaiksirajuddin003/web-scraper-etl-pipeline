import json
import logging
import requests
from bs4 import BeautifulSoup
from scraper_etl.config import BASE_URL, HEADERS, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Extractor:
    def __init__(self, base_url: str = BASE_URL, max_pages: int = 3):
        self.base_url = base_url
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_page(self, url: str) -> str:
        logging.info(f"Fetching: {url}")
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def extract_quotes(self) -> list[dict]:
        current_url = self.base_url
        all_raw_data = []
        pages_scraped = 0

        while current_url and pages_scraped < self.max_pages:
            html = self.fetch_page(current_url)
            soup = BeautifulSoup(html, "html.parser")
            quote_blocks = soup.find_all("div", class_="quote")

            for block in quote_blocks:
                text = block.find("span", class_="text").get_text()
                author = block.find("small", class_="author").get_text()
                tags = [tag.get_text() for tag in block.find_all("a", class_="tag")]
                
                all_raw_data.append({
                    "raw_text": text,
                    "raw_author": author,
                    "raw_tags": tags
                })

            next_btn = soup.find("li", class_="next")
            if next_btn and next_btn.find("a"):
                next_path = next_btn.find("a")["href"]
                current_url = f"{self.base_url}{next_path}"
                pages_scraped += 1
            else:
                break

        raw_output_file = RAW_DATA_DIR / "raw_quotes.json"
        with open(raw_output_file, "w", encoding="utf-8") as f:
            json.dump(all_raw_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Extracted {len(all_raw_data)} raw records across {pages_scraped + 1} page(s).")
        return all_raw_data