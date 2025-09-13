"""
News aggregator with failover support.
"""
import logging
from typing import List, Dict, Any
from .gdelt_provider import GdeltNewsProvider
from .guardian_provider import GuardianNewsProvider
from .newsapi_provider import NewsAPIProvider
from .logger import get_logger

logger = get_logger(__name__)

class NewsAggregator:
    """Aggregates news from multiple providers with failover support."""
    
    def __init__(self):
        """Initialize the news aggregator with all providers."""
        self.providers = [
           
            GuardianNewsProvider(),   # Primary provider
            GdeltNewsProvider(),      # First fallback
            NewsAPIProvider()         # Second fallback
        ]
        
        # Track which providers are available
        self.available_providers = [p for p in self.providers if p.is_available]
        if not self.available_providers:
            logger.error("No news providers are available!")

    def fetch_news(self, category: str = None, max_articles: int = 50) -> List[Dict[str, Any]]:
        """Fetch news using available providers with failover.
        
        Args:
            category: Optional category to filter by
            max_articles: Maximum number of articles to return
            
        Returns:
            List of news articles from the first successful provider
            
        Raises:
            Exception: If no providers are available or all providers fail
        """
        if not self.available_providers:
            raise Exception("No news providers are available")
            
        errors = []
        for provider in self.available_providers:
            try:
                logger.info(f"Attempting to fetch news from {provider.name}")
                articles = provider.fetch_news(category)
                
                if articles:
                    logger.info(f"Successfully fetched {len(articles)} articles from {provider.name}")
                    # Sort by date and limit to max_articles
                    articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
                    return articles[:max_articles]
                else:
                    logger.warning(f"No articles returned from {provider.name}, trying next provider")
                    
            except Exception as e:
                logger.error(f"Error fetching news from {provider.name}: {e}")
                errors.append(f"{provider.name}: {str(e)}")
                continue
                
        # If we get here, all providers failed
        error_msg = "All news providers failed: " + "; ".join(errors)
        logger.error(error_msg)
        raise Exception(error_msg)

    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get the status of all providers.
        
        Returns:
            List of provider status dictionaries
        """
        return [{
            'name': provider.name,
            'available': provider.is_available,
            'error': provider.last_error
        } for provider in self.providers]

    def reset_providers(self):
        """Reset all providers to available state."""
        for provider in self.providers:
            provider.mark_available()
        self.available_providers = [p for p in self.providers if p.is_available]

    def get_categories(self) -> List[str]:
        """Get list of supported news categories.
        
        Returns:
            List of category strings
        """
        return [
            'technology',
            'business',
            'science',
            'sports',
            'entertainment',
            'politics',
            'markets',
            'general'
        ]
