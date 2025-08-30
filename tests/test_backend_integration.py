"""
Integration tests for the backend service with NewsAPI and AI summarization
"""
import unittest
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.news_fetcher import NewsFetcher
from src.core.cache import Cache
from src.orchestrator import NewsOrchestrator
from tests.mock_ai_generator import MockAIGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestBackendIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        # Ensure we have the required API keys
        cls.news_api_key = os.getenv('NEWS_API_KEY')
        if not cls.news_api_key:
            raise ValueError("NEWS_API_KEY environment variable must be set to run integration tests")
        
        # Initialize components
        cls.news_fetcher = NewsFetcher()
        cls.ai_generator = MockAIGenerator()
        cls.cache = Cache()
        # Create orchestrator with mock AI generator
        cls.orchestrator = NewsOrchestrator()
        cls.orchestrator.ai_generator = cls.ai_generator  # Replace with mock
        
        # Categories to test
        cls.categories = ['technology', 'business', 'science']
        
        # Cache file for storing test results
        cls.cache_dir = Path(__file__).parent / 'test_cache'
        cls.cache_dir.mkdir(exist_ok=True)
    
    def setUp(self):
        """Set up for each test"""
        self.start_time = datetime.now()
        logger.info(f"Starting test: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up after each test"""
        duration = datetime.now() - self.start_time
        logger.info(f"Test {self._testMethodName} completed in {duration.total_seconds():.2f} seconds")
    
    def test_01_news_api_fetch(self):
        """Test fetching news from NewsAPI for each category"""
        for category in self.categories:
            with self.subTest(category=category):
                articles = self.news_fetcher.fetch_news(category)
                
                # Verify we got articles
                self.assertIsInstance(articles, list)
                self.assertGreater(len(articles), 0)
                
                # Check article structure
                article = articles[0]
                required_fields = ['title', 'description', 'url', 'publishedAt', 'source']
                for field in required_fields:
                    self.assertIn(field, article)
                
                # Save articles for later tests
                cache_file = self.cache_dir / f"{category}_articles.json"
                with open(cache_file, 'w') as f:
                    json.dump(articles[:5], f)  # Save first 5 articles
                
                logger.info(f"Fetched and cached {len(articles)} articles for {category}")
    
    def test_02_ai_summarization(self):
        """Test AI summarization on real news articles"""
        for category in self.categories:
            with self.subTest(category=category):
                # Load cached articles
                cache_file = self.cache_dir / f"{category}_articles.json"
                with open(cache_file) as f:
                    articles = json.load(f)
                
                for i, article in enumerate(articles):
                    # Ensure article has required fields
                    article_data = {
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'publishedAt': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'Unknown')
                    }
                    
                    # Generate summary
                    summary, detected_category, is_breaking = self.ai_generator.summarize_article(article_data)
                    
                    # Verify summary
                    self.assertIsInstance(summary, str)
                    self.assertTrue(len(summary) > 0)  # Summary should not be empty
                    
                    # Verify category detection
                    self.assertIn(detected_category, 
                                ['technology', 'business', 'science', 'world', 'general'])
                    
                    # If it's the original category, it should be detected correctly
                    if category in ['technology', 'business', 'science']:
                        self.assertEqual(category, detected_category)
                    
                    # Verify breaking news flag
                    self.assertIsInstance(is_breaking, bool)
                    
                    logger.info(f"Successfully summarized article {i+1} for {category}")
                    
                    # Add results to article for full pipeline test
                    article['summary'] = summary
                    article['detected_category'] = detected_category
                    article['is_breaking'] = is_breaking
                
                # Save processed articles
                with open(cache_file, 'w') as f:
                    json.dump(articles, f)
    
    def test_03_cache_operations(self):
        """Test caching of processed articles"""
        for category in self.categories:
            with self.subTest(category=category):
                # Load processed articles
                cache_file = self.cache_dir / f"{category}_articles.json"
                with open(cache_file) as f:
                    articles = json.load(f)
                
                # Test cache save
                self.cache.save_news(category, articles)
                
                # Test cache retrieval
                cached = self.cache.get_news(category)
                self.assertEqual(len(cached), len(articles))
                
                # Verify all fields are preserved
                for orig, cached_art in zip(articles, cached):
                    self.assertEqual(orig['title'], cached_art['title'])
                    self.assertEqual(orig['summary'], cached_art['summary'])
                    self.assertEqual(orig['detected_category'], cached_art['detected_category'])
                    self.assertEqual(orig['is_breaking'], cached_art['is_breaking'])
                
                logger.info(f"Successfully tested cache operations for {category}")
    
    def test_04_full_pipeline(self):
        """Test the complete news processing pipeline"""
        for category in self.categories:
            with self.subTest(category=category):
                # Process news through orchestrator
                processed_articles = self.orchestrator.process_news(category)
                
                # Verify we got results
                self.assertIsInstance(processed_articles, list)
                self.assertGreater(len(processed_articles), 0)
                
                # Check each processed article
                for article in processed_articles:
                    # Verify all required fields
                    required_fields = [
                        'title', 'description', 'url', 'publishedAt', 'source',
                        'summary', 'category', 'isBreaking'
                    ]
                    for field in required_fields:
                        self.assertIn(field, article)
                    
                    # Verify field types
                    self.assertIsInstance(article['title'], str)
                    self.assertIsInstance(article['summary'], str)
                    self.assertIsInstance(article['isBreaking'], bool)
                    self.assertIn(article['category'], 
                                ['technology', 'business', 'science', 'world', 'general'])
                
                logger.info(f"Successfully tested full pipeline for {category}")
    
    def test_05_rate_limiting(self):
        """Test rate limiting functionality"""
        # Test rapid sequential requests
        for _ in range(3):
            articles = self.news_fetcher.fetch_news('technology')
            self.assertIsInstance(articles, list)
            self.assertGreater(len(articles), 0)
        
        logger.info("Successfully tested rate limiting")

if __name__ == '__main__':
    unittest.main(verbosity=2)
