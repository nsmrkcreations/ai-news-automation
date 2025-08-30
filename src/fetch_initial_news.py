"""
Script to fetch initial news data for testing
"""
import os
from dotenv import load_dotenv
from core.news_fetcher import NewsFetcher
from core.logger import setup_logger
import json

def fetch_initial_news():
    """Fetch initial news data for all categories"""
    logger = setup_logger()
    
    # Load environment variables
    load_dotenv()
    
    # Create news fetcher
    fetcher = NewsFetcher()
    
    # Categories to fetch
    categories = ['technology', 'business', 'science', 'world', 'general']
    
    all_articles = []
    
    for category in categories:
        try:
            logger.info(f"Fetching {category} news...")
            articles = fetcher.fetch_news(category)
            for article in articles:
                article['category'] = category
            all_articles.extend(articles)
            logger.info(f"Fetched {len(articles)} articles for {category}")
        except Exception as e:
            logger.error(f"Error fetching {category} news: {str(e)}")
    
    # Save to public/data/news.json
    output_dir = "public/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "news.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(all_articles)} articles to {output_file}")

if __name__ == "__main__":
    fetch_initial_news()
