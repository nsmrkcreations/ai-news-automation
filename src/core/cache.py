"""
Cache manager for storing and retrieving news data
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class Cache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def save_news(self, category: str, articles: List[Dict[Any, Any]]):
        """Save news articles to cache"""
        cache_file = os.path.join(self.cache_dir, f"news_cache_{category}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'articles': articles
            }, f, ensure_ascii=False, indent=2)
            
    def get_news(self, category: str) -> List[Dict[Any, Any]]:
        """Get news articles from cache"""
        cache_file = os.path.join(self.cache_dir, f"news_cache_{category}.json")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('articles', [])
        except Exception:
            return []
        return []
