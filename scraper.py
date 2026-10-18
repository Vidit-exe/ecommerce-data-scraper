"""
Resilient E-Commerce Web Scraper & Data Pipeline
Extracts structured product catalog data across multiple pages, 
cleans messy values, and exports to CSV and JSON formats.
"""

import time
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def clean_price(raw_price: str) -> float:
    """Extract numeric float value from currency string (e.g., '£51.77' -> 51.77)."""
    match = re.search(r"[\d.]+", raw_price)
    return float(match.group()) if match else 0.0


def scrape_page(url: str, session: requests.Session):
    """Parses a single catalogue page and extracts product items."""
    try:
        response = session.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] Error fetching {url}: {e}")
        return [], None

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for article in soup.select("article.product_pod"):
        title = article.h3.a["title"].strip()
        price_raw = article.select_one(".price_color").get_text(strip=True)
        price_gbp = clean_price(price_raw)
        
        availability_text = article.select_one(".availability").get_text(strip=True)
        in_stock = "In stock" in availability_text
        
        rating_classes = article.select_one("p.star-rating")["class"]
        rating_word = next((c for c in rating_classes if c != "star-rating"), "Zero")
        star_rating = RATING_MAP.get(rating_word, 0)
        
        detail_rel_link = article.h3.a["href"]
        product_link = BASE_URL + detail_rel_link.replace("../", "")

        products.append({
            "title": title,
            "price_gbp": price_gbp,
            "star_rating": star_rating,
            "in_stock": in_stock,
            "product_url": product_link
        })

    next_btn = soup.select_one("li.next a")
    next_page_url = None
    if next_btn:
        next_page_url = BASE_URL + next_btn["href"]

    return products, next_page_url


def run_scraper(max_pages: int = 5):
    """Orchestrates multi-page scraping pipeline and exports structured data."""
    print(f"[*] Starting scraper pipeline (crawling up to {max_pages} pages)...")
    session = requests.Session()
    current_url = START_URL
    all_records = []
    page_count = 0

    while current_url and page_count < max_pages:
        page_count += 1
        print(f" -> Scraping Page {page_count}: {current_url}")
        
        page_data, next_url = scrape_page(current_url, session)
        all_records.extend(page_data)
        current_url = next_url

        # Polite crawler delay to avoid rate limiting
        time.sleep(1.0)

    if not all_records:
        print("[!] No records gathered.")
        return

    df = pd.DataFrame(all_records)
    
    # Validation & summary metrics
    print(f"\n[+] Successfully extracted {len(df)} products across {page_count} pages.")
    print(f" -> Average Price: £{df['price_gbp'].mean():.2f}")
    print(f" -> In-stock Percentage: {(df['in_stock'].mean() * 100):.1f}%")

    # Export deliverables
    csv_file = "scraped_products.csv"
    json_file = "scraped_products.json"
    df.to_csv(csv_file, index=False)
    df.to_json(json_file, orient="records", indent=2)
    print(f"[+] Deliverables saved to '{csv_file}' and '{json_file}'.")


if __name__ == "__main__":
    run_scraper(max_pages=5)