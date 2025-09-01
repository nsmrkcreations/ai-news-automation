"""
Test suite for the GDELT news provider
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import json
import requests
from src.core.gdelt_provider import GdeltNewsProvider

class TestGdeltProvider(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.provider = GdeltNewsProvider()
        self.test_article = {
            'title': 'Test Article Title',
            'seendescription': 'This is a test article about technology and AI.',
            'url': 'https://example.com/article',
            'socialimage': 'https://example.com/image.jpg',
            'seendate': '2025-09-01T12:00:00Z',
            'domain': 'techcrunch.com',
            'tone': 2.5,
            'themes': ['TECH', 'TECH_AI'],
            'locations': ['San Francisco', 'San Francisco'],  # Duplicate for testing deduplication
            'persons': ['John Doe'],
            'organizations': ['Tech Corp'],
            'seentext': 'Full article text about technology and artificial intelligence.'
        }

    def test_init(self):
        """Test provider initialization"""
        self.assertEqual(self.provider.name, "GDELT")
        self.assertTrue(self.provider.is_available)
        self.assertIsNone(self.provider.last_error)
        self.assertEqual(self.provider.base_url, "https://api.gdeltproject.org/api/v2/doc/doc")

    def test_theme_to_category_mapping(self):
        """Test theme to category mapping is complete"""
        # Test all themes map to valid categories
        valid_categories = {'technology', 'business', 'science', 'sports', 
                          'entertainment', 'politics', 'general'}
        for theme, category in self.provider.theme_to_category.items():
            self.assertIn(category, valid_categories)

    def test_determine_category_from_themes(self):
        """Test category determination from GDELT themes"""
        category = self.provider._determine_category(self.test_article)
        self.assertEqual(category, 'technology')  # Should match TECH theme

    def test_determine_category_from_domain(self):
        """Test category determination from domain"""
        test_article = self.test_article.copy()
        test_article['themes'] = []  # Remove themes
        category = self.provider._determine_category(test_article)
        self.assertEqual(category, 'technology')  # Should match techcrunch.com domain

    def test_determine_category_from_content(self):
        """Test category determination from content analysis"""
        test_article = self.test_article.copy()
        test_article['themes'] = []
        test_article['domain'] = 'example.com'  # Use neutral domain
        category = self.provider._determine_category(test_article)
        self.assertEqual(category, 'technology')  # Should match tech keywords in content

    def test_determine_category_fallback(self):
        """Test category fallback when no clear category"""
        empty_article = {
            'title': 'Generic Title',
            'description': 'Generic description',
            'url': 'https://example.com'
        }
        category = self.provider._determine_category(empty_article, default_category='test')
        self.assertEqual(category, 'test')  # Should use default category
        category = self.provider._determine_category(empty_article)
        self.assertEqual(category, 'general')  # Should use 'general' if no default

    @patch('requests.Session')
    def test_process_article_dates(self, mock_session):
        """Test different date formats processing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response
        
        # Set up a complete test article
        base_article = {
            'title': 'Test Title',
            'url': 'http://example.com/article',
            'domain': 'example.com',
            'socialimage': 'http://example.com/image.jpg',
            'description': 'Test description'
        }
        
        # Test ISO format
        test_article = base_article.copy()
        test_article['seendate'] = '2025-09-01T12:00:00Z'
        mock_data = {'articles': [test_article]}
        mock_response.json.return_value = mock_data
        mock_response.text = json.dumps(mock_data)
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertIn('publishedAt', news[0])
        
        # Test Unix timestamp
        test_article = base_article.copy()
        test_article['seendate'] = 1735689600  # 2025-01-01
        mock_data = {'articles': [test_article]}
        mock_response.json.return_value = mock_data
        mock_response.text = json.dumps(mock_data)
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertIn('publishedAt', news[0])
        
        # Test invalid date
        test_article = base_article.copy()
        test_article['seendate'] = 'invalid'
        mock_data = {'articles': [test_article]}
        mock_response.json.return_value = mock_data
        mock_response.text = json.dumps(mock_data)
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertIn('publishedAt', news[0])

    @patch('requests.Session')
    def test_api_request_retry(self, mock_session):
        """Test API request retry mechanism"""
        # Set up session mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'articles': []}
        mock_response.text = json.dumps({'articles': []})
        mock_response.url = 'http://test.com'
        mock_session.return_value.get.return_value = mock_response
        
        # Make request and verify retry behavior
        test_query = "test query"
        self.provider._make_request(test_query)
        
        # Verify request was made
        mock_session.return_value.get.assert_called()
        
        # Verify retries are configured
        adapter = mock_session.return_value.mount.call_args_list[0][0][1]
        self.assertEqual(adapter.max_retries.total, 3)
        self.assertEqual(adapter.max_retries.backoff_factor, 1)
        self.assertTrue(all(status in adapter.max_retries.status_forcelist for status in [429, 500, 502, 503, 504]))

    @patch('requests.Session')
    def test_video_url_processing(self, mock_session):
        """Test video URL processing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response
        
        # Set up a complete test article
        base_article = {
            'title': 'Test Title',
            'description': 'Test description',
            'url': 'http://example.com/article',
            'domain': 'example.com'
        }

        # Test MP4 detection
        test_article = base_article.copy()
        test_article['socialimage'] = 'https://example.com/video.mp4'
        test_data = {'articles': [test_article]}
        mock_response.json.return_value = test_data
        mock_response.text = json.dumps(test_data)
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertEqual(news[0]['videoUrl'], 'https://example.com/video.mp4')
        
        # Test YouTube URL detection
        test_article = base_article.copy()
        test_article['socialimage'] = 'https://example.com/image.jpg'
        test_article['url'] = 'https://youtube.com/watch?v=test123'
        test_data = {'articles': [test_article]}
        mock_response.json.return_value = test_data
        mock_response.text = json.dumps(test_data)
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertEqual(news[0]['videoUrl'], 'https://www.youtube.com/embed/test123')

    @patch('requests.Session')
    def test_deduplication(self, mock_session):
        """Test deduplication of arrays"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Set up a complete test article with duplicates
        test_article = {
            'title': 'Test Title',
            'url': 'http://example.com/article',
            'description': 'Test description',
            'domain': 'example.com',
            'locations': ['San Francisco', 'San Francisco', 'New York', 'New York'],
            'persons': ['John Doe', 'John Doe', 'Jane Smith'],
            'organizations': ['Tech Corp', 'Tech Corp', 'Other Corp']
        }
        
        test_data = {'articles': [test_article]}
        mock_response.text = json.dumps(test_data)
        mock_response.json.return_value = test_data
        mock_session.return_value.get.return_value = mock_response
        
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        article = news[0]
        
        # Test deduplication of arrays
        self.assertEqual(len(article['locations']), 2)  # Should deduplicate locations
        self.assertEqual(len(article['persons']), 2)    # Should deduplicate persons
        self.assertEqual(len(article['organizations']), 2)  # Should deduplicate organizations
        self.assertEqual(len(set(article['locations'])), len(article['locations']))  # No duplicates

    @patch('requests.Session')
    def test_error_handling(self, mock_session):
        """Test error handling and provider availability"""
        # Test raw network error
        mock_session.return_value.get.side_effect = requests.exceptions.RequestException("Network error")
        with self.assertRaises(requests.exceptions.RequestException):
            self.provider.fetch_news()
        self.assertFalse(self.provider.is_available)
        self.assertIsNotNone(self.provider.last_error)
        self.assertIn("Network error", self.provider.last_error)
        
        # Reset provider state
        self.provider.mark_available()
        
        # Test JSON decode error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON"
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "Invalid JSON", 0)
        mock_session.return_value.get.side_effect = None
        mock_session.return_value.get.return_value = mock_response
        
        with self.assertRaises(json.JSONDecodeError):
            self.provider.fetch_news()
        self.assertFalse(self.provider.is_available)

    def test_fetch_news_with_category(self):
        """Test fetching news with specific category"""
        news = self.provider.fetch_news('technology')
        self.assertIsInstance(news, list)
        if news:  # Check only if articles are returned
            for article in news:
                self.assertTrue(all(key in article for key in ['title', 'description', 'url', 'category']))
                self.assertEqual(article['category'], 'technology')

    @patch('requests.Session')
    def test_fetch_news_fallback_query(self, mock_session):
        """Test fallback query when primary query fails"""
        # Create mock responses for both primary and fallback queries
        first_response = Mock()
        first_response.status_code = 200
        first_response.text = json.dumps({'articles': []})
        first_response.json.return_value = {'articles': []}

        second_response = Mock()
        second_response.status_code = 200
        mock_data = {'articles': [self.test_article]}
        second_response.text = json.dumps(mock_data)
        second_response.json.return_value = mock_data

        mock_session.return_value.get.side_effect = [first_response, second_response]
        
        news = self.provider.fetch_news('technology')
        self.assertTrue(len(news) > 0)
        self.assertEqual(mock_session.return_value.get.call_count, 2)  # Should try both queries

    @patch('requests.Session')
    def test_article_validation(self, mock_session):
        """Test article validation rules"""
        # Set up mock response
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Test missing title
        test_article = self.test_article.copy()
        test_article['title'] = ''
        mock_data = {'articles': [test_article]}
        mock_response.text = json.dumps(mock_data)
        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        news = self.provider.fetch_news()
        self.assertEqual(len(news), 0)  # Should skip article with missing title
        
        # Test missing URL
        test_article = self.test_article.copy()
        test_article['title'] = 'Test Title'
        test_article['url'] = None
        mock_data = {'articles': [test_article]}
        mock_response.text = json.dumps(mock_data)
        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        news = self.provider.fetch_news()
        self.assertEqual(len(news), 0)  # Should skip article with missing URL

    @patch('requests.Session')
    def test_source_name_cleaning(self, mock_session):
        """Test source name cleaning"""
        # Set up mock response with proper data
        mock_response = Mock()
        mock_response.status_code = 200
        
        # Create test article
        test_article = self.test_article.copy()
        test_article['domain'] = 'www.test-site.com'
        test_article['url'] = 'http://test-site.com'  # Ensure URL is present for validation
        test_article['title'] = 'Test Title'  # Ensure title is present
        mock_data = {'articles': [test_article]}
        
        # Set up response
        mock_response.text = json.dumps(mock_data)
        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertEqual(news[0]['source']['name'], 'Test-Site')
        
        # Test empty domain
        test_article = self.test_article.copy()
        test_article['domain'] = ''
        test_article['url'] = 'http://test-site.com'  # Ensure URL is present for validation
        test_article['title'] = 'Test Title'  # Ensure title is present
        mock_data = {'articles': [test_article]}
        mock_response.text = json.dumps(mock_data)
        mock_response.json.return_value = mock_data
        mock_session.return_value.get.return_value = mock_response
        news = self.provider.fetch_news()
        self.assertTrue(len(news) > 0)
        self.assertEqual(news[0]['source']['name'], 'GDELT')


if __name__ == '__main__':
    unittest.main()
