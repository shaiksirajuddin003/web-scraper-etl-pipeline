import logging
from scraper_etl.extract import Extractor
from scraper_etl.transform import Transformer
from scraper_etl.load import Loader

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ETLPipeline:
    def __init__(self, max_pages: int = 2):
        self.extractor = Extractor(max_pages=max_pages)
        self.transformer = Transformer()
        self.loader = Loader()

    def run(self):
        logging.info("Starting ETL Pipeline...")
        raw_data = self.extractor.extract_quotes()
        transformed_data = self.transformer.transform(raw_data)
        self.loader.load_to_sqlite(transformed_data)
        self.loader.load_to_csv(transformed_data)
        logging.info("ETL Pipeline completed successfully.")