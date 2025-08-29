import os
import json
import requests
from typing import List, Dict
from datetime import datetime
from pathlib import Path

class NewsAggregator:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2/top-headlines'
        self.categories = os.getenv('NEWS_CATEGORIES', 'technology,science,business,ai').split(',')
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.testing = os.getenv('TESTING', 'false').lower() == 'true'

    def fetch_trending(self, category: str = None, country: str = 'us', page_size: int = 10) -> List[Dict]:
        """Fetch trending news articles"""
        # In testing mode, try to use cache first
        if self.testing:
            cached_data = self._get_cached_data(category, country)
            if cached_data:
                return cached_data[:page_size]  # Return only requested number of articles

        params = {
            'apiKey': self.api_key,
            'pageSize': page_size,
            'language': 'en',
            'country': country
        }
        
        if category:
            params['category'] = category

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            
            # Cache the results if in testing mode
            if self.testing:
                self._cache_data(articles, category, country)
                
            return articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            if self.testing:
                print("Attempting to use cached data...")
                cached_data = self._get_cached_data(category, country)
                if cached_data:
                    return cached_data[:page_size]
            return []
            
    def _get_cache_file(self, category: str, country: str) -> Path:
        """Get the cache file path for the given parameters"""
        category = category or 'all'
        return self.cache_dir / f"news_cache_{category}_{country}.json"
        
    def _get_cached_data(self, category: str, country: str) -> List[Dict]:
        """Get cached news data if available and not expired"""
        cache_file = self._get_cache_file(category, country)
        if not cache_file.exists():
            return []
            
        try:
            data = json.loads(cache_file.read_text())
            # Check if cache is from today
            cache_date = datetime.fromisoformat(data['timestamp']).date()
            if cache_date == datetime.now().date():
                return data['articles']
        except Exception as e:
            print(f"Error reading cache: {e}")
        return []
        
    def _cache_data(self, articles: List[Dict], category: str, country: str):
        """Cache the news data"""
        cache_file = self._get_cache_file(category, country)
        data = {
            'timestamp': datetime.now().isoformat(),
            'articles': articles
        }
        try:
            cache_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error writing cache: {e}")

    def extract_keywords(self, articles: List[Dict]) -> List[str]:
        """Extract relevant keywords from articles"""
        keywords = set()
        for article in articles:
            # Extract from title and description
            for text in [article.get('title', ''), article.get('description', '')]:
                words = text.lower().split()
                keywords.update([word for word in words if len(word) > 4])
        
        # Remove common words and return top keywords
        common_words = {'about', 'after', 'again', 'their', 'these', 'those', 'where', 'which'}
        keywords = keywords - common_words
        return list(keywords)[:10]  # Return top 10 keywords

    def format_for_static_site(self, articles: List[Dict]) -> List[Dict]:
        """Format articles for static site generation"""
        formatted = []
        for article in articles:
            formatted_article = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'urlToImage': article.get('urlToImage', ''),
                'publishedAt': article.get('publishedAt', datetime.now().isoformat()),
                'source': article.get('source', {}).get('name', 'Unknown Source'),
                'category': article.get('category', 'technology')
            }
            formatted.append(formatted_article)
        return formatted
