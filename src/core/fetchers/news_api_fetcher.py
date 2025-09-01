"""
NewsAPI fetcher implementation
"""
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from .base import NewsFetcherBase

logger = logging.getLogger(__name__)

class NewsAPIFetcher(NewsFetcherBase):
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NEWS_API_KEY environment variable is not set")
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_news(self, category: Optional[str] = None) -> List[Dict[Any, Any]]:
        """Fetch news from NewsAPI"""
        endpoint = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'language': 'en',
            'pageSize': 100
        }
        
        if category and category != 'general':
            params['category'] = category
            
        try:
            logger.info(f"Fetching NewsAPI articles for category: {category or 'general'}")
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            logger.info(f"Got {len(articles)} NewsAPI articles for {category or 'general'}")
            
            valid_articles = []
            for article in articles:
                if all(article.get(field) for field in ['title', 'url']):
                    standardized = self.standardize_article(article, category)
                    valid_articles.append(standardized)
            
            return valid_articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI fetch error: {str(e)}")
            return []
            
    def standardize_article(self, raw_article: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Convert NewsAPI format to standard format"""
        article = super().standardize_article(raw_article, category)
        
        # Map NewsAPI specific fields
        article.update({
            'title': raw_article.get('title', '').strip(),
            'description': raw_article.get('description', '').strip(),
            'url': raw_article.get('url', ''),
            'urlToImage': raw_article.get('urlToImage', article['urlToImage']),
            'publishedAt': raw_article.get('publishedAt', article['publishedAt']),
            'source': {
                'id': raw_article.get('source', {}).get('id'),
                'name': raw_article.get('source', {}).get('name', 'Unknown')
            },
            'content': raw_article.get('content'),
            'author': raw_article.get('author'),
            'provider': 'newsapi'
        })
        
        return article
