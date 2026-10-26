import csv
import logging
import sqlite3
from typing import List, Dict, Any
from scraper_etl.config import DB_PATH, CSV_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Loader:
    def __init__(self, db_path=DB_PATH, csv_path=CSV_PATH):
        self.db_path = db_path
        self.csv_path = csv_path

    def load_to_sqlite(self, records: List[Dict[str, Any]]) -> None:
        if not records:
            logging.warning("No records to load.")
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote TEXT NOT NULL,
                    author TEXT NOT NULL,
                    tag_count INTEGER,
                    tags TEXT,
                    char_length INTEGER,
                    word_count INTEGER
                )
            """)
            cursor.execute("DELETE FROM quotes")

            insert_query = """
                INSERT INTO quotes (quote, author, tag_count, tags, char_length, word_count)
                VALUES (:quote, :author, :tag_count, :tags, :char_length, :word_count)
            """
            cursor.executemany(insert_query, records)
            conn.commit()

        logging.info(f"Saved {len(records)} rows to SQLite: {self.db_path}")

    def load_to_csv(self, records: List[Dict[str, Any]]) -> None:
        if not records:
            return

        fieldnames = ["quote", "author", "tag_count", "tags", "char_length", "word_count"]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        logging.info(f"Saved {len(records)} rows to CSV: {self.csv_path}")