import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

st.set_page_config(
    page_title="Universal Web Scraper & ETL Studio",
    page_icon="🕸️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🕸️ Universal Web Scraper & ETL Studio")
st.caption("Extract structured data, perform automated validation, and export to CSV or JSON.")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Extraction Settings")

target_url = st.sidebar.text_input(
    "Target Website URL",
    value="https://quotes.toscrape.com"
)

scrape_mode = st.sidebar.radio(
    "Extraction Strategy",
    ["Standard Mode (Quotes/Text)", "Custom CSS Selector Mode (Any Site)"]
)

if scrape_mode == "Custom CSS Selector Mode (Any Site)":
    st.sidebar.info("💡 Right-click any element on the website -> Inspect -> look for the tag and class name.")
    container_tag = st.sidebar.text_input("Container Tag (e.g., div, article, li)", value="div")
    container_class = st.sidebar.text_input("Container Class (e.g., quote, post, product)", value="quote")
    target_tag = st.sidebar.text_input("Target Text Tag (e.g., span, h2, p)", value="span")
    target_class = st.sidebar.text_input("Target Text Class (optional)", value="text")

max_pages = st.sidebar.slider("Pages to Traverse", min_value=1, max_value=5, value=2)
request_delay = st.sidebar.slider("Timeout (seconds)", min_value=3, max_value=15, value=10)

run_etl = st.sidebar.button("🚀 Run Pipeline", type="primary", use_container_width=True)

# --- Core Extraction Engine ---
def scrape_pages(url: str, pages: int, timeout: int):
    results = []
    
    for page in range(1, pages + 1):
        page_url = f"{url.rstrip('/')}/page/{page}/" if page > 1 else url
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            res = requests.get(page_url, headers=headers, timeout=timeout)
            if res.status_code != 200:
                st.warning(f"⚠️ Page {page} returned status {res.status_code}")
                break
        except Exception as err:
            st.error(f"❌ Connection error on page {page}: {err}")
            break

        soup = BeautifulSoup(res.text, "html.parser")

        if scrape_mode == "Standard Mode (Quotes/Text)":
            quote_boxes = soup.find_all("div", class_="quote")
            if not quote_boxes:
                # Fallback: Scrape headers and paragraphs if not quotes.toscrape
                headings = soup.find_all(["h1", "h2", "h3", "p"])
                for item in headings[:15]:
                    txt = item.get_text(strip=True)
                    if len(txt) > 10:
                        results.append({
                            "source_page": page,
                            "category_author": item.name.upper(),
                            "extracted_text": txt,
                            "tags": "web-content"
                        })
            else:
                for box in quote_boxes:
                    t_elem = box.find("span", class_="text")
                    a_elem = box.find("small", class_="author")
                    tags = [t.get_text(strip=True) for t in box.find_all("a", class_="tag")]
                    
                    results.append({
                        "source_page": page,
                        "category_author": a_elem.get_text(strip=True) if a_elem else "Unknown",
                        "extracted_text": t_elem.get_text(strip=True) if t_elem else "",
                        "tags": ", ".join(tags) if tags else "none"
                    })
        else:
            # Custom CSS Extraction
            attrs = {"class": container_class} if container_class.strip() else {}
            containers = soup.find_all(container_tag, attrs=attrs)
            
            for item in containers:
                target_attrs = {"class": target_class} if target_class.strip() else {}
                found = item.find(target_tag, attrs=target_attrs) if target_class.strip() else item.find(target_tag)
                raw_text = found.get_text(strip=True) if found else item.get_text(strip=True)
                
                if raw_text:
                    results.append({
                        "source_page": page,
                        "category_author": "Custom Extracted",
                        "extracted_text": raw_text,
                        "tags": f"selector:{container_tag}.{container_class}"
                    })

    return results

# --- Pipeline Execution Flow ---
if run_etl:
    with st.spinner("Executing extraction and transformation..."):
        data = scrape_pages(target_url, max_pages, request_delay)
    
    if not data:
        st.error("No matching elements found. Check the URL and CSS selectors.")
    else:
        df = pd.DataFrame(data)
        
        # Transformation & Feature Engineering
        df["extracted_text"] = df["extracted_text"].str.replace("“", "").str.replace("”", "").str.strip()
        df["word_count"] = df["extracted_text"].apply(lambda x: len(x.split()))
        df["char_count"] = df["extracted_text"].apply(len)
        df = df[df["char_count"] > 0].drop_duplicates(subset=["extracted_text"])

        # Display Top Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Records Extracted", len(df))
        c2.metric("Unique Entities / Authors", df["category_author"].nunique())
        c3.metric("Average Word Count", f"{round(df['word_count'].mean(), 1)} words")
        c4.metric("Max Word Count", f"{df['word_count'].max()} words")

        st.markdown("---")

        # Interactive Filtering & Search
        st.subheader("🔍 Explore Cleaned Data")
        search_query = st.text_input("Filter results by keyword", placeholder="Type a word or name...")
        
        display_df = df
        if search_query:
            display_df = df[df["extracted_text"].str.contains(search_query, case=False, na=False) |
                            df["category_author"].str.contains(search_query, case=False, na=False)]

        st.dataframe(display_df, use_container_width=True)

        # Visualizations
        if df["category_author"].nunique() > 1:
            st.subheader("📊 Entity Distribution")
            top_counts = df["category_author"].value_counts().head(10)
            st.bar_chart(top_counts)

        # Export Buttons
        st.subheader("💾 Export Data")
        e1, e2 = st.columns(2)
        
        csv_data = df.to_csv(index=False).encode("utf-8")
        e1.download_button(
            label="📥 Download Structured CSV",
            data=csv_data,
            file_name="scraped_pipeline_data.csv",
            mime="text/csv",
            use_container_width=True
        )

        json_data = df.to_json(orient="records", indent=2)
        e2.download_button(
            label="📥 Download JSON Format",
            data=json_data,
            file_name="scraped_pipeline_data.json",
            mime="application/json",
            use_container_width=True
        )