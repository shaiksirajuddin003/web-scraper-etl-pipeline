from scraper_etl.transform import Transformer

def test_clean_text_removes_quotes():
    raw = '“The greatest glory in living lies not in never falling.”'
    cleaned = Transformer.clean_text(raw)
    assert cleaned == "The greatest glory in living lies not in never falling."

def test_transform_computes_metrics_and_deduplicates():
    transformer = Transformer()
    raw_sample = [
        {"raw_text": "“Stay hungry, stay foolish.”", "raw_author": "Steve Jobs", "raw_tags": ["tech", "life"]},
        {"raw_text": "“Stay hungry, stay foolish.”", "raw_author": "Steve Jobs", "raw_tags": ["tech", "life"]}
    ]
    result = transformer.transform(raw_sample)
    
    assert len(result) == 1
    record = result[0]
    assert record["author"] == "Steve Jobs"
    assert record["tag_count"] == 2
    assert record["word_count"] == 4
    assert record["quote"] == "Stay hungry, stay foolish."