"""
Validation utilities for news data
"""
from typing import List, Dict, Any
from datetime import datetime
import json

def validate_article(article: Dict[str, Any]) -> bool:
    """
    Validate a single news article.
    
    Args:
        article: Article data to validate
        
    Returns:
        True if article is valid, False otherwise
    """
    required_fields = ['title', 'url', 'publishedAt', 'source']
    
    # Check required fields
    if not all(field in article for field in required_fields):
        return False
        
    # Validate source structure
    if not isinstance(article['source'], dict) or 'name' not in article['source']:
        return False
        
    # Validate dates
    try:
        datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
        if 'fetchedAt' in article:
            datetime.fromisoformat(article['fetchedAt'].replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return False
        
    return True

def validate_news_data(articles: List[Dict[str, Any]]) -> bool:
    """
    Validate a list of news articles.
    
    Args:
        articles: List of articles to validate
        
    Returns:
        True if all articles are valid, False otherwise
    """
    if not isinstance(articles, list):
        return False
        
    return all(validate_article(article) for article in articles)

def save_news_data(articles: List[Dict[str, Any]], filepath: str) -> bool:
    """
    Safely save news data to file with validation.
    
    Args:
        articles: List of articles to save
        filepath: Path to save the file to
        
    Returns:
        True if save was successful, False otherwise
    """
    if not validate_news_data(articles):
        return False
        
    try:
        # Write to temporary file first
        temp_path = filepath + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
            
        # Validate the written data
        with open(temp_path, 'r', encoding='utf-8') as f:
            test_load = json.load(f)
            
        if not validate_news_data(test_load):
            return False
            
        # If validation passes, rename temp file to actual file
        import os
        if os.path.exists(filepath):
            os.remove(filepath)
        os.rename(temp_path, filepath)
        return True
        
    except Exception:
        # Clean up temp file if it exists
        import os
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False
