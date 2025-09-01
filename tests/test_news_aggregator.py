"""
Tests for the news aggregator
"""
import unittest
from unittest.mock import Mock, patch
import requests
from src.core.news_aggregator import NewsAggregator
from src.core.gdelt_provider import GdeltNewsProvider
from src.core.guardian_provider import GuardianNewsProvider
from src.core.newsapi_provider import NewsAPIProvider

class TestNewsAggregator(unittest.TestCase):
    """Test cases for the news aggregator"""

    def setUp(self):
        """Set up test environment"""
        self.aggregator = NewsAggregator()
        self.test_article = {
            'title': 'Test Article',
            'description': 'Test Description',
            'url': 'https://example.com/article',
            'publishedAt': '2025-09-02T12:00:00Z',
            'source': {'name': 'Test Source'},
            'category': 'technology'
        }

    def test_init(self):
        """Test aggregator initialization"""
        self.assertEqual(len(self.aggregator.providers), 3)
        self.assertIsInstance(self.aggregator.providers[0], GdeltNewsProvider)
        self.assertIsInstance(self.aggregator.providers[1], GuardianNewsProvider)
        self.assertIsInstance(self.aggregator.providers[2], NewsAPIProvider)

    def test_get_categories(self):
        """Test getting supported categories"""
        categories = self.aggregator.get_categories()
        self.assertIsInstance(categories, list)
        self.assertTrue(len(categories) > 0)
        self.assertIn('technology', categories)
        self.assertIn('business', categories)

    def test_provider_status(self):
        """Test getting provider status"""
        status = self.aggregator.get_provider_status()
        self.assertEqual(len(status), 3)
        for provider_status in status:
            self.assertIn('name', provider_status)
            self.assertIn('available', provider_status)
            self.assertIn('error', provider_status)

    @patch('src.core.gdelt_provider.GdeltNewsProvider.fetch_news')
    def test_primary_provider_success(self, mock_fetch):
        """Test successful fetch from primary provider"""
        mock_fetch.return_value = [self.test_article]
        
        news = self.aggregator.fetch_news('technology')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['title'], self.test_article['title'])
        
        # Should not try other providers
        self.assertEqual(mock_fetch.call_count, 1)

    @patch('src.core.gdelt_provider.GdeltNewsProvider.fetch_news')
    @patch('src.core.guardian_provider.GuardianNewsProvider.fetch_news')
    def test_fallback_to_guardian(self, mock_guardian_fetch, mock_gdelt_fetch):
        """Test fallback to Guardian when GDELT fails"""
        # Make GDELT fail
        mock_gdelt_fetch.side_effect = requests.exceptions.RequestException("Network error")
        
        # Make Guardian succeed
        mock_guardian_fetch.return_value = [self.test_article]
        
        news = self.aggregator.fetch_news('technology')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['title'], self.test_article['title'])
        
        # Verify both providers were tried
        mock_gdelt_fetch.assert_called_once()
        mock_guardian_fetch.assert_called_once()

    @patch('src.core.gdelt_provider.GdeltNewsProvider.fetch_news')
    @patch('src.core.guardian_provider.GuardianNewsProvider.fetch_news')
    @patch('src.core.newsapi_provider.NewsAPIProvider.fetch_news')
    def test_fallback_to_newsapi(self, mock_newsapi_fetch, mock_guardian_fetch, mock_gdelt_fetch):
        """Test fallback to NewsAPI when both GDELT and Guardian fail"""
        # Make GDELT and Guardian fail
        mock_gdelt_fetch.side_effect = requests.exceptions.RequestException("Network error")
        mock_guardian_fetch.side_effect = requests.exceptions.RequestException("API error")
        
        # Make NewsAPI succeed
        mock_newsapi_fetch.return_value = [self.test_article]
        
        news = self.aggregator.fetch_news('technology')
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['title'], self.test_article['title'])
        
        # Verify all providers were tried
        mock_gdelt_fetch.assert_called_once()
        mock_guardian_fetch.assert_called_once()
        mock_newsapi_fetch.assert_called_once()

    @patch('src.core.gdelt_provider.GdeltNewsProvider.fetch_news')
    @patch('src.core.guardian_provider.GuardianNewsProvider.fetch_news')
    @patch('src.core.newsapi_provider.NewsAPIProvider.fetch_news')
    def test_all_providers_fail(self, mock_newsapi_fetch, mock_guardian_fetch, mock_gdelt_fetch):
        """Test handling when all providers fail"""
        # Make all providers fail
        mock_gdelt_fetch.side_effect = requests.exceptions.RequestException("GDELT error")
        mock_guardian_fetch.side_effect = requests.exceptions.RequestException("Guardian error")
        mock_newsapi_fetch.side_effect = requests.exceptions.RequestException("NewsAPI error")
        
        with self.assertRaises(Exception) as context:
            self.aggregator.fetch_news('technology')
            
        self.assertIn("All news providers failed", str(context.exception))
        self.assertIn("GDELT error", str(context.exception))
        self.assertIn("Guardian error", str(context.exception))
        self.assertIn("NewsAPI error", str(context.exception))

    def test_reset_providers(self):
        """Test resetting providers"""
        # Mark all providers as unavailable
        for provider in self.aggregator.providers:
            provider.mark_unavailable("Test error")
            
        # Reset providers
        self.aggregator.reset_providers()
        
        # Verify all providers are available
        for provider in self.aggregator.providers:
            self.assertTrue(provider.is_available)
            self.assertIsNone(provider.last_error)

    def test_max_articles_limit(self):
        """Test max articles limit"""
        # Create test articles
        many_articles = [
            {**self.test_article, 'title': f'Article {i}'}
            for i in range(100)
        ]
        
        with patch('src.core.gdelt_provider.GdeltNewsProvider.fetch_news') as mock_fetch:
            mock_fetch.return_value = many_articles
            
            # Test default limit
            news = self.aggregator.fetch_news('technology')
            self.assertEqual(len(news), 50)  # Default max_articles
            
            # Test custom limit
            news = self.aggregator.fetch_news('technology', max_articles=10)
            self.assertEqual(len(news), 10)

if __name__ == '__main__':
    unittest.main()
