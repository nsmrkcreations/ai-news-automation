import os
from datetime import datetime
from pathlib import Path
import frontmatter
from typing import Dict, Any
import yaml

class ContentManager:
    def __init__(self):
        self.site_dir = Path('./site')
        self.posts_dir = self.site_dir / '_posts'
        self.images_dir = self.site_dir / 'assets' / 'images'
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
        
        post = frontmatter.Post(
            content['article'],
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
