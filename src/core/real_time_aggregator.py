import asyncio
import json
import os
from datetime import datetime
from aiohttp import ClientSession
from core.logger import setup_logger
from core.news_aggregator import NewsAggregator

logger = setup_logger()

class RealTimeNewsAggregator(NewsAggregator):
    def __init__(self, api_key, update_callback=None):
        super().__init__(api_key)
        self.update_callback = update_callback
        self.last_update = {}  # Track last update per category
        self.active_connections = set()
        
    async def start_real_time_updates(self):
        """Start real-time news updates"""
        while True:
            try:
                new_articles = []
                for category in self.categories:
                    # Check each category
                    category_articles = await self.check_category_updates(category)
                    if category_articles:
                        new_articles.extend(category_articles)
                
                if new_articles:
                    # Format articles
                    formatted_articles = self.format_for_static_site(new_articles)
                    
                    # Update news.json
                    await self.update_news_file(formatted_articles)
                    
                    # Notify connected clients
                    if self.update_callback:
                        await self.update_callback(formatted_articles)
                
                # Adaptive delay based on time of day and update frequency
                delay = self.calculate_update_delay()
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in real-time updates: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def check_category_updates(self, category):
        """Check for updates in a specific category"""
        try:
            response = await self.api.async_get_top_headlines(
                language='en',
                country='us',
                category=category,
                page_size=5
            )
            
            if not response or 'articles' not in response:
                return []
            
            # Filter out articles we've already seen
            new_articles = []
            last_update = self.last_update.get(category, datetime.min)
            
            for article in response['articles']:
                pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                if pub_date > last_update:
                    if self.validate_article(article):
                        article['category'] = category
                        new_articles.append(article)
            
            if new_articles:
                self.last_update[category] = datetime.utcnow()
            
            return new_articles
            
        except Exception as e:
            logger.error(f"Error checking {category} updates: {e}")
            return []
    
    def validate_article(self, article):
        """Validate article has all required fields and check for breaking news"""
        required_fields = ['title', 'description', 'url', 'urlToImage', 'publishedAt']
        if not all(article.get(field) for field in required_fields):
            return False

        # Check for breaking news indicators
        breaking_keywords = ['breaking', 'urgent', 'just in', 'breaking news', 'emergency']
        title_lower = article['title'].lower()
        desc_lower = article['description'].lower()
        
        is_breaking = any(keyword in title_lower or keyword in desc_lower 
                         for keyword in breaking_keywords)
        
        article['isBreaking'] = is_breaking
        
        # Calculate article importance score
        article['importanceScore'] = self.calculate_importance_score(article)
        
        return True

    def calculate_importance_score(self, article):
        """Calculate article importance score based on various factors"""
        score = 0
        
        # Breaking news gets highest priority
        if article.get('isBreaking'):
            score += 100
            
        # Recent articles get higher priority
        pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
        hours_old = (datetime.utcnow() - pub_date).total_seconds() / 3600
        time_score = max(0, 24 - hours_old) * 2  # Higher score for newer articles
        score += time_score
        
        # Keywords indicating importance
        importance_keywords = [
            'exclusive', 'official', 'confirmed', 'update', 'live',
            'developing', 'announcement', 'major', 'critical'
        ]
        
        content = f"{article['title']} {article['description']}".lower()
        keyword_matches = sum(1 for keyword in importance_keywords if keyword in content)
        score += keyword_matches * 5
        
        return round(score, 2)
    
    async def update_news_file(self, new_articles):
        """Update the news.json file with new articles"""
        file_path = 'public/data/news.json'
        try:
            # Read existing articles
            existing_articles = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            
            # Combine and sort articles
            all_articles = new_articles + existing_articles
            all_articles.sort(key=lambda x: x['publishedAt'], reverse=True)
            
            # Keep only the most recent 50 articles
            all_articles = all_articles[:50]
            
            # Save updated articles
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating news file: {e}")
    
    def calculate_update_delay(self):
        """Calculate adaptive delay based on time of day"""
        hour = datetime.now().hour
        
        # More frequent updates during peak hours (8 AM - 10 PM)
        if 8 <= hour <= 22:
            return 300  # 5 minutes
        else:
            return 900  # 15 minutes during off-peak hours
