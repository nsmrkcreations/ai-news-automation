"""
Script to fetch news with proper category handling
"""
import os
import json
from pathlib import Path
from src.core.news_fetcher import NewsFetcher
from src.core.logger import setup_logger

def main():
    # Set up logging
    setup_logger()
    
    # Initialize news fetcher
    fetcher = NewsFetcher()
    
    # Categories to fetch
    categories = ['technology', 'business', 'science', 'sports', 'entertainment', 'health', 'general']
    
    all_articles = []
    
    # Fetch news for each category
    for category in categories:
        try:
            print(f"Fetching {category} news...")
            articles = fetcher.fetch_news(category)
            all_articles.extend(articles)
            print(f"Fetched {len(articles)} {category} articles")
        except Exception as e:
            print(f"Error fetching {category} news: {str(e)}")
    
    # Save to file
    output_dir = Path("public/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "news.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    print(f"\nSuccessfully saved {len(all_articles)} articles to {output_file}")
    
    # Print sample article
    if all_articles:
        print("\nSample article:")
        sample = all_articles[0]
        print(f"Title: {sample.get('title')}")
        print(f"Category: {sample.get('category')}")
        print(f"Source: {sample.get('source', {}).get('name')}")
        print(f"URL: {sample.get('url')}")

if __name__ == "__main__":
    main()
