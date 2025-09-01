"""
Test rate limiting and caching functionality
"""
import time
import os
from core.rate_limiter import RateLimiter, EnhancedCache
from core.config import Config
from dotenv import load_dotenv

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("Testing rate limiting...")
    
    # Create rate limiter (5 calls per 10 seconds)
    limiter = RateLimiter(calls=5, time_window=10)
    
    # Make several calls
    for i in range(7):
        if limiter.try_acquire():
            print(f"Call {i+1}: Allowed")
        else:
            print(f"Call {i+1}: Rate limited")
        time.sleep(1)
    
    print("\nWaiting for rate limit window to reset...")
    time.sleep(10)
    
    # Try again after window reset
    if limiter.try_acquire():
        print("Call after reset: Allowed")
    else:
        print("Call after reset: Rate limited")

def test_caching():
    """Test enhanced caching functionality"""
    print("\nTesting caching...")
    
    # Create cache
    cache = EnhancedCache(cache_dir="test_cache")
    
    # Test setting and getting
    print("Setting test value...")
    cache.set("test_key", {"data": "test_value"})
    
    # Get from cache
    value = cache.get("test_key")
    print(f"Retrieved value: {value}")
    
    # Test expiration
    print("\nTesting cache expiration...")
    from datetime import timedelta
    cache.set("expire_key", {"data": "expire_value"}, expiry=timedelta(seconds=2))
    
    print("Value before expiration:", cache.get("expire_key"))
    time.sleep(3)
    print("Value after expiration:", cache.get("expire_key"))
    
    # Get cache stats
    stats = cache.get_cache_size()
    print(f"\nCache stats: {stats}")
    
    # Clean up test cache
    import shutil
    if os.path.exists("test_cache"):
        shutil.rmtree("test_cache")

if __name__ == "__main__":
    load_dotenv()
    test_rate_limiting()
    test_caching()
