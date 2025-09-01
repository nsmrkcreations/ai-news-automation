"""Base class for news providers with common functionality."""
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)

class NewsProvider(ABC):
    """Abstract base class for news providers."""

    def __init__(self, name: str = "Base Provider"):
        """Initialize the news provider.
        
        Args:
            name: Name of the provider
        """
        self.name = name
        self.is_available = True
        self.last_error = None
        
        # Health tracking
        self.last_successful_fetch = None
        self.failure_count = 0
        self.consecutive_failures = 0
        self.total_requests = 0
        self.successful_requests = 0

    @abstractmethod
    def fetch_news(self, category: str = None) -> List[Dict[str, Any]]:
        """Fetch news articles.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of news articles
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement fetch_news")

    def mark_available(self):
        """Mark the provider as available and reset failure counters."""
        self.is_available = True
        self.last_error = None
        self.consecutive_failures = 0
        logger.info(f"{self.name} marked as available")
        
    def mark_unavailable(self, error: str):
        """Mark the provider as unavailable and update failure metrics.
        
        Args:
            error: Error message explaining why provider is unavailable
        """
        self.is_available = False
        self.last_error = error
        self.failure_count += 1
        self.consecutive_failures += 1
        logger.error(f"{self.name} marked as unavailable: {error}")
        
    def track_request(self, success: bool):
        """Track a request's success/failure for health monitoring.
        
        Args:
            success: Whether the request was successful
        """
        self.total_requests += 1
        if success:
            from datetime import datetime
            self.successful_requests += 1
            self.last_successful_fetch = datetime.now().isoformat()
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get detailed health metrics for the provider.
        
        Returns:
            Dictionary containing health metrics
        """
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        return {
            'name': self.name,
            'available': self.is_available,
            'lastError': self.last_error,
            'lastSuccessfulFetch': self.last_successful_fetch,
            'failureCount': self.failure_count,
            'consecutiveFailures': self.consecutive_failures,
            'totalRequests': self.total_requests,
            'successfulRequests': self.successful_requests,
            'successRate': round(success_rate, 2)
        }
