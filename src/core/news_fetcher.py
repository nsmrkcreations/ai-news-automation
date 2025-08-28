from datetime import datetime
import json
import os
from core.logger import setup_logger

logger = setup_logger()

class NewsFetcher:
    def __init__(self):
        self.news_file = 'public/data/news.json'
        self.ensure_data_directory()

    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.news_file), exist_ok=True)

    def save_news(self, articles):
        """Save news articles to JSON file"""
        try:
            existing = self.load_existing_news()
            # Add new articles at the beginning
            updated = articles + existing
            # Keep only last 100 articles to prevent file growing too large
            updated = updated[:100]
            
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(updated, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved {len(articles)} new articles")
        except Exception as e:
            logger.error(f"Error saving news: {e}")

    def load_existing_news(self):
        """Load existing news articles from JSON file"""
        try:
            if os.path.exists(self.news_file):
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading existing news: {e}")
            return []

    def get_news_since(self, timestamp):
        """Get news articles newer than the given timestamp"""
        articles = self.load_existing_news()
        return [a for a in articles if datetime.fromisoformat(a['publishedAt'].replace('Z', '+00:00')).timestamp() > timestamp]

    def get_news_by_category(self, category):
        """Get news articles for a specific category"""
        articles = self.load_existing_news()
        if category != 'all':
            articles = [a for a in articles if a['category'].lower() == category.lower()]
        return articles
