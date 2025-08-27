import os
from datetime import datetime
from pathlib import Path
import frontmatter
from typing import Dict, Any
import yaml
from .adsense_manager import AdSenseManager

class ContentManager:
    def __init__(self):
        self.site_dir = Path('./site')
        self.posts_dir = self.site_dir / '_posts'
        self.images_dir = self.site_dir / 'assets' / 'images'
        self.adsense = AdSenseManager()
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directories"""
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def create_post(self, content: Dict[str, Any]) -> Path:
        """Create a new Jekyll post"""
        date = datetime.now().strftime('%Y-%m-%d')
        slug = self._create_slug(content['title'])
        filename = f"{date}-{slug}.md"
        
        # Extract article content
        article_content = content['article']
        if isinstance(article_content, dict):
            # Handle new format with images and prepare for ads
            article_content = self.adsense.prepare_content_for_ads(article_content)
            post_content = article_content['content']
            image_info = article_content.get('image')
            
            # Prepare metadata
            metadata = {
                'title': content['title'],
                'date': datetime.now().isoformat(),
                'categories': content.get('categories', ['news']),
                'image': image_info['path'] if image_info else None,
                'image_alt': image_info['alt'] if image_info else None,
            }
            
            # Add video metadata if available
            if article_content.get('videos'):
                metadata['videos'] = []
                for video in article_content['videos']:
                    if video['type'] == 'video_file':
                        metadata['videos'].append({
                            'type': 'file',
                            'path': video['path'],
                            'title': video['title']
                        })
                    else:
                        metadata['videos'].append({
                            'type': video['type'],
                            'id': video['id'],
                            'embed_url': video['embed_url']
                        })
            
            # Create post with all metadata
            post = frontmatter.Post(
                post_content,
                **metadata
            )
        else:
            # Handle legacy format without images
            post = frontmatter.Post(
                article_content,
                title=content['title'],
                date=datetime.now().isoformat(),
                categories=content.get('categories', ['news']),
            tags=content.get('keywords', []),
            image=content.get('image', ''),
            layout='post',
            author='NewsSurgeAI'
        )
        
        filepath = self.posts_dir / filename
        with open(filepath, 'wb') as f:
            frontmatter.dump(post, f)
        
        return filepath

    def _create_slug(self, title: str) -> str:
        """Create a URL-friendly slug from title"""
        return title.lower().replace(' ', '-').replace('?', '').replace('!', '')

    def save_image(self, image_url: str, title: str) -> str:
        """Download and save an image"""
        # Implementation for image handling
        pass
