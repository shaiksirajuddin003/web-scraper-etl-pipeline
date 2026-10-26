import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Transformer:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return text.strip().replace("“", "").replace("”", "").replace('"', "")

    def transform(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logging.info("Transforming raw data...")
        cleaned_records = []
        seen = set()

        for item in raw_records:
            quote = self.clean_text(item.get("raw_text", ""))
            author = item.get("raw_author", "").strip()
            tags = item.get("raw_tags", [])

            identifier = (quote, author)
            if not quote or identifier in seen:
                continue
            seen.add(identifier)

            cleaned_records.append({
                "quote": quote,
                "author": author,
                "tag_count": len(tags),
                "tags": ", ".join(tags) if tags else "untagged",
                "char_length": len(quote),
                "word_count": len(quote.split())
            })

        logging.info(f"Transformed into {len(cleaned_records)} validated, clean records.")
        return cleaned_records