"""
Tests for the NewsFetcher component
"""
import pytest
from unittest.mock import patch, Mock
from src.core.news_fetcher import NewsFetcher
from tests.test_utils import (
    mock_news_api_response,
    setup_test_env,
    MockResponse,
    assert_valid_article_list
)

class TestNewsFetcher:
    @pytest.fixture
    def news_fetcher(self, setup_test_env):
        return NewsFetcher()

    def test_initialization(self, news_fetcher):
        """Test NewsFetcher initialization"""
        assert news_fetcher.news_api_key == 'test_api_key'
        assert news_fetcher.base_url == "https://newsapi.org/v2"

    @patch('requests.get')
    def test_fetch_news_success(self, mock_get, news_fetcher, mock_news_api_response):
        """Test successful news fetching"""
        mock_get.return_value = MockResponse(mock_news_api_response)
        
        articles = news_fetcher.fetch_news('technology')
        assert_valid_article_list(articles)
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['params']['category'] == 'technology'
        assert kwargs['params']['apiKey'] == 'test_api_key'

    @patch('requests.get')
    def test_fetch_news_no_category(self, mock_get, news_fetcher, mock_news_api_response):
        """Test fetching news without category"""
        mock_get.return_value = MockResponse(mock_news_api_response)
        
        articles = news_fetcher.fetch_news()
        assert_valid_article_list(articles)
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'category' not in kwargs['params']

    @patch('requests.get')
    def test_fetch_news_api_error(self, mock_get, news_fetcher):
        """Test handling of API errors"""
        # Test different error scenarios
        error_cases = [
            (403, 'Forbidden'),
            (429, 'Too Many Requests'),
            (500, 'Internal Server Error')
        ]
        
        for status_code, message in error_cases:
            mock_get.return_value = MockResponse({'error': message}, status_code)
            articles = news_fetcher.fetch_news('technology')
            assert articles == [], f"Should return empty list on {status_code} error"

    @patch('requests.get')
    def test_fetch_news_network_error(self, mock_get, news_fetcher):
        """Test handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        articles = news_fetcher.fetch_news('technology')
        assert articles == [], "Should return empty list on network error"

    @patch('requests.get')
    def test_fetch_news_invalid_response(self, mock_get, news_fetcher):
        """Test handling of invalid API responses"""
        # Test missing articles key
        mock_get.return_value = MockResponse({'status': 'ok'})
        articles = news_fetcher.fetch_news('technology')
        assert articles == [], "Should handle missing articles in response"
        
        # Test invalid article format
        mock_get.return_value = MockResponse({
            'status': 'ok',
            'articles': [{'invalid': 'format'}]
        })
        articles = news_fetcher.fetch_news('technology')
        assert articles == [], "Should handle invalid article format"

    @patch('requests.get')
    def test_fetch_news_rate_limit(self, mock_get, news_fetcher):
        """Test handling of rate limiting"""
        mock_get.return_value = MockResponse(
            {'error': 'Rate limit exceeded'},
            429
        )
        articles = news_fetcher.fetch_news('technology')
        assert articles == [], "Should handle rate limiting gracefully"

    def test_invalid_api_key(self):
        """Test behavior with invalid API key"""
        fetcher = NewsFetcher()
        fetcher.news_api_key = 'invalid_key'
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = MockResponse(
                {'error': 'Invalid API key'},
                401
            )
            articles = fetcher.fetch_news('technology')
            assert articles == [], "Should handle invalid API key"

    @patch('requests.get')
    def test_fetch_news_categories(self, mock_get, news_fetcher, mock_news_api_response):
        """Test fetching news for different categories"""
        mock_get.return_value = MockResponse(mock_news_api_response)
        
        categories = ['technology', 'business', 'science', 'world', 'general']
        for category in categories:
            articles = news_fetcher.fetch_news(category)
            assert_valid_article_list(articles)
            
            args, kwargs = mock_get.call_args
            assert kwargs['params']['category'] == category

    @patch('requests.get')
    def test_fetch_news_response_validation(self, mock_get, news_fetcher):
        """Test validation of article fields"""
        # Test with missing optional fields
        minimal_article = {
            'title': 'Test Title',
            'url': 'http://test.com',
            'publishedAt': '2025-08-30T12:00:00Z'
        }
        
        mock_get.return_value = MockResponse({
            'status': 'ok',
            'articles': [minimal_article]
        })
        
        articles = news_fetcher.fetch_news('technology')
        assert len(articles) == 1
        assert articles[0]['title'] == 'Test Title'
        assert 'description' in articles[0]  # Should have default value
        assert 'urlToImage' in articles[0]  # Should have default value
