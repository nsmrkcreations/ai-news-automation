"""
GDELT API fetcher implementation
"""
import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import requests
from gdeltdoc import GdeltDoc, Filters
from .base import NewsFetcherBase

logger = logging.getLogger(__name__)

class GDELTFetcher(NewsFetcherBase):
    def __init__(self):
        self.gdelt = GdeltDoc()
        self.filters = Filters()
        
    def fetch_news(self, category: Optional[str] = None) -> List[Dict[Any, Any]]:
        """Fetch news from GDELT"""
        try:
            # Set up GDELT filters
            self.filters.keyword = self._get_category_keywords(category)
            self.filters.start_date = datetime.now().replace(hour=0, minute=0, second=0)
            self.filters.num_records = 50
            self.filters.english_only()
            
            logger.info(f"Fetching GDELT articles for category: {category or 'general'}")
            articles = self.gdelt.article_search(self.filters)
            
            if articles is None:
                logger.warning("No articles returned from GDELT")
                return []
                
            logger.info(f"Got {len(articles)} GDELT articles for {category or 'general'}")
            
            valid_articles = []
            for article in articles:
                if article.get('title') and article.get('url'):
                    standardized = self.standardize_article(article, category)
                    valid_articles.append(standardized)
            
            return valid_articles
            
        except Exception as e:
            logger.error(f"GDELT fetch error: {str(e)}")
            return []
    
    def _get_category_keywords(self, category: Optional[str]) -> str:
        """Map categories to GDELT search terms"""
        mapping = {
            'technology': 'technology OR tech OR artificial intelligence OR cybersecurity',
            'business': 'business OR economy OR market OR finance',
            'sports': 'sports OR Olympics OR football OR soccer OR basketball',
            'entertainment': 'entertainment OR movie OR music OR celebrity',
            'health': 'health OR medical OR healthcare OR medicine',
            'science': 'science OR research OR discovery',
            'politics': 'politics OR government OR election'
        }
        return mapping.get(category, '')
            
    def standardize_article(self, raw_article: Dict[str, Any], category: str = None) -> Dict[str, Any]:
        """Convert GDELT format to standard format"""
        article = super().standardize_article(raw_article, category)
        
        # Map GDELT specific fields
        article.update({
            'title': raw_article.get('title', '').strip(),
            'description': raw_article.get('description', '').strip(),
            'url': raw_article.get('url', ''),
            'urlToImage': raw_article.get('image', article['urlToImage']),
            'publishedAt': raw_article.get('seendate', article['publishedAt']),
            'source': {
                'id': raw_article.get('sourcecountry', 'unknown'),
                'name': raw_article.get('domain', 'Unknown')
            },
            'content': raw_article.get('text', ''),
            'provider': 'gdelt'
        })
        
        return article
