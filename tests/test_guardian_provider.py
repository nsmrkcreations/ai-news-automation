"""
Tests for The Guardian news provider
"""
import unittest
from unittest.mock import Mock, patch
import json
import requests
from datetime import datetime
from src.core.guardian_provider import GuardianNewsProvider

class TestGuardianProvider(unittest.TestCase):
    """Test cases for The Guardian news provider"""

    def setUp(self):
        """Set up test environment"""
        self.provider = GuardianNewsProvider()
        self.test_api_key = "test_key"
        self.provider.api_key = self.test_api_key
        self.provider.is_available = True
        
        self.test_article = {
            "id": "technology/2025/sep/02/test-article",
            "type": "article",
            "sectionId": "technology",
            "webTitle": "Test Article Title",
            "webUrl": "https://www.theguardian.com/technology/2025/sep/02/test-article",
            "apiUrl": "https://content.guardianapis.com/technology/2025/sep/02/test-article",
            "fields": {
                "headline": "Test Article Title",
                "standfirst": "This is a test article about technology",
                "thumbnail": "https://media.guim.co.uk/test.jpg",
                "lastModified": "2025-09-02T12:00:00Z",
                "body": "Full article content here"
            },
            "tags": [
                {
                    "id": "technology/ai",
                    "type": "keyword",
                    "webTitle": "Artificial intelligence (AI)"
                }
            ]
        }

    def test_init(self):
        """Test provider initialization"""
        self.assertEqual(self.provider.name, "Guardian")
        self.assertTrue(self.provider.is_available)
        self.assertIsNone(self.provider.last_error)
        self.assertEqual(self.provider.base_url, "https://content.guardianapis.com/search")

    def test_section_to_category_mapping(self):
        """Test section to category mapping"""
        # Test all sections map to valid categories
        valid_categories = {'technology', 'business', 'science', 'sports', 
                          'entertainment', 'politics', 'general'}
        for section, category in self.provider.section_to_category.items():
            self.assertIn(category, valid_categories)

    @patch('requests.Session')
    def test_make_request(self, mock_session):
        """Test API request making"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'response': {'results': []}}
        mock_session.return_value.get.return_value = mock_response
        
        result = self.provider._make_request()
        self.assertEqual(result, {'results': []})
        
        # Verify API key was used
        called_args = mock_session.return_value.get.call_args
        self.assertIn('api-key', called_args[1]['params'])
        self.assertEqual(called_args[1]['params']['api-key'], self.test_api_key)

    def test_parse_date(self):
        """Test date parsing"""
        test_date = "2025-09-02T12:00:00Z"
        parsed = self.provider._parse_date(test_date)
        self.assertEqual(parsed, "2025-09-02T12:00:00Z")
        
        # Test invalid date
        invalid_date = "not a date"
        parsed = self.provider._parse_date(invalid_date)
        self.assertTrue(parsed.endswith('Z'))  # Should return current time
        
    def test_determine_category(self):
        """Test category determination"""
        article = self.test_article
        category = self.provider._determine_category(article)
        self.assertEqual(category, 'technology')
        
        # Test fallback when no section matches
        article['sectionId'] = 'nonexistent'
        category = self.provider._determine_category(article)
        self.assertEqual(category, 'general')
        
        # Test empty article
        category = self.provider._determine_category({})
        self.assertEqual(category, 'general')

    @patch('requests.Session')
    def test_fetch_news(self, mock_session):
        """Test news fetching"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_data = {'response': {'results': [self.test_article]}}
        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        
        articles = self.provider.fetch_news()
        self.assertEqual(len(articles), 1)
        article = articles[0]
        
        # Verify article format
        self.assertEqual(article['title'], self.test_article['webTitle'])
        self.assertEqual(article['url'], self.test_article['webUrl'])
        self.assertEqual(article['description'], self.test_article['fields']['standfirst'])
        self.assertEqual(article['imageUrl'], self.test_article['fields']['thumbnail'])
        self.assertEqual(article['category'], 'technology')
        self.assertEqual(article['source']['name'], 'The Guardian')

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
        self.provider = GuardianNewsProvider()  # Reinitialize to trigger check
        self.assertFalse(self.provider.is_available)
        self.assertIn("API key not found", self.provider.last_error)

if __name__ == '__main__':
    unittest.main()
