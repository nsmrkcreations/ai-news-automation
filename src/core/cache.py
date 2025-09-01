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

class CacheManager(Cache):
    """Alias for Cache class for backward compatibility"""
    pass

class EnhancedCache(Cache):
    """Enhanced cache with additional features"""
    def __init__(self, cache_dir: str = "cache"):
        super().__init__(cache_dir)
        self.stats = {'hits': 0, 'misses': 0}
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return self.stats
    
    def clear_cache(self):
        """Clear all cache files and reset statistics"""
        import glob
        
        try:
            # Clear all cache files
            cache_files = glob.glob(os.path.join(self.cache_dir, "news_cache_*.json"))
            for f in cache_files:
                try:
                    os.remove(f)
                except OSError as e:
                    print(f"Error removing {f}: {e}")
                    
            # Reset stats
            self.stats = {'hits': 0, 'misses': 0}
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
