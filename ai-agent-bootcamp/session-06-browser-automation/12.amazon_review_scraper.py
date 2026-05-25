"""
Amazon Review Scraper — ScrapingDog API Demo

Scrapes Amazon product reviews using ScrapingDog API.
Requires: SCRAPINGDOG_API_KEY in .env
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

def scrape_amazon_reviews(asin: str, page: int = 1) -> dict:
    """Scrape Amazon reviews for a product ASIN."""
    api_key = os.getenv("SCRAPINGDOG_API_KEY")
    if not api_key:
        raise ValueError("SCRAPINGDOG_API_KEY not set. Get a key at https://scrapingdog.com")

    url = "https://api.scrapingdog.com/amazon/reviews"
    params = {"api_key": api_key, "asin": asin, "page": page}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    asin = input("Enter Amazon ASIN (e.g. B08N5WRWNW): ").strip()
    data = scrape_amazon_reviews(asin)
    for review in data.get("reviews", []):
        print(f"★ {review.get('rating')} — {review.get('title')}")
        print(f"  {review.get('body', '')[:200]}")
        print()
