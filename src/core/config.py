"""
Configuration for the news automation system
"""
from dataclasses import dataclass
from typing import Dict, Any
import os

@dataclass
class NewsAPIConfig:
    api_key: str
    base_url: str = "https://newsapi.org/v2"
    rate_limit_calls: int = 100  # Calls per day for free tier
    rate_limit_window: int = 86400  # 24 hours in seconds

@dataclass
class CacheConfig:
    cache_dir: str = "cache"
    news_expiry_hours: int = 1
    breaking_news_expiry_minutes: int = 15

@dataclass
class OllamaConfig:
    model: str = "llama2"
    base_url: str = "http://localhost:11434"
    max_retries: int = 3
    timeout: int = 30

@dataclass
class Config:
    news_api: NewsAPIConfig
    cache: CacheConfig
    ollama: OllamaConfig
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables
        """
        return cls(
            news_api=NewsAPIConfig(
                api_key=os.getenv('NEWS_API_KEY', ''),
                rate_limit_calls=int(os.getenv('NEWS_API_RATE_LIMIT_CALLS', '100')),
                rate_limit_window=int(os.getenv('NEWS_API_RATE_LIMIT_WINDOW', '86400'))
            ),
            cache=CacheConfig(
                cache_dir=os.getenv('CACHE_DIR', 'cache'),
                news_expiry_hours=int(os.getenv('NEWS_EXPIRY_HOURS', '1')),
                breaking_news_expiry_minutes=int(os.getenv('BREAKING_NEWS_EXPIRY_MINUTES', '15'))
            ),
            ollama=OllamaConfig(
                model=os.getenv('OLLAMA_MODEL', 'llama2'),
                base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
                max_retries=int(os.getenv('OLLAMA_MAX_RETRIES', '3')),
                timeout=int(os.getenv('OLLAMA_TIMEOUT', '30'))
            )
        )
