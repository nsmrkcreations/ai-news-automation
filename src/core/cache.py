import json
import os
from datetime import datetime, timedelta

class NewsCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
    def get_cached_news(self):
        """Get cached news if it exists and is not expired"""
        cache_file = os.path.join(self.cache_dir, 'news_cache.json')
        
        if not os.path.exists(cache_file):
            return None
            
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            
        # Check if cache is expired (older than 3 hours)
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        if datetime.now() - cache_time > timedelta(hours=3):
            return None
            
        return cache_data['articles']
        
    def cache_news(self, articles):
        """Cache the news articles"""
        cache_file = os.path.join(self.cache_dir, 'news_cache.json')
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'articles': articles
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
