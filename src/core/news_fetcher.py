import os
import json
import requests
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        if not self.news_api_key:
            raise ValueError("NEWS_API_KEY environment variable is not set")
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_news(self, category: Optional[str] = None) -> List[Dict[Any, Any]]:
        """
        Fetch news articles from NewsAPI.org
        Args:
            category: Optional category to filter news
        Returns:
            List of news articles
        """
        endpoint = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.news_api_key,
            'language': 'en',
            'pageSize': 100  # Maximum articles per request
        }
        
        if category and category != 'general':
            params['category'] = category
            
        try:
            logger.info(f"Fetching news for category: {category or 'general'}")
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            logger.info(f"Successfully fetched {len(articles)} articles for {category or 'general'}")
            
            # Filter out articles with missing required fields
            valid_articles = []
            for article in articles:
                if all(article.get(field) for field in ['title', 'url']):
                    # Clean and standardize the article
                    cleaned_article = self._clean_article(article)
                    valid_articles.append(cleaned_article)
            
            return valid_articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
            
    def _clean_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize article format
        """
        return {
            'title': article.get('title', '').strip(),
            'description': article.get('description', '').strip(),
            'url': article.get('url', ''),
            'urlToImage': article.get('urlToImage', 'images/fallback.jpg'),
            'publishedAt': article.get('publishedAt', datetime.now().isoformat()),
            'source': article.get('source', {}).get('name', 'Unknown'),
            'category': article.get('category', 'general'),
            'isBreaking': False  # Will be updated by the orchestrator
        }
