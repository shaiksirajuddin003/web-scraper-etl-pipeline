from scraper_etl.pipeline import ETLPipeline

if __name__ == "__main__":
    pipeline = ETLPipeline(max_pages=2)
    pipeline.run()