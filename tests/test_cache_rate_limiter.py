"""
Tests for Cache and Rate Limiter components
"""
import pytest
import time
from datetime import datetime, timedelta
from src.core.rate_limiter import RateLimiter, EnhancedCache
from tests.test_utils import create_test_dataset, test_cache_dir

class TestRateLimiter:
    def test_rate_limiting_basic(self):
        """Test basic rate limiting functionality"""
        limiter = RateLimiter(calls=3, time_window=1)
        
        # Should allow 3 calls
        assert limiter.try_acquire()
        assert limiter.try_acquire()
        assert limiter.try_acquire()
        
        # Should deny 4th call
        assert not limiter.try_acquire()

    def test_rate_limiting_window(self):
        """Test rate limit window functionality"""
        limiter = RateLimiter(calls=2, time_window=1)
        
        # Use up rate limit
        assert limiter.try_acquire()
        assert limiter.try_acquire()
        assert not limiter.try_acquire()
        
        # Wait for window to reset
        time.sleep(1.1)
        assert limiter.try_acquire()

    def test_concurrent_access(self):
        """Test rate limiting under concurrent access"""
        import threading
        
        limiter = RateLimiter(calls=3, time_window=1)
        results = []
        
        def try_acquire():
            results.append(limiter.try_acquire())
        
        # Create and start threads
        threads = [threading.Thread(target=try_acquire) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Should have exactly 3 successes
        assert sum(results) == 3

    def test_wait_if_needed(self):
        """Test wait_if_needed functionality"""
        limiter = RateLimiter(calls=2, time_window=1)
        
        # Use up rate limit
        assert limiter.try_acquire()
        assert limiter.try_acquire()
        
        # Measure wait time
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        assert elapsed >= 1.0

class TestEnhancedCache:
    def test_basic_cache_operations(self, test_cache_dir):
        """Test basic cache set/get operations"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Test setting and getting
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        
        # Test non-existent key
        assert cache.get('non_existent') is None

    def test_cache_expiry(self, test_cache_dir):
        """Test cache expiration"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Set with short expiry
        cache.set('expire_key', 'expire_value', expiry=timedelta(seconds=1))
        assert cache.get('expire_key') == 'expire_value'
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get('expire_key') is None

    def test_memory_cache(self, test_cache_dir):
        """Test memory cache functionality"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Set value
        cache.set('memory_key', 'memory_value')
        
        # Should be in memory cache
        assert 'memory_key' in cache.memory_cache
        assert cache.memory_cache['memory_key']['value'] == 'memory_value'

    def test_file_persistence(self, test_cache_dir):
        """Test file persistence"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Set value
        test_data = {'key': 'value'}
        cache.set('file_key', test_data)
        
        # Create new cache instance (clear memory cache)
        new_cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Should still be able to get value
        assert new_cache.get('file_key') == test_data

    def test_clear_expired(self, test_cache_dir):
        """Test clearing expired entries"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Set some values with different expiry times
        cache.set('expire1', 'value1', expiry=timedelta(seconds=1))
        cache.set('expire2', 'value2', expiry=timedelta(hours=1))
        
        # Wait for first to expire
        time.sleep(1.1)
        cache.clear_expired()
        
        assert cache.get('expire1') is None
        assert cache.get('expire2') == 'value2'

    def test_cache_size(self, test_cache_dir):
        """Test cache size reporting"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Add some items
        for i in range(5):
            cache.set(f'key{i}', f'value{i}')
        
        stats = cache.get_cache_size()
        assert stats['memory_items'] == 5
        assert stats['file_items'] == 5

    def test_complex_data_types(self, test_cache_dir):
        """Test caching complex data types"""
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        # Test with different data types
        test_cases = [
            ('list', [1, 2, 3]),
            ('dict', {'a': 1, 'b': 2}),
            ('nested', {'a': [1, 2, {'b': 3}]}),
            ('datetime', datetime.now()),
            ('none', None)
        ]
        
        for key, value in test_cases:
            cache.set(key, value)
            retrieved = cache.get(key)
            if isinstance(value, datetime):
                # Compare string representations for datetime
                assert str(retrieved) == str(value)
            else:
                assert retrieved == value

    def test_concurrent_access(self, test_cache_dir):
        """Test concurrent cache access"""
        import threading
        
        cache = EnhancedCache(cache_dir=test_cache_dir)
        
        def cache_operation(id):
            cache.set(f'key{id}', f'value{id}')
            assert cache.get(f'key{id}') == f'value{id}'
        
        threads = [
            threading.Thread(target=cache_operation, args=(i,))
            for i in range(10)
        ]
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verify all values were stored correctly
        for i in range(10):
            assert cache.get(f'key{i}') == f'value{i}'
