"""
Tests for the AI Generator component
"""
import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from src.core.ai_generator import AIGenerator
from tests.test_utils import (
    create_test_article,
    mock_ollama_response,
    setup_test_env,
    MockResponse
)

class TestAIGenerator:
    @pytest.fixture
    def ai_generator(self, setup_test_env):
        return AIGenerator()

    @pytest.fixture
    def test_article(self):
        return create_test_article()

    def test_initialization(self, ai_generator):
        """Test AIGenerator initialization"""
        assert ai_generator.model == 'test_model'
        assert ai_generator.max_retries == 3
        assert 'localhost' in ai_generator.ollama_url

    @patch('requests.post')
    def test_summarize_article_success(self, mock_post, ai_generator, test_article):
        """Test successful article summarization"""
        # Mock responses for summary, category, and breaking news check
        responses = [
            {'response': 'Test summary'},
            {'response': 'technology'},
            {'response': 'false'}
        ]
        mock_post.side_effect = [MockResponse(r) for r in responses]
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        
        assert isinstance(summary, str)
        assert summary == 'Test summary'
        assert category == 'technology'
        assert not is_breaking
        assert mock_post.call_count == 3

    @patch('requests.post')
    def test_summarize_article_retry(self, mock_post, ai_generator, test_article):
        """Test retry mechanism"""
        # First call fails, second succeeds
        mock_post.side_effect = [
            Exception("Connection error"),
            MockResponse({'response': 'Test summary'}),
            MockResponse({'response': 'technology'}),
            MockResponse({'response': 'false'})
        ]
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert summary == 'Test summary'
        assert mock_post.call_count == 4

    @patch('requests.post')
    def test_summarize_article_all_retries_fail(self, mock_post, ai_generator, test_article):
        """Test handling of persistent failures"""
        mock_post.side_effect = Exception("Connection error")
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert summary == test_article['description']
        assert category == 'general'
        assert not is_breaking
        assert mock_post.call_count >= 3

    @patch('requests.post')
    def test_category_validation(self, mock_post, ai_generator, test_article):
        """Test category validation"""
        # Test with invalid category response
        mock_post.side_effect = [
            MockResponse({'response': 'Test summary'}),
            MockResponse({'response': 'invalid_category'}),
            MockResponse({'response': 'false'})
        ]
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert category == 'general'  # Should default to general

    @patch('requests.post')
    def test_breaking_news_detection(self, mock_post, ai_generator, test_article):
        """Test breaking news detection"""
        # Test true case
        mock_post.side_effect = [
            MockResponse({'response': 'Test summary'}),
            MockResponse({'response': 'technology'}),
            MockResponse({'response': 'true'})
        ]
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert is_breaking

        # Test false case
        mock_post.side_effect = [
            MockResponse({'response': 'Test summary'}),
            MockResponse({'response': 'technology'}),
            MockResponse({'response': 'false'})
        ]
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert not is_breaking

    def test_check_ollama_status(self, ai_generator):
        """Test Ollama status check"""
        with patch('requests.get') as mock_get:
            # Test when Ollama is running
            mock_get.return_value = MockResponse({
                'models': [{'name': 'test_model'}]
            })
            assert ai_generator.check_ollama_status()
            
            # Test when Ollama is down
            mock_get.side_effect = Exception("Connection refused")
            assert not ai_generator.check_ollama_status()

    @patch('requests.post')
    def test_timeout_handling(self, mock_post, ai_generator, test_article):
        """Test handling of timeouts"""
        mock_post.side_effect = TimeoutError("Request timed out")
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert summary == test_article['description']
        assert category == 'general'
        assert not is_breaking

    @patch('requests.post')
    def test_empty_response_handling(self, mock_post, ai_generator, test_article):
        """Test handling of empty responses"""
        mock_post.return_value = MockResponse({'response': ''})
        
        summary, category, is_breaking = ai_generator.summarize_article(test_article)
        assert summary == test_article['description']
        assert category == 'general'
        assert not is_breaking

    @patch('requests.post')
    def test_malformed_article_handling(self, mock_post, ai_generator):
        """Test handling of malformed articles"""
        malformed_article = {'title': 'Test'}  # Missing required fields
        
        summary, category, is_breaking = ai_generator.summarize_article(malformed_article)
        assert isinstance(summary, str)
        assert category == 'general'
        assert not is_breaking
