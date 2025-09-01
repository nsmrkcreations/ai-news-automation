"""
The Guardian news provider implementation.
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from .news_providers import NewsProvider
from .logger import get_logger

logger = get_logger(__name__)

class GuardianNewsProvider(NewsProvider):
    """Guardian API news provider implementation."""
    
    def __init__(self):
        """Initialize the Guardian news provider."""
        super().__init__("Guardian")
        self.base_url = "https://content.guardianapis.com/search"
        self.api_key = os.getenv("GUARDIAN_API_KEY")
        if not self.api_key:
            self.is_available = False
            self.last_error = "Guardian API key not found"
        self.is_available = True
        self.last_error = None
        
        # Map Guardian sections to our categories
        self.section_to_category = {
            'technology': 'technology',
            'business': 'business',
            'science': 'science',
            'sport': 'sports',
            'culture': 'entertainment',
            'politics': 'politics',
            'uk-news': 'general',
            'us-news': 'general',
            'world': 'general',
            'environment': 'science'
        }

    def _make_request(self, section: str = None) -> Dict[str, Any]:
        """Make a request to the Guardian API.
        
        Args:
            section: Optional section to filter by
            
        Returns:
            Dict containing the API response
        """
        params = {
            'api-key': self.api_key,
            'show-fields': 'headline,standfirst,thumbnail,lastModified,body,main,trailText,hasStoryPackage,thumbnail,videoId',
            'page-size': 50,
            'order-by': 'newest',
            'show-tags': 'keyword,type,tone',
            'show-elements': 'video,image'
        }
        
        if section:
            params['section'] = section
            
        try:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                max_retries=3,
                pool_connections=100,
                pool_maxsize=100
            )
            session.mount("https://", adapter)
            
            response = session.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()['response']
            
        except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
            self.is_available = False
            self.last_error = str(e)
            raise

    def _parse_date(self, date_str: str) -> str:
        """Parse Guardian date format to ISO format.
        
        Args:
            date_str: Date string from Guardian API
            
        Returns:
            ISO formatted date string
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            return dt.isoformat() + "Z"
        except (ValueError, TypeError):
            return datetime.utcnow().isoformat() + "Z"

    def _determine_category(self, article: Dict[str, Any], default_category: str = 'general') -> str:
        """Determine the category of an article.
        
        Args:
            article: Article data from Guardian API
            default_category: Default category if none can be determined
            
        Returns:
            Category string
        """
        # Check section mapping
        section = article.get('sectionId', '')
        if section in self.section_to_category:
            return self.section_to_category[section]
            
        # Check tags
        for tag in article.get('tags', []):
            tag_id = tag.get('id', '').lower()
            if tag_id in self.section_to_category:
                return self.section_to_category[tag_id]
                
        return default_category

    def fetch_news(self, category: str = None) -> List[Dict[str, Any]]:
        """Fetch news from The Guardian API.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of parsed news articles
        """
        if not self.is_available:
            raise Exception(f"Provider {self.name} is not available: {self.last_error}")
            
        try:
            # Convert our category to Guardian section
            section = None
            if category:
                for s, c in self.section_to_category.items():
                    if c == category:
                        section = s
                        break
            
            raw_data = self._make_request(section)
            articles = []
            
            for item in raw_data.get('results', []):
                # Skip articles without required fields
                if not all(item.get(field) for field in ['webUrl', 'webTitle']):
                    continue
                    
                fields = item.get('fields', {})
                # Extract video information if available
                video_content = None
                if 'elements' in item:
                    for element in item['elements']:
                        if element.get('type') == 'video':
                            assets = element.get('assets', [])
                            for asset in assets:
                                if asset.get('type') == 'video':
                                    video_content = {
                                        'url': asset.get('file'),
                                        'mimeType': asset.get('mimeType'),
                                        'duration': asset.get('duration'),
                                        'width': asset.get('width'),
                                        'height': asset.get('height')
                                    }
                                    break
                
                article = {
                    'title': item['webTitle'],
                    'url': item['webUrl'],
                    'description': fields.get('standfirst', ''),
                    'content': fields.get('body', ''),
                    'publishedAt': self._parse_date(fields.get('lastModified', '')),
                    'source': {
                        'id': 'guardian',
                        'name': 'The Guardian'
                    },
                    'author': None,  # Guardian API doesn't provide author info in basic fields
                    'imageUrl': fields.get('thumbnail', None),
                    'category': self._determine_category(item),
                    'video': video_content,  # Add video content if available
                    'hasVideo': video_content is not None
                }
                
                articles.append(article)
                
            return articles
            
        except Exception as e:
            self.is_available = False
            self.last_error = str(e)
            logger.error(f"Error fetching news from Guardian: {e}")
            raise
