import os
import requests
from typing import List, Dict

class NewsAggregator:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2/top-headlines'
        self.categories = os.getenv('NEWS_CATEGORIES', 'technology,science,business,ai').split(',')

    def fetch_trending(self, category: str = None, country: str = 'us', page_size: int = 20) -> List[Dict]:
        """Fetch trending news articles"""
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
            return response.json().get('articles', [])
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

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
