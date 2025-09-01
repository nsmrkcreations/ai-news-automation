"""
NewsAPI provider implementation.
"""
import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .news_providers import NewsProvider
from .logger import get_logger

logger = get_logger(__name__)

class NewsAPIProvider(NewsProvider):
    """NewsAPI provider implementation."""
    
    def __init__(self):
        """Initialize the NewsAPI provider."""
        super().__init__("NewsAPI")
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            self.is_available = False
            self.last_error = "NewsAPI key not found"
        self.is_available = True
        self.last_error = None
        
        # Map NewsAPI categories to our categories
        self.category_mapping = {
            'technology': 'technology',
            'business': 'business',
            'science': 'science',
            'sports': 'sports',
            'entertainment': 'entertainment',
            'health': 'science',
            'general': 'general'
        }

    def _make_request(self, category: str = None, country: str = 'us') -> Dict[str, Any]:
        """Make a request to the NewsAPI.
        
        Args:
            category: Optional category to filter by
            country: Country code for news sources
            
        Returns:
            Dict containing the API response
        """
        headers = {
            'X-Api-Key': self.api_key
        }
        
        params = {
            'country': country,
            'pageSize': 50
        }
        
        if category:
            # Map our category to NewsAPI category
            for newsapi_cat, our_cat in self.category_mapping.items():
                if our_cat == category:
                    params['category'] = newsapi_cat
                    break
        
        try:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                max_retries=3,
                pool_connections=100,
                pool_maxsize=100
            )
            session.mount("https://", adapter)
            
            response = session.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
            self.is_available = False
            self.last_error = str(e)
            raise

    def _format_date(self, date_str: str) -> str:
        """Format NewsAPI date to ISO format.
        
        Args:
            date_str: Date string from NewsAPI
            
        Returns:
            ISO formatted date string
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            return dt.isoformat() + "Z"
        except (ValueError, TypeError):
            return datetime.utcnow().isoformat() + "Z"

    def fetch_news(self, category: str = None) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of parsed news articles
        """
        if not self.is_available:
            raise Exception(f"Provider {self.name} is not available: {self.last_error}")
            
        try:
            raw_data = self._make_request(category)
            articles = []
            
            for item in raw_data.get('articles', []):
                # Skip articles without required fields
                if not all(item.get(field) for field in ['url', 'title']):
                    continue
                    
                source = item.get('source', {})
                article = {
                    'title': item['title'],
                    'url': item['url'],
                    'description': item.get('description', ''),
                    'content': item.get('content', ''),
                    'publishedAt': self._format_date(item.get('publishedAt', '')),
                    'source': {
                        'id': source.get('id', 'newsapi'),
                        'name': source.get('name', 'NewsAPI')
                    },
                    'author': item.get('author'),
                    'imageUrl': item.get('urlToImage'),
                    'category': category or 'general'
                }
                
                articles.append(article)
                
            return articles
            
        except Exception as e:
            self.is_available = False
            self.last_error = str(e)
            logger.error(f"Error fetching news from NewsAPI: {e}")
            raise
