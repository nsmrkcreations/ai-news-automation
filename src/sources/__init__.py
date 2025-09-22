"""
Source adapters for news fetching from various publishers
"""
from .base_adapter import SourceAdapter
from .rss_adapter import RSSAdapter

__all__ = ['SourceAdapter', 'RSSAdapter']