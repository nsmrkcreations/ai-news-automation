"""
Test suite for the news automation pipeline
"""
import unittest
import os
import json
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent.parent))

from src.core.news_fetcher import NewsFetcher
from src.core.ai_generator import AIGenerator
from src.core.cache import Cache
from src.orchestrator import NewsOrchestrator

def load_test_data():
    """Load test data from JSON file"""
    test_data_path = os.path.join(os.path.dirname(__file__), 'test_data.json')
    with open(test_data_path, 'r') as f:
        return json.load(f)

class TestNewsPipeline(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Ensure we have required environment variables
        os.environ['NEWS_API_KEY'] = os.getenv('NEWS_API_KEY', 'test_key')
        self.news_fetcher = NewsFetcher()
        self.ai_generator = AIGenerator()
        self.cache = Cache()
        self.orchestrator = NewsOrchestrator()

    def test_news_fetcher(self):
        """Test news fetching with mock data"""
        test_data = load_test_data()
        # Monkey patch the fetch_news method to return test data
        original_fetch = self.news_fetcher.fetch_news
        self.news_fetcher.fetch_news = lambda category: test_data.get(category, [])
        
        try:
            # Test technology news
            tech_articles = self.news_fetcher.fetch_news('technology')
            self.assertEqual(len(tech_articles), 2)
            self.assertEqual(tech_articles[0]['source']['name'], 'TechCrunch')
            self.assertTrue('quantum' in tech_articles[0]['title'].lower())
            
            # Test business news
            business_articles = self.news_fetcher.fetch_news('business')
            self.assertEqual(len(business_articles), 1)
            self.assertEqual(business_articles[0]['source']['name'], 'Bloomberg')
        finally:
            # Restore original method
            self.news_fetcher.fetch_news = original_fetch

    def test_ai_generator(self):
        """Test AI summarization with real article data"""
        test_data = load_test_data()
        quantum_article = test_data['technology'][0]
        battery_article = test_data['technology'][1]
        
        # Test quantum computing article
        summary1, category1, is_breaking1 = self.ai_generator.summarize_article(quantum_article)
        self.assertIsInstance(summary1, str)
        self.assertTrue(len(summary1) > 0)
        self.assertEqual(category1, 'technology')  # Should definitely be categorized as technology
        self.assertTrue(is_breaking1)  # Should be breaking news due to breakthrough
        
        # Test battery technology article
        summary2, category2, is_breaking2 = self.ai_generator.summarize_article(battery_article)
        self.assertIsInstance(summary2, str)
        self.assertTrue(len(summary2) > 0)
        self.assertEqual(category2, 'technology')
        # Breaking news status may vary, so we just check the type
        self.assertIsInstance(is_breaking2, bool)

    def test_cache_operations(self):
        """Test cache operations with real article data"""
        test_data = load_test_data()
        tech_articles = test_data['technology']
        
        # Test saving to cache
        self.cache.save_news('technology', tech_articles)
        
        # Test retrieving from cache
        cached_articles = self.cache.get_news('technology')
        self.assertEqual(len(cached_articles), 2)
        self.assertEqual(cached_articles[0]['title'], 'AI Startup Develops Revolutionary Quantum Computing Solution')
        self.assertEqual(cached_articles[1]['source']['name'], 'Wired')
        
        # Test cache update
        new_article = test_data['business'][0]
        updated_articles = [new_article] + tech_articles
        self.cache.save_news('technology', updated_articles)
        
        # Verify cache was updated
        updated_cached = self.cache.get_news('technology')
        self.assertEqual(len(updated_cached), 3)
        self.assertEqual(updated_cached[0]['source']['name'], 'Bloomberg')

    def test_news_processing(self):
        """Test end-to-end news processing with real data"""
        test_data = load_test_data()
        
        # Monkey patch the news fetcher
        original_fetch = self.news_fetcher.fetch_news
        self.news_fetcher.fetch_news = lambda category: test_data.get(category, [])
        
        try:
            # Process technology news
            articles = self.orchestrator.process_news('technology')
            
            # Verify the structure and content of processed articles
            self.assertEqual(len(articles), 2)
            
            # Check first article (Quantum Computing)
            article = articles[0]
            self.assertTrue('quantum' in article['title'].lower())
            self.assertTrue(isinstance(article.get('summary'), str))
            self.assertEqual(article.get('category'), 'technology')
            self.assertTrue(article.get('isBreaking'))  # Should be breaking due to breakthrough
            
            # Check second article (Battery Technology)
            article2 = articles[1]
            self.assertTrue('battery' in article2['title'].lower())
            self.assertTrue(isinstance(article2.get('summary'), str))
            self.assertEqual(article2.get('category'), 'technology')
            
            # Verify all required fields are present
            required_fields = ['title', 'description', 'url', 'urlToImage', 
                             'publishedAt', 'source', 'category', 'isBreaking', 'summary']
            for field in required_fields:
                self.assertIn(field, article)
                self.assertIn(field, article2)
        finally:
            # Restore original method
            self.news_fetcher.fetch_news = original_fetch
            for field in required_fields:
                self.assertIn(field, article)

if __name__ == '__main__':
    unittest.main()
