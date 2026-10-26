import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Web Scraper & ETL Dashboard", layout="wide")

st.title("🌐 Automated Web Scraper & ETL Pipeline")
st.write("Enter a target URL and configure your extraction settings below.")

# Sidebar / User Inputs
st.sidebar.header("Scraper Configuration")
target_url = st.sidebar.text_input("Target URL", value="https://quotes.toscrape.com")
max_pages = st.sidebar.slider("Number of Pages to Scrape", min_value=1, max_value=5, value=2)

run_button = st.sidebar.button("Run ETL Pipeline", type="primary")

def scrape_data(base_url: str, pages: int):
    raw_records = []
    
    for page in range(1, pages + 1):
        page_url = f"{base_url.rstrip('/')}/page/{page}/" if page > 1 else base_url
        st.write(f"📡 Fetching: `{page_url}`")
        
        try:
            res = requests.get(page_url, timeout=10)
            if res.status_code != 200:
                st.warning(f"Failed to fetch {page_url} (Status: {res.status_code})")
                break
        except Exception as e:
            st.error(f"Network error: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        quote_boxes = soup.find_all("div", class_="quote")

        # If page structure doesn't match quotes.toscrape.com, extract generic headings/paragraphs
        if not quote_boxes:
            headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
            for h in headings[:10]:
                raw_records.append({
                    "author": "Page Heading",
                    "quote": h,
                    "tags": ["web-content"]
                })
        else:
            for box in quote_boxes:
                text = box.find("span", class_="text").get_text(strip=True) if box.find("span", class_="text") else ""
                author = box.find("small", class_="author").get_text(strip=True) if box.find("small", class_="author") else "Unknown"
                tags = [t.get_text(strip=True) for t in box.find_all("a", class_="tag")]
                
                raw_records.append({
                    "author": author,
                    "quote": text,
                    "tags": tags
                })

        next_btn = soup.find("li", class_="next")
        if not next_btn and quote_boxes:
            break

    return raw_records

def transform_data(records):
    cleaned = []
    for r in records:
        text = r["quote"].replace("“", "").replace("”", "").strip()
        cleaned.append({
            "author": r["author"],
            "quote": text,
            "tags": ", ".join(r["tags"]),
            "word_count": len(text.split()),
            "char_count": len(text)
        })
    return pd.DataFrame(cleaned)

if run_button:
    with st.spinner("Extracting web pages..."):
        raw = scrape_data(target_url, max_pages)
    
    if not raw:
        st.error("No extractable elements found at that URL.")
    else:
        st.success(f"Extracted {len(raw)} records!")
        
        # Transformation
        df = transform_data(raw)
        
        # Display KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Unique Authors / Types", df["author"].nunique())
        col3.metric("Avg Word Count", round(df["word_count"].mean(), 1))
        
        # Display Interactive Data Table
        st.subheader("Extracted & Transformed Records")
        st.dataframe(df, use_container_width=True)
        
        # Download Button
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Clean CSV",
            data=csv_bytes,
            file_name="scraped_pipeline_output.csv",
            mime="text/csv"
        )