import unittest
from unittest.mock import patch, MagicMock
from src.core.provider_manager import NewsProviderManager
from src.core.guardian_provider import GuardianNewsProvider
from src.core.gdelt_provider import GdeltNewsProvider
from src.core.newsapi_provider import NewsAPIProvider

class TestFailover(unittest.TestCase):
    """Test the failover mechanism between news providers."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = NewsProviderManager(use_cache=False)  # Disable cache for tests
        
        # Create sample news data
        self.guardian_news = [{'title': 'Guardian News', 'source': {'name': 'The Guardian'}}]
        self.gdelt_news = [{'title': 'GDELT News', 'source': {'name': 'GDELT'}}]
        self.newsapi_news = [{'title': 'NewsAPI News', 'source': {'name': 'NewsAPI'}}]

    def test_normal_operation_uses_guardian(self):
        """Test that Guardian is used as primary source when working."""
        with patch.object(GuardianNewsProvider, 'fetch_news', return_value=self.guardian_news):
            news = self.manager.fetch_news()
            self.assertEqual(news[0]['source']['name'], 'The Guardian')

    def test_failover_to_gdelt_when_guardian_fails(self):
        """Test failover to GDELT when Guardian fails."""
        with patch.object(GuardianNewsProvider, 'fetch_news', side_effect=Exception('Guardian API error')), \
             patch.object(GdeltNewsProvider, 'fetch_news', return_value=self.gdelt_news):
            news = self.manager.fetch_news()
            self.assertEqual(news[0]['source']['name'], 'GDELT')

    def test_failover_to_newsapi_when_both_fail(self):
        """Test failover to NewsAPI when both Guardian and GDELT fail."""
        with patch.object(GuardianNewsProvider, 'fetch_news', side_effect=Exception('Guardian error')), \
             patch.object(GdeltNewsProvider, 'fetch_news', side_effect=Exception('GDELT error')), \
             patch.object(NewsAPIProvider, 'fetch_news', return_value=self.newsapi_news):
            news = self.manager.fetch_news()
            self.assertEqual(news[0]['source']['name'], 'NewsAPI')

    def test_provider_health_tracking(self):
        """Test that provider health is tracked correctly during failover."""
        guardian_provider = self.manager.providers[0]
        gdelt_provider = self.manager.providers[1]
        
        # Simulate Guardian failure
        with patch.object(GuardianNewsProvider, 'fetch_news', side_effect=Exception('Guardian error')), \
             patch.object(GdeltNewsProvider, 'fetch_news', return_value=self.gdelt_news):
            self.manager.fetch_news()
            
            # Check Guardian health metrics
            guardian_health = guardian_provider.get_health_metrics()
            self.assertFalse(guardian_provider.is_available)
            self.assertEqual(guardian_health['failureCount'], 1)
            
            # Check GDELT health metrics
            gdelt_health = gdelt_provider.get_health_metrics()
            self.assertTrue(gdelt_provider.is_available)
            self.assertEqual(gdelt_health['successfulRequests'], 1)

    def test_provider_recovery(self):
        """Test that failed provider can recover and be used again."""
        guardian_provider = self.manager.providers[0]
        
        # First request fails
        with patch.object(GuardianNewsProvider, 'fetch_news', side_effect=Exception('Guardian error')), \
             patch.object(GdeltNewsProvider, 'fetch_news', return_value=self.gdelt_news):
            self.manager.fetch_news()
            self.assertFalse(guardian_provider.is_available)
        
        # Reset provider
        guardian_provider.mark_available()
        
        # Second request succeeds
        with patch.object(GuardianNewsProvider, 'fetch_news', return_value=self.guardian_news):
            news = self.manager.fetch_news()
            self.assertTrue(guardian_provider.is_available)
            self.assertEqual(news[0]['source']['name'], 'The Guardian')

    def test_consecutive_failures_handling(self):
        """Test that provider is disabled after multiple consecutive failures."""
        guardian_provider = self.manager.providers[0]
        
        # Simulate 3 consecutive failures
        with patch.object(GuardianNewsProvider, 'fetch_news', side_effect=Exception('Guardian error')), \
             patch.object(GdeltNewsProvider, 'fetch_news', return_value=self.gdelt_news):
            for _ in range(3):
                self.manager.fetch_news()
            
            # Check Guardian health metrics
            guardian_health = guardian_provider.get_health_metrics()
            self.assertFalse(guardian_provider.is_available)
            self.assertEqual(guardian_health['consecutiveFailures'], 3)
            self.assertEqual(guardian_health['failureCount'], 3)

    def test_cache_fallback_when_all_providers_fail(self):
        """Test that system falls back to cache when all providers fail."""
        # First, make a successful request to populate cache
        with patch.object(GuardianNewsProvider, 'fetch_news', return_value=self.guardian_news):
            self.manager.fetch_news()
        
        # Then make all providers fail
        with patch.object(GuardianNewsProvider, 'fetch_news', side_effect=Exception('Guardian error')), \
             patch.object(GdeltNewsProvider, 'fetch_news', side_effect=Exception('GDELT error')), \
             patch.object(NewsAPIProvider, 'fetch_news', side_effect=Exception('NewsAPI error')):
            try:
                news = self.manager.fetch_news()
                self.assertEqual(news[0]['source']['name'], 'The Guardian')  # Should get cached Guardian news
            except Exception as e:
                self.fail(f"Should not raise exception when cache is available: {str(e)}")

if __name__ == '__main__':
    unittest.main()
