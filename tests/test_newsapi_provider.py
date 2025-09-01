"""
Tests for NewsAPI provider
"""
import unittest
from unittest.mock import Mock, patch
import json
import requests
from datetime import datetime
from src.core.newsapi_provider import NewsAPIProvider

class TestNewsAPIProvider(unittest.TestCase):
    """Test cases for the NewsAPI provider"""

    def setUp(self):
        """Set up test environment"""
        self.provider = NewsAPIProvider()
        self.test_api_key = "test_key"
        self.provider.api_key = self.test_api_key
        self.provider.is_available = True
        
        self.test_article = {
            "source": {
                "id": "techcrunch",
                "name": "TechCrunch"
            },
            "author": "John Doe",
            "title": "Test Article Title",
            "description": "This is a test article about technology",
            "url": "https://techcrunch.com/2025/09/02/test-article",
            "urlToImage": "https://techcrunch.com/test.jpg",
            "publishedAt": "2025-09-02T12:00:00Z",
            "content": "Full article content here"
        }

    def test_init(self):
        """Test provider initialization"""
        self.assertEqual(self.provider.name, "NewsAPI")
        self.assertTrue(self.provider.is_available)
        self.assertIsNone(self.provider.last_error)
        self.assertEqual(self.provider.base_url, "https://newsapi.org/v2/top-headlines")

    def test_category_mapping(self):
        """Test category mapping"""
        # Test all categories map to valid categories
        valid_categories = {'technology', 'business', 'science', 'sports', 
                          'entertainment', 'general'}
        for newsapi_cat, our_cat in self.provider.category_mapping.items():
            self.assertIn(our_cat, valid_categories)

    @patch('requests.Session')
    def test_make_request(self, mock_session):
        """Test API request making"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'articles': []}
        mock_session.return_value.get.return_value = mock_response
        
        result = self.provider._make_request()
        self.assertEqual(result, {'articles': []})
        
        # Verify API key was used in headers
        called_args = mock_session.return_value.get.call_args
        self.assertIn('X-Api-Key', called_args[1]['headers'])
        self.assertEqual(called_args[1]['headers']['X-Api-Key'], self.test_api_key)

    def test_format_date(self):
        """Test date formatting"""
        test_date = "2025-09-02T12:00:00Z"
        formatted = self.provider._format_date(test_date)
        self.assertEqual(formatted, "2025-09-02T12:00:00Z")
        
        # Test invalid date
        invalid_date = "not a date"
        formatted = self.provider._format_date(invalid_date)
        self.assertTrue(formatted.endswith('Z'))  # Should return current time

    @patch('requests.Session')
    def test_fetch_news(self, mock_session):
        """Test news fetching"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_data = {'articles': [self.test_article]}
        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        
        articles = self.provider.fetch_news('technology')
        self.assertEqual(len(articles), 1)
        article = articles[0]
        
        # Verify article format
        self.assertEqual(article['title'], self.test_article['title'])
        self.assertEqual(article['url'], self.test_article['url'])
        self.assertEqual(article['description'], self.test_article['description'])
        self.assertEqual(article['imageUrl'], self.test_article['urlToImage'])
        self.assertEqual(article['category'], 'technology')
        self.assertEqual(article['source']['name'], 'TechCrunch')
        self.assertEqual(article['author'], 'John Doe')

    @patch('requests.Session')
    def test_error_handling(self, mock_session):
        """Test error handling"""
        # Test network error
        mock_session.return_value.get.side_effect = requests.exceptions.RequestException("Network error")
        with self.assertRaises(requests.exceptions.RequestException):
            self.provider.fetch_news()
        self.assertFalse(self.provider.is_available)
        self.assertIn("Network error", self.provider.last_error)
        
        # Test JSON decode error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "Invalid JSON", 0)
        mock_session.return_value.get.side_effect = None
        mock_session.return_value.get.return_value = mock_response
        
        with self.assertRaises(json.JSONDecodeError):
            self.provider.fetch_news()
        self.assertFalse(self.provider.is_available)

    def test_provider_availability(self):
        """Test provider availability checks"""
        # Test with API key
        self.provider.api_key = "test_key"
        self.assertTrue(self.provider.is_available)
        
        # Test without API key
        self.provider.api_key = ""
        self.provider = NewsAPIProvider()  # Reinitialize to trigger check
        self.assertFalse(self.provider.is_available)
        self.assertIn("API key not found", self.provider.last_error)

    @patch('requests.Session')
    def test_category_filtering(self, mock_session):
        """Test category filtering in requests"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'articles': []}
        mock_session.return_value.get.return_value = mock_response
        
        # Test with technology category
        self.provider.fetch_news('technology')
        called_args = mock_session.return_value.get.call_args
        self.assertIn('category', called_args[1]['params'])
        self.assertEqual(called_args[1]['params']['category'], 'technology')
        
        # Test with unknown category
        self.provider.fetch_news('unknown')
        called_args = mock_session.return_value.get.call_args
        self.assertNotIn('category', called_args[1]['params'])

if __name__ == '__main__':
    unittest.main()
