"""
Rate limiter and cache manager
"""
import time
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
import logging
from threading import Lock

class RateLimiter:
    def __init__(self, calls: int, time_window: int):
        """
        Initialize rate limiter
        Args:
            calls: Number of calls allowed
            time_window: Time window in seconds
        """
        self.calls = calls
        self.time_window = time_window
        self.timestamps = []
        self.lock = Lock()
        
    def try_acquire(self) -> bool:
        """
        Try to acquire a rate limit token
        Returns:
            bool: True if allowed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            
            # Remove timestamps outside the window
            self.timestamps = [ts for ts in self.timestamps if ts > now - self.time_window]
            
            if len(self.timestamps) < self.calls:
                self.timestamps.append(now)
                return True
                
            return False
            
    def wait_if_needed(self) -> float:
        """
        Wait if rate limit is exceeded
        Returns:
            float: Time waited in seconds
        """
        while not self.try_acquire():
            time.sleep(1)
        return 0.0

class EnhancedCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Any] = {}
        self.default_expiry = timedelta(hours=1)
        self.lock = Lock()
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache
        """
        # Try memory cache first
        with self.lock:
            if key in self.memory_cache:
                data = self.memory_cache[key]
                if datetime.now() < data['expiry']:
                    return data['value']
                else:
                    del self.memory_cache[key]
        
        # Try file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data['expiry']) > datetime.now():
                        # Update memory cache
                        self.memory_cache[key] = {
                            'value': data['value'],
                            'expiry': datetime.fromisoformat(data['expiry'])
                        }
                        return data['value']
                    else:
                        os.remove(cache_file)
        except Exception as e:
            logging.error(f"Cache read error for {key}: {str(e)}")
        
        return None
        
    def set(self, key: str, value: Any, expiry: Optional[timedelta] = None):
        """
        Set item in cache
        """
        expiry_time = datetime.now() + (expiry or self.default_expiry)
        
        # Update memory cache
        with self.lock:
            self.memory_cache[key] = {
                'value': value,
                'expiry': expiry_time
            }
        
        # Update file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'value': value,
                    'expiry': expiry_time.isoformat()
                }, f)
        except Exception as e:
            logging.error(f"Cache write error for {key}: {str(e)}")
            
    def clear_expired(self):
        """
        Clear expired items from cache
        """
        # Clear memory cache
        with self.lock:
            now = datetime.now()
            expired_keys = [
                key for key, data in self.memory_cache.items()
                if data['expiry'] < now
            ]
            for key in expired_keys:
                del self.memory_cache[key]
        
        # Clear file cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if datetime.fromisoformat(data['expiry']) < now:
                            os.remove(filepath)
                except Exception as e:
                    logging.error(f"Error clearing cache file {filename}: {str(e)}")
                    
    def get_cache_size(self) -> Dict[str, int]:
        """
        Get cache size information
        """
        memory_size = len(self.memory_cache)
        file_size = len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        
        return {
            'memory_items': memory_size,
            'file_items': file_size
        }
