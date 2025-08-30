"""
Comprehensive test suite for news automation
"""
import unittest
import os
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.core.news_fetcher import NewsFetcher
from src.core.ai_generator import AIGenerator
from src.core.rate_limiter import RateLimiter, EnhancedCache
from src.core.error_monitor import ErrorMonitor
from src.orchestrator import NewsOrchestrator

class TestNewsFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = NewsFetcher()
        
    @patch('requests.get')
    def test_fetch_news_success(self, mock_get):
        # Mock successful API response
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {
            'articles': [
                {
                    'title': 'Test Article',
                    'description': 'Test Description',
                    'url': 'http://test.com'
                }
            ]
        }
        
        articles = self.fetcher.fetch_news('technology')
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['title'], 'Test Article')
        
    @patch('requests.get')
    def test_fetch_news_error(self, mock_get):
        # Mock API error
        mock_get.side_effect = Exception('API Error')
        
        articles = self.fetcher.fetch_news('technology')
        self.assertEqual(len(articles), 0)

class TestAIGenerator(unittest.TestCase):
    def setUp(self):
        self.ai_generator = AIGenerator()
        
    @patch('requests.post')
    def test_summarize_article(self, mock_post):
        # Mock Ollama response
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            'response': 'Test summary'
        }
        
        article = {
            'title': 'Test Title',
            'description': 'Test Description',
            'content': 'Test Content'
        }
        
        summary, category, is_breaking = self.ai_generator.summarize_article(article)
        self.assertIsInstance(summary, str)
        self.assertIsInstance(category, str)
        self.assertIsInstance(is_breaking, bool)
        
    def test_check_ollama_status(self):
        status = self.ai_generator.check_ollama_status()
        self.assertIsInstance(status, bool)

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.rate_limiter = RateLimiter(calls=2, time_window=1)
        
    def test_rate_limiting(self):
        # First two calls should succeed
        self.assertTrue(self.rate_limiter.try_acquire())
        self.assertTrue(self.rate_limiter.try_acquire())
        
        # Third call should fail
        self.assertFalse(self.rate_limiter.try_acquire())
        
        # Wait for time window to pass
        time.sleep(1.1)
        
        # Should succeed again
        self.assertTrue(self.rate_limiter.try_acquire())

class TestEnhancedCache(unittest.TestCase):
    def setUp(self):
        self.cache = EnhancedCache(cache_dir='test_cache')
        
    def tearDown(self):
        # Clean up test cache
        import shutil
        if os.path.exists('test_cache'):
            shutil.rmtree('test_cache')
            
    def test_cache_operations(self):
        # Test setting and getting
        self.cache.set('test_key', 'test_value')
        self.assertEqual(self.cache.get('test_key'), 'test_value')
        
        # Test expiration
        self.cache.set('expire_key', 'expire_value', expiry=timedelta(seconds=1))
        self.assertEqual(self.cache.get('expire_key'), 'expire_value')
        
        time.sleep(1.1)
        self.assertIsNone(self.cache.get('expire_key'))

class TestErrorMonitor(unittest.TestCase):
    def setUp(self):
        self.error_monitor = ErrorMonitor()
        
    def test_error_logging(self):
        # Log some errors
        self.error_monitor.log_error('test_error', 'Test message')
        
        # Get summary
        summary = self.error_monitor.get_error_summary()
        self.assertGreater(summary['total_errors'], 0)
        self.assertIn('test_error', summary['error_distribution'])

class TestNewsOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = NewsOrchestrator()
        
    @patch('src.core.news_fetcher.NewsFetcher.fetch_news')
    @patch('src.core.ai_generator.AIGenerator.summarize_article')
    def test_process_news(self, mock_summarize, mock_fetch):
        # Mock fetcher response
        mock_fetch.return_value = [{
            'title': 'Test Article',
            'description': 'Test Description',
            'url': 'http://test.com',
            'publishedAt': datetime.now().isoformat()
        }]
        
        # Mock AI response
        mock_summarize.return_value = ('AI Summary', 'technology', True)
        
        # Process news
        articles = self.orchestrator.process_news('technology')
        
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['category'], 'technology')
        self.assertTrue(articles[0]['isBreaking'])

if __name__ == '__main__':
    unittest.main()
