"""
News provider manager with failover support
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from .gdelt_provider import GdeltNewsProvider
from .guardian_provider import GuardianNewsProvider
from .newsapi_provider import NewsAPIProvider
from .news_providers import NewsProvider
from .logger import get_logger

logger = get_logger(__name__)

class NewsProviderManager:
    """Manages multiple news providers with failover."""
    
    def __init__(self):
        """Initialize the provider manager with all available providers."""
        self.providers = [
            GuardianNewsProvider(),  # Primary provider
            GdeltNewsProvider(),     # First fallback
            NewsAPIProvider()        # Second fallback
        ]
        
        # Track available providers
        self.available_providers = [p for p in self.providers if p.is_available]
        if not self.available_providers:
            logger.error("No news providers are available!")



    def fetch_news(self, category: str = None) -> List[Dict[str, Any]]:
        """Fetch news from providers with automatic fallback.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of news articles from the first successful provider
            
        Raises:
            Exception: If all providers fail
        """
        errors = []

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

        # If all providers fail, raise exception
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
