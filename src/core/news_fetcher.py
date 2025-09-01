"""
News fetcher with multiple provider support
"""
import os
import json
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from .fetchers import NewsAPIFetcher, GuardianFetcher, GDELTFetcher

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        """Initialize all news fetchers"""
        self.fetchers = []
        
        # Try to initialize each fetcher
        for fetcher_class in [NewsAPIFetcher, GuardianFetcher, GDELTFetcher]:
            try:
                self.fetchers.append(fetcher_class())
                logger.info(f"Successfully initialized {fetcher_class.__name__}")
            except Exception as e:
                logger.warning(f"Could not initialize {fetcher_class.__name__}: {str(e)}")
        
        if not self.fetchers:
            raise ValueError("No news fetchers could be initialized")
        
    def fetch_news(self, category: Optional[str] = None) -> List[Dict[Any, Any]]:
        """
        Fetch news articles from all available providers
        Args:
            category: Optional category to filter news
        Returns:
            List of standardized news articles from all providers
        """
        all_articles = []
        
        for fetcher in self.fetchers:
            try:
                # Get articles from this provider
                articles = fetcher.fetch_news(category)
                logger.info(f"Got {len(articles)} articles from {fetcher.__class__.__name__}")
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching from {fetcher.__class__.__name__}: {str(e)}")
                continue
        
        # Sort by publishedAt date, newest first
        all_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        
        return all_articles

    def save_to_json(self, articles: List[Dict[str, Any]], output_path: str):
        """Save articles to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(articles)} articles to {output_path}")
        except Exception as e:
            logger.error(f"Error saving articles to JSON: {str(e)}")
            raise
