"""
RSS-based source adapter
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import Iterator, Dict, Any
from datetime import datetime
import logging
from .base_adapter import SourceAdapter

logger = logging.getLogger(__name__)

class RSSAdapter(SourceAdapter):
    """Adapter for RSS-based news sources"""
    
    def __init__(self, config: Dict[str, Any], user_agent: str = None):
        super().__init__(config)
        self.rss_url = config.get('rss')
        self.user_agent = user_agent or 'NewsSurgeAI/1.0'
        
        if not self.rss_url:
            raise ValueError(f"RSS URL required for source {self.source_id}")
    
    def discover(self) -> Iterator[str]:
        """
        Discover article URLs from RSS feed
        
        Yields:
            str: Article URLs
        """
        try:
            logger.info(f"Fetching RSS feed: {self.rss_url}")
            
            # Set user agent for feedparser
            feedparser.USER_AGENT = self.user_agent
            
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has issues: {feed.bozo_exception}")
            
            count = 0
            for entry in feed.entries:
                if count >= self.max_items:
                    break
                
                url = entry.get('link')
                if url:
                    yield url
                    count += 1
                    
            logger.info(f"Discovered {count} articles from {self.source_name}")
            
        except Exception as e:
            logger.error(f"Error discovering articles from {self.source_name}: {str(e)}")
    
    def fetch(self, url: str) -> str:
        """
        Fetch raw HTML content from URL
        
        Args:
            url: Article URL
            
        Returns:
            str: Raw HTML content
        """
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content into normalized article data
        
        Args:
            html: Raw HTML content
            url: Original article URL
            
        Returns:
            Dict containing normalized article data
        """
        if not html:
            return {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = self.extract_title(soup)
            
            # Extract published date
            published_at = self.extract_published_date(soup)
            
            # Extract content
            excerpt, content_snippet = self.extract_content(soup)
            
            # Extract media
            media = self.extract_media_urls(soup)
            
            return {
                'title': title,
                'published_at': published_at,
                'excerpt': excerpt,
                'content_snippet': content_snippet,
                'media': media,
                'category': self.category,
                'language': 'en'
            }
            
        except Exception as e:
            logger.error(f"Error parsing article {url}: {str(e)}")
            return {}
    
    def extract_title(self, soup) -> str:
        """Extract article title"""
        # Try Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try regular title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Untitled Article"
    
    def extract_published_date(self, soup) -> str:
        """Extract published date"""
        # Try various meta tags
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publishdate'}),
            ('meta', {'name': 'date'}),
            ('meta', {'property': 'og:updated_time'}),
            ('time', {'datetime': True}),
        ]
        
        for tag_name, attrs in date_selectors:
            element = soup.find(tag_name, attrs)
            if element:
                date_str = element.get('content') or element.get('datetime')
                if date_str:
                    try:
                        # Try to parse and format the date
                        from dateutil import parser
                        parsed_date = parser.parse(date_str)
                        return parsed_date.isoformat() + 'Z'
                    except:
                        pass
        
        # Default to current time
        return datetime.utcnow().isoformat() + 'Z'
    
    def extract_content(self, soup) -> tuple:
        """Extract article content and excerpt"""
        # Try to find main content area
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            '.story-body',
            '.article-body'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_area = soup.select_one(selector)
            if content_area:
                # Remove script and style elements
                for script in content_area(["script", "style", "nav", "aside", "footer"]):
                    script.decompose()
                
                # Get text from paragraphs
                paragraphs = content_area.find_all('p')
                if paragraphs:
                    content_text = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
                    break
        
        # Fallback: get all paragraphs
        if not content_text:
            paragraphs = soup.find_all('p')
            content_text = ' '.join([p.get_text().strip() for p in paragraphs[:3]])
        
        # Clean up text
        content_text = ' '.join(content_text.split())
        
        # Create excerpt (first 2-3 sentences or 300 chars)
        sentences = content_text.split('. ')
        if len(sentences) >= 2:
            excerpt = '. '.join(sentences[:3]) + '.'
        else:
            excerpt = content_text[:300] + '...' if len(content_text) > 300 else content_text
        
        # Content snippet (first 500 chars)
        content_snippet = content_text[:500] + '...' if len(content_text) > 500 else content_text
        
        return excerpt, content_snippet