"""
Integration tests for news providers
"""
import os
import pytest
from datetime import datetime
from src.core.gdelt_provider import GdeltNewsProvider
from src.core.guardian_provider import GuardianNewsProvider
from src.core.newsapi_provider import NewsAPIProvider
from src.core.provider_manager import NewsProviderManager

@pytest.fixture
def provider_manager():
    """Set up provider manager with all providers"""
    return NewsProviderManager(use_cache=False)

@pytest.fixture(autouse=True)
def setup_env():
    """Set up environment variables before tests"""
    os.environ["GUARDIAN_API_KEY"] = "c3c7df8a-61dc-403f-8c26-dc5a6546c782"
    os.environ["NEWS_API_KEY"] = "556025e23b5e4d6b94b4780a4e89fdd8"
    yield
    # Clean up after tests
    os.environ.pop("GUARDIAN_API_KEY", None)
    os.environ.pop("NEWS_API_KEY", None)

@pytest.fixture
def providers():
    """Set up individual providers for testing"""
    return {
        'gdelt': GdeltNewsProvider(),
        'guardian': GuardianNewsProvider(),
        'newsapi': NewsAPIProvider()
    }

def validate_article(article):
    """Validate article structure"""
    required_fields = ['title', 'url', 'publishedAt', 'source', 'category']
    return all(field in article for field in required_fields)

class TestProvidersIntegration:
    """Test suite for provider integration"""
    
    def test_provider_initialization(self, providers):
        """Test that all providers initialize correctly"""
        for name, provider in providers.items():
            assert provider.name is not None
            assert hasattr(provider, 'is_available')
            assert hasattr(provider, 'base_url')
    
    def test_provider_availability(self, providers):
        """Test provider availability and API keys"""
        for name, provider in providers.items():
            assert provider.is_available, f"{name} provider should be available"
            if hasattr(provider, 'api_key'):
                assert provider.api_key is not None, f"{name} provider missing API key"
    
    @pytest.mark.vcr
    def test_gdelt_news_fetch(self, providers):
        """Test GDELT news fetching"""
        provider = providers['gdelt']
        articles = provider.fetch_news(category='technology')
        assert len(articles) > 0, "GDELT should return articles"
        assert all(validate_article(article) for article in articles)
    
    @pytest.mark.vcr
    def test_guardian_news_fetch(self, providers):
        """Test Guardian news fetching"""
        provider = providers['guardian']
        articles = provider.fetch_news(category='technology')
        assert len(articles) > 0, "Guardian should return articles"
        assert all(validate_article(article) for article in articles)
    
    @pytest.mark.vcr
    def test_newsapi_news_fetch(self, providers):
        """Test NewsAPI news fetching"""
        provider = providers['newsapi']
        articles = provider.fetch_news(category='technology')
        assert len(articles) > 0, "NewsAPI should return articles"
        assert all(validate_article(article) for article in articles)
    
    def test_provider_failover(self, provider_manager):
        """Test provider failover mechanism"""
        # Force first provider to fail
        provider_manager.providers[0].is_available = False
        
        # Should automatically switch to next provider
        articles = provider_manager.fetch_news(category='technology')
        assert len(articles) > 0, "Failover should provide articles"
        assert all(validate_article(article) for article in articles)
    
    def test_category_mapping(self, providers):
        """Test category mapping across providers"""
        categories = ['technology', 'business', 'science', 'sports', 
                     'entertainment', 'politics', 'general']
        
        for name, provider in providers.items():
            for category in categories:
                articles = provider.fetch_news(category=category)
                if articles:  # Some categories might not have articles
                    assert all(article['category'] == category for article in articles), \
                        f"{name} provider returned articles with wrong category"
    
    @pytest.mark.vcr
    def test_provider_error_handling(self, providers):
        """Test error handling in providers"""
        for name, provider in providers.items():
            # Simulate API failure by setting invalid base URL
            original_url = provider.base_url
            provider.base_url = "https://invalid-url-for-testing.com"
            
            try:
                with pytest.raises(Exception):
                    provider.fetch_news()
            finally:
                # Restore original URL
                provider.base_url = original_url
                
            assert not provider.is_available, f"{name} provider should be marked as unavailable after error"
            assert provider.last_error is not None, f"{name} provider should record error message"
