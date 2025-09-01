"""
News fetcher implementations for different providers
"""
from .news_api_fetcher import NewsAPIFetcher
from .guardian_fetcher import GuardianFetcher
from .gdelt_fetcher import GDELTFetcher

__all__ = ['NewsAPIFetcher', 'GuardianFetcher', 'GDELTFetcher']
