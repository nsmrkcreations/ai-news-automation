"""
Base fetcher class defining the common interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class NewsFetcherBase(ABC):
    """Abstract base class for news fetchers"""
    
    @abstractmethod
    def fetch_news(self, category: Optional[str] = None) -> List[Dict[Any, Any]]:
        """Fetch news articles from the provider"""
        pass
        
    def standardize_article(self, raw_article: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """
        Standardize article format across all providers
        
        Standard format:
        {
            "title": str,
            "description": str,
            "url": str,
            "urlToImage": str,
            "publishedAt": ISO timestamp str,
            "source": {
                "id": str,
                "name": str
            },
            "category": str,
            "content": str (optional),
            "author": str (optional),
            "provider": str (which API provided this),
            "fetchedAt": ISO timestamp
        }
        """
        return {
            'title': '',  # Implement in child class
            'description': '',
            'url': '',
            'urlToImage': 'images/fallback.jpg',
            'publishedAt': datetime.now().isoformat(),
            'source': {
                'id': None,
                'name': 'Unknown'
            },
            'category': category or 'general',
            'content': None,
            'author': None,
            'provider': 'unknown',
            'fetchedAt': datetime.now().isoformat()
        }
