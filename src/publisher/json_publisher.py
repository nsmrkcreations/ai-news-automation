"""
JSON file publisher for news data
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONPublisher:
    """Publisher for JSON news data"""
    
    def __init__(self, output_dir: str, filename: str):
        self.output_dir = Path(output_dir)
        self.filename = filename
        self.output_path = self.output_dir / filename
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def publish(self, articles: List[Dict[str, Any]]) -> bool:
        """
        Publish articles to JSON file
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            # Sort articles by published date (newest first)
            sorted_articles = sorted(
                articles,
                key=lambda x: x.get('published_at', ''),
                reverse=True
            )
            
            # Add metadata
            output_data = {
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'total_articles': len(sorted_articles),
                'categories': list(set(article.get('category', 'general') for article in sorted_articles)),
                'sources': list(set(article.get('source', 'Unknown') for article in sorted_articles)),
                'articles': sorted_articles
            }
            
            # Write to file
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Published {len(sorted_articles)} articles to {self.output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing JSON: {str(e)}")
            return False
    
    def load_existing(self) -> List[Dict[str, Any]]:
        """
        Load existing articles from JSON file
        
        Returns:
            List of existing articles
        """
        try:
            if self.output_path.exists():
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('articles', [])
            return []
            
        except Exception as e:
            logger.error(f"Error loading existing JSON: {str(e)}")
            return []
    
    def merge_articles(self, new_articles: List[Dict[str, Any]], 
                      existing_articles: List[Dict[str, Any]], 
                      max_articles: int = 250) -> List[Dict[str, Any]]:
        """
        Merge new articles with existing ones, removing duplicates
        
        Args:
            new_articles: New articles to add
            existing_articles: Existing articles
            max_articles: Maximum number of articles to keep
            
        Returns:
            List of merged articles
        """
        # Create sets of existing article IDs and URLs for duplicate detection
        existing_ids = {article.get('id') for article in existing_articles}
        existing_urls = {article.get('source_url') for article in existing_articles if article.get('source_url')}
        
        # Filter out duplicates from new articles (by ID and URL)
        unique_new = []
        for article in new_articles:
            article_id = article.get('id')
            article_url = article.get('source_url')
            
            # Skip if duplicate ID or URL
            if article_id in existing_ids or article_url in existing_urls:
                continue
                
            unique_new.append(article)
            # Add to sets to prevent duplicates within new articles too
            existing_ids.add(article_id)
            if article_url:
                existing_urls.add(article_url)
        
        # Combine and sort
        all_articles = unique_new + existing_articles
        sorted_articles = sorted(
            all_articles,
            key=lambda x: x.get('published_at', ''),
            reverse=True
        )
        
        # Limit to max articles
        return sorted_articles[:max_articles]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about published articles
        
        Returns:
            Dict with statistics
        """
        try:
            articles = self.load_existing()
            if not articles:
                return {'total': 0, 'categories': {}, 'sources': {}}
            
            # Count by category
            categories = {}
            for article in articles:
                cat = article.get('category', 'general')
                categories[cat] = categories.get(cat, 0) + 1
            
            # Count by source
            sources = {}
            for article in articles:
                src = article.get('source', 'Unknown')
                sources[src] = sources.get(src, 0) + 1
            
            return {
                'total': len(articles),
                'categories': categories,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {'total': 0, 'categories': {}, 'sources': {}}