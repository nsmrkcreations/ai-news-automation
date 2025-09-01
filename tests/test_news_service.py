"""
Comprehensive test suite for news service components
"""
import pytest
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.webapp import app
from src.core.provider_manager import NewsProviderManager
from src.core.news_providers import NewsProvider
from src.core.validation import validate_news_data
from src.core.health_monitor import HealthMonitor

# Test client for API tests
@pytest.fixture
def client():
    from fastapi.testclient import TestClient as FastAPITestClient
    return FastAPITestClient(app)

# Sample test data
SAMPLE_ARTICLE = {
    'title': 'Test Article',
    'description': 'Test Description',
    'url': 'https://test.com/article',
    'urlToImage': 'https://test.com/image.jpg',
    'publishedAt': datetime.now().isoformat(),
    'source': {
        'id': 'test-source',
        'name': 'Test Source'
    },
    'category': 'technology',
    'isBreaking': False,
    'fetchedAt': datetime.now().isoformat()
}

@pytest.fixture
def sample_news_data():
    """Fixture for sample news data"""
    return [SAMPLE_ARTICLE.copy() for _ in range(3)]

@pytest.fixture
def health_monitor():
    """Fixture for health monitor"""
    monitor = HealthMonitor()
    yield monitor
    # Cleanup
    if os.path.exists(monitor.state_file):
        os.remove(monitor.state_file)

class TestNewsAPI:
    """Test suite for news API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_get_news_no_params(self, client):
        """Test getting news without parameters"""
        response = client.get("/api/news")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "count" in data
        assert "data" in data

    def test_get_news_with_category(self, client):
        """Test getting news with category filter"""
        response = client.get("/api/news?category=technology")
        assert response.status_code == 200
        data = response.json()
        assert all(article["category"] == "technology" for article in data["data"])

    def test_get_news_with_limit(self, client):
        """Test getting news with limit"""
        limit = 2
        response = client.get(f"/api/news?limit={limit}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= limit

class TestNewsValidation:
    """Test suite for news validation"""

    def test_valid_article(self, sample_news_data):
        """Test valid article validation"""
        assert validate_news_data(sample_news_data)

    def test_invalid_article_missing_required(self):
        """Test validation with missing required fields"""
        invalid_article = SAMPLE_ARTICLE.copy()
        del invalid_article["title"]
        assert not validate_news_data([invalid_article])

    def test_invalid_article_wrong_date(self):
        """Test validation with invalid date format"""
        invalid_article = SAMPLE_ARTICLE.copy()
        invalid_article["publishedAt"] = "not-a-date"
        assert not validate_news_data([invalid_article])

class TestHealthMonitoring:
    """Test suite for health monitoring"""

    def test_health_monitor_initialization(self, health_monitor):
        """Test health monitor initialization"""
        status = health_monitor.get_health_status()
        assert status["status"] in ["healthy", "initializing"]
        assert status["consecutiveFailures"] == 0

    def test_health_monitor_success_recording(self, health_monitor):
        """Test recording successful health checks"""
        health_monitor.record_health_check(True)
        status = health_monitor.get_health_status()
        assert status["status"] == "healthy"
        assert status["consecutiveFailures"] == 0

    def test_health_monitor_failure_recording(self, health_monitor):
        """Test recording failed health checks"""
        for _ in range(4):  # Trigger failing status
            health_monitor.record_health_check(False)
        status = health_monitor.get_health_status()
        assert status["status"] == "failing"
        assert status["consecutiveFailures"] == 4

class TestNewsProviders:
    """Test suite for news providers"""

    @pytest.fixture
    def provider_manager(self):
        """Fixture for provider manager"""
        return NewsProviderManager(use_cache=False)

    def test_provider_failover(self, provider_manager):
        """Test provider failover mechanism"""
        # Make primary provider fail
        provider_manager.providers[0].is_available = False
        
        # Verify fallback to secondary provider
        assert provider_manager.get_healthy_provider() == provider_manager.providers[1]

    def test_provider_recovery(self, provider_manager):
        """Test provider recovery after failure"""
        provider = provider_manager.providers[0]
        provider.is_available = False
        provider.mark_available()
        assert provider.is_available
        assert provider_manager.get_healthy_provider() == provider

    @pytest.mark.integration
    def test_full_news_cycle(self, provider_manager, sample_news_data):
        """Test complete news fetching and processing cycle"""
        # Mock news fetching
        with patch.object(provider_manager.providers[0], 'fetch_news') as mock_fetch:
            mock_fetch.return_value = sample_news_data
            
            # Process news
            result = provider_manager.fetch_news()
            
            # Verify results
            assert len(result) == len(sample_news_data)
            assert all(validate_news_data([article]) for article in result)

if __name__ == '__main__':
    pytest.main(['-v', __file__])
