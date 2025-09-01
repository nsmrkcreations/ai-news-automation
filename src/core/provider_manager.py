"""
News provider manager with caching and fallback support
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dateutil.parser import parse as parse_date
from .gdelt_provider import GdeltNewsProvider
from .guardian_provider import GuardianNewsProvider
from .newsapi_provider import NewsAPIProvider
from .news_providers import NewsProvider
from .logger import get_logger

logger = get_logger(__name__)

class NewsProviderManager:
    """Manages multiple news providers with caching and failover."""
    
    def __init__(self, use_cache: bool = True):
        """Initialize the provider manager with all available providers.
        
        Args:
            use_cache: Whether to use cache for news articles
        """
        self.providers = [
            GuardianNewsProvider(),  # Primary provider
            GdeltNewsProvider(),     # First fallback
            NewsAPIProvider()        # Second fallback
        ]
        
        self.use_cache = use_cache
        
        # Create cache directory
        self.cache_dir = Path("cache")
        if use_cache:
            self.cache_dir.mkdir(exist_ok=True)
        
        # Track available providers
        self.available_providers = [p for p in self.providers if p.is_available]
        if not self.available_providers:
            logger.error("No news providers are available!")

    def _get_cache_file(self, category: str) -> Path:
        """Get the cache file path for a category.
        
        Args:
            category: News category or None for general
            
        Returns:
            Path object for the cache file
        """
        return self.cache_dir / f"news_cache_{category or 'general'}.json"

    def _save_to_cache(self, articles: List[Dict[str, Any]], category: str):
        """Save articles to cache.
        
        Args:
            articles: List of articles to cache
            category: News category or None for general
        """
        cache_file = self._get_cache_file(category)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")

    def _load_from_cache(self, category: str, ignore_age: bool = False) -> List[Dict[str, Any]]:
        """Load articles from cache if available and not too old.
        
        Args:
            category: News category or None for general
            ignore_age: If True, return cached data regardless of age
            
        Returns:
            List of cached articles, or empty list if cache is invalid/old
        """
        cache_file = self._get_cache_file(category)
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                if articles and len(articles) > 0:
                    # Add fetchedAt if missing
                    if 'fetchedAt' not in articles[0]:
                        current_time = datetime.now().isoformat()
                        for article in articles:
                            article['fetchedAt'] = current_time
                    
                    # Check cache age unless explicitly ignored
                    if ignore_age or datetime.now() - parse_date(articles[0]['fetchedAt']) < timedelta(hours=1):
                        return articles
        except Exception as e:
            logger.error(f"Error loading from cache: {str(e)}")
        return []

    def fetch_news(self, category: str = None) -> List[Dict[str, Any]]:
        """Fetch news from providers with automatic fallback.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of news articles from the first successful provider,
            or cached articles if all providers fail
            
        Raises:
            Exception: If all providers fail and no cached data is available
        """
        errors = []

        # First check cache if enabled
        if self.use_cache:
            cached_articles = self._load_from_cache(category)
            if cached_articles:
                logger.info("Returning cached articles")
                return cached_articles

        # Try each provider in order with health tracking
        for provider in self.available_providers:
            try:
                logger.info(f"Attempting to fetch news from {provider.name}")
                
                # Add timeout for provider requests
                articles = provider.fetch_news(category)
                
                if articles:
                    # Track successful request
                    provider.track_request(True)
                    
                    logger.info(f"Successfully fetched {len(articles)} articles from {provider.name}")
                    
                    # Process categories and add AI enhancement flag for each article
                    from .category_analyzer import CategoryAnalyzer
                    for article in articles:
                        # Let CategoryAnalyzer determine the best category
                        article['category'] = CategoryAnalyzer.get_category(article)
                        
                        # Check if article was AI-enhanced
                        if article.get('aiEnhanced'):
                            # Add 🤖 prefix to title (ensure proper encoding in JSON)
                            article['title'] = f"🤖 {article['title']}"
                            # Add badge for frontend display
                            article['aiBadge'] = {
                                'text': 'AI Enhanced',
                                'icon': '🤖',
                                'tooltip': 'This article was enhanced using AI'
                            }
                        
                        # For debugging, get confidence scores
                        if logger.isEnabledFor(logging.DEBUG):
                            scores = CategoryAnalyzer.get_confidence_scores(article)
                            logger.debug(f"Category confidence scores for '{article['title'][:50]}...': {scores}")
                    
                    # Log article statistics
                    category_counts = {}
                    videos = 0
                    for article in articles:
                        category_counts[article['category']] = category_counts.get(article['category'], 0) + 1
                        if article.get('hasVideo', False):
                            videos += 1
                    
                    logger.info(f"Category distribution: {category_counts}")
                    if videos > 0:
                        logger.info(f"Found {videos} articles with video content from {provider.name}")
                    
                    # Log provider health
                    health = provider.get_health_metrics()
                    logger.info(f"Provider {provider.name} health metrics: Success rate={health['successRate']}%, "
                              f"Total requests={health['totalRequests']}")
                    
                    # Save to cache if enabled
                    if self.use_cache:
                        self._save_to_cache(articles, category)
                    return articles
                    
                logger.warning(f"No articles returned from {provider.name}")
                provider.track_request(False)
                
            except Exception as e:
                error_msg = f"{provider.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error fetching from {provider.name}: {str(e)}")
                
                # Track failed request and mark provider as unavailable
                provider.track_request(False)
                provider.mark_unavailable(str(e))
                
                # Check if we should temporarily disable the provider
                health = provider.get_health_metrics()
                if health['consecutiveFailures'] >= 3:  # Disable after 3 consecutive failures
                    logger.warning(f"Provider {provider.name} disabled due to multiple consecutive failures")
                    provider.is_available = False  # Explicitly disable the provider
                    self.available_providers = [p for p in self.providers if p.is_available]
                    continue
                
            finally:
                # Log provider status and health
                health = provider.get_health_metrics()
                logger.info(f"Provider {provider.name} status: " + 
                          f"{'Available' if provider.is_available else 'Unavailable'}, " +
                          f"Success rate: {health['successRate']}%")

        # If all providers fail, fall back to cache regardless of age
        cached_data = self._load_from_cache(category, ignore_age=True)
        if cached_data:
            logger.info("All providers failed, using cached data")
            return cached_data
            
        # If no cache available, then error out
        error_msg = "All news providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        raise Exception(error_msg)

    def reset_providers(self):
        """Reset all providers to available state."""
        for provider in self.providers:
            provider.mark_available()
        self.available_providers = [p for p in self.providers if p.is_available]

    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get the status of all providers.
        
        Returns:
            List of provider status dictionaries with detailed health information
        """
        statuses = []
        for idx, provider in enumerate(self.providers):
            status = {
                'name': provider.name,
                'available': provider.is_available,
                'error': provider.last_error,
                'priority': idx + 1,  # Priority order (1=highest)
                'isPrimary': idx == 0,
                'lastSuccessfulFetch': getattr(provider, 'last_successful_fetch', None),
                'failureCount': getattr(provider, 'failure_count', 0),
                'lastError': provider.last_error
            }
            statuses.append(status)
            
        return statuses
        
    def get_healthy_provider(self) -> Optional[NewsProvider]:
        """Get the first available healthy provider.
        
        Returns:
            The first available provider or None if all are unavailable
        """
        for provider in self.providers:
            if provider.is_available:
                return provider
        return None
