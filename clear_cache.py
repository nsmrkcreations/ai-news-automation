"""
Utility script to clear the news cache
"""
import os
import sys
import logging
from src.core.cache import EnhancedCache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_cache():
    """Clear all news cache files"""
    try:
        cache = EnhancedCache()
        
        # Get count of cache files before clearing
        cache_files = [f for f in os.listdir(cache.cache_dir) if f.startswith('news_cache_')]
        initial_count = len(cache_files)
        
        if initial_count == 0:
            logger.info("Cache is already empty")
            return True
            
        # Clear the cache
        if cache.clear_cache():
            logger.info(f"Successfully cleared {initial_count} cache files")
            return True
        else:
            logger.error("Failed to clear cache")
            return False
            
    except Exception as e:
        logger.error(f"Error while clearing cache: {e}")
        return False

if __name__ == "__main__":
    try:
        if clear_cache():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
