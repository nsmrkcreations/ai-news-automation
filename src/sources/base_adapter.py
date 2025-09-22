"""
Base source adapter class for news fetching
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Iterator
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SourceAdapter(ABC):
    """Base class for all source adapters"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_id = config.get('id', 'unknown')
        self.source_name = config.get('name', 'Unknown Source')
        self.max_items = config.get('max_items', 10)
        self.category = config.get('category', 'general')
        
    @abstractmethod
    def discover(self) -> Iterator[str]:
        """
        Discover article URLs from the source
        
        Yields:
            str: Article URLs
        """
        pass
    
    @abstractmethod
    def fetch(self, url: str) -> str:
        """
        Fetch raw HTML content from URL
        
        Args:
            url: Article URL
            
        Returns:
            str: Raw HTML content
        """
        pass
    
    @abstractmethod
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content into normalized article data
        
        Args:
            html: Raw HTML content
            url: Original article URL
            
        Returns:
            Dict containing normalized article data
        """
        pass
    
    def generate_id(self, url: str, title: str = None) -> str:
        """
        Generate unique ID for article
        
        Args:
            url: Article URL
            title: Article title (optional)
            
        Returns:
            str: Unique article ID
        """
        content = f"{self.source_id}_{url}"
        if title:
            content += f"_{title}"
        return f"{self.source_id}_{hashlib.sha1(content.encode()).hexdigest()[:12]}"
    
    def normalize_article(self, parsed_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Normalize parsed article data to standard format
        
        Args:
            parsed_data: Raw parsed data
            url: Original article URL
            
        Returns:
            Dict: Normalized article data
        """
        now = datetime.utcnow().isoformat() + 'Z'
        
        return {
            'id': self.generate_id(url, parsed_data.get('title')),
            'title': parsed_data.get('title', '').strip(),
            'source': self.source_name,
            'source_url': url,
            'published_at': parsed_data.get('published_at', now),
            'category': parsed_data.get('category', self.category),
            'language': parsed_data.get('language', 'en'),
            'media': parsed_data.get('media', []),
            'excerpt': parsed_data.get('excerpt', '').strip(),
            'content_snippet': parsed_data.get('content_snippet', '').strip(),
            'summary': '',  # Will be filled by Ollama
            'keywords': [],  # Will be filled by Ollama
            'reading_time_minutes': self.estimate_reading_time(parsed_data.get('content_snippet', '')),
            'fetched_at': now
        }
    
    def estimate_reading_time(self, text: str) -> int:
        """
        Estimate reading time in minutes
        
        Args:
            text: Article text
            
        Returns:
            int: Estimated reading time in minutes
        """
        if not text:
            return 1
        
        words = len(text.split())
        # Average reading speed: 200 words per minute
        minutes = max(1, round(words / 200))
        return minutes
    
    def extract_media_urls(self, soup) -> List[Dict[str, str]]:
        """
        Extract media URLs from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            List of media dictionaries
        """
        media = []
        
        # Try Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            media.append({
                'type': 'image',
                'url': og_image['content']
            })
            return media
        
        # Try Twitter image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            media.append({
                'type': 'image',
                'url': twitter_image['content']
            })
            return media
        
        # Find largest image in article
        images = soup.find_all('img')
        for img in images:
            src = img.get('src') or img.get('data-src')
            if src and 'http' in src:
                # Skip small images (likely icons/ads)
                width = img.get('width')
                height = img.get('height')
                if width and height:
                    try:
                        if int(width) > 200 and int(height) > 150:
                            media.append({
                                'type': 'image',
                                'url': src
                            })
                            break
                    except ValueError:
                        pass
                else:
                    # If no dimensions, take the first reasonable image
                    if not any('logo' in src.lower() or 'icon' in src.lower() for src in [src]):
                        media.append({
                            'type': 'image',
                            'url': src
                        })
                        break
        
        return media