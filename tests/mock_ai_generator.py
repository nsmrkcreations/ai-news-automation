"""Mock AI Generator for testing"""
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class MockAIGenerator:
    def __init__(self):
        self.call_count = 0
    
    def summarize_article(self, article: Dict[str, Any]) -> Tuple[str, str, bool]:
        """
        Mock article summarization
        """
        self.call_count += 1
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Return the description as summary, detect category from content
        category = 'technology' if any(word in title.lower() for word in ['ai', 'tech', 'robot', 'software']) else \
                  'business' if any(word in title.lower() for word in ['market', 'stock', 'economy']) else \
                  'science' if any(word in title.lower() for word in ['research', 'study', 'science']) else \
                  'general'
        
        # Detect breaking news based on keywords
        is_breaking = any(word in title.lower() for word in [
            'breaking', 'urgent', 'just in', 'latest', 'exclusive',
            'breakthrough', 'revolution'
        ])
        
        return description or title, category, is_breaking
