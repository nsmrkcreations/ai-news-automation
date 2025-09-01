"""
The Guardian API fetcher implementation
"""
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from .base import NewsFetcherBase

logger = logging.getLogger(__name__)

class GuardianFetcher(NewsFetcherBase):
    def __init__(self):
        self.api_key = os.getenv('GUARDIAN_API_KEY')
        if not self.api_key:
            raise ValueError("GUARDIAN_API_KEY environment variable is not set")
        self.base_url = "https://content.guardianapis.com"
        
    def fetch_news(self, category: Optional[str] = None) -> List[Dict[Any, Any]]:
        """Fetch news from The Guardian API"""
        endpoint = f"{self.base_url}/search"
        
        # Map our categories to Guardian sections
        section = self._map_category_to_section(category)
        
        params = {
            'api-key': self.api_key,
            'show-fields': 'all',
            'page-size': 50,
            'order-by': 'newest'
        }
        
        if section:
            params['section'] = section
            
        try:
            logger.info(f"Fetching Guardian articles for category: {category or 'general'}")
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('response', {}).get('results', [])
            logger.info(f"Got {len(articles)} Guardian articles for {category or 'general'}")
            
            valid_articles = []
            for article in articles:
                if article.get('webTitle') and article.get('webUrl'):
                    standardized = self.standardize_article(article, category)
                    valid_articles.append(standardized)
            
            return valid_articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Guardian API fetch error: {str(e)}")
            return []
    
    def _map_category_to_section(self, category: Optional[str]) -> Optional[str]:
        """Map our standard categories to Guardian sections"""
        mapping = {
            'technology': 'technology',
            'business': 'business',
            'sports': 'sport',
            'entertainment': 'culture',
            'health': 'society',
            'science': 'science',
            'politics': 'politics'
        }
        return mapping.get(category)
            
    def standardize_article(self, raw_article: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Convert Guardian API format to standard format"""
        article = super().standardize_article(raw_article, category)
        
        fields = raw_article.get('fields', {})
        
        article.update({
            'title': raw_article.get('webTitle', '').strip(),
            'description': fields.get('trailText', '').strip(),
            'url': raw_article.get('webUrl', ''),
            'urlToImage': fields.get('thumbnail', article['urlToImage']),
            'publishedAt': raw_article.get('webPublicationDate', article['publishedAt']),
            'source': {
                'id': 'guardian',
                'name': 'The Guardian'
            },
            'content': fields.get('bodyText'),
            'author': fields.get('byline'),
            'provider': 'guardian'
        })
        
        return article
