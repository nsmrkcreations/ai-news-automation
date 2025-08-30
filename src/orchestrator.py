"""
Main orchestrator for the news automation system
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from core.news_fetcher import NewsFetcher
from core.ai_generator import AIGenerator
from core.cache import CacheManager, EnhancedCache
from core.rate_limiter import RateLimiter
from core.error_monitor import ErrorMonitor

class NewsOrchestrator:
    def __init__(self):
        # Set up logging
        self.logger = setup_logger()
        
        # Initialize components
        self.news_fetcher = NewsFetcher()
        self.ai_generator = AIGenerator()
        self.cache = EnhancedCache()  # Using enhanced cache instead of basic Cache
        
        # Set up rate limiter (100 calls per day for NewsAPI free tier)
        self.rate_limiter = RateLimiter(calls=100, time_window=86400)
        
        # Set up error monitoring
        self.error_monitor = ErrorMonitor()
        
    def process_news(self, category: str = None) -> List[Dict[Any, Any]]:
        """
        Main process to fetch, summarize, and store news
        """
        try:
            # Check cache first
            cache_key = f"news_{category or 'all'}"
            cached_news = self.cache.get(cache_key)
            if cached_news:
                self.logger.info(f"Returning cached news for category: {category or 'all'}")
                return cached_news

            # Check rate limit before making API call
            if not self.rate_limiter.try_acquire():
                self.error_monitor.log_error(
                    'rate_limit',
                    'Rate limit exceeded for news API',
                    {'category': category}
                )
                # Return cached data if available, even if expired
                return cached_news if cached_news else []

            # Check if Ollama is available
            if not self.ai_generator.check_ollama_status():
                self.error_monitor.log_error(
                    'ai_service',
                    'Ollama is not available',
                    {'category': category}
                )
                return self._process_news_fallback(category)

            # Fetch raw news
            raw_articles = self.news_fetcher.fetch_news(category)
            if not raw_articles:
                self.error_monitor.log_error(
                    'news_fetch',
                    'No articles returned from news API',
                    {'category': category}
                )
                return []

            processed_articles = []
            for article in raw_articles:
                try:
                    # Process article with AI
                    summary, detected_category, is_breaking = self.ai_generator.summarize_article(article)

                    # Use provided category if available, otherwise use AI-detected category
                    final_category = category if category else detected_category

                    # Create standardized article format
                    processed_article = {
                        'title': article.get('title'),
                        'description': summary or article.get('description'),
                        'url': article.get('url'),
                        'urlToImage': article.get('urlToImage', 'images/fallback.jpg'),
                        'publishedAt': article.get('publishedAt'),
                        'source': article.get('source', {}).get('name'),
                        'category': final_category,
                        'isBreaking': is_breaking or self._is_breaking_news(article.get('publishedAt'))
                    }

                    processed_articles.append(processed_article)
                    self.logger.info(f"Processed article: {article.get('title')} [{final_category}]")

                except Exception as e:
                    self.error_monitor.log_error(
                        'article_processing',
                        str(e),
                        {'article': article.get('title'), 'category': category}
                    )
                    continue

            # Cache the processed articles
            if processed_articles:
                expiry = timedelta(minutes=15) if any(a['isBreaking'] for a in processed_articles) else timedelta(hours=1)
                self.cache.set(cache_key, processed_articles, expiry=expiry)

            return processed_articles

        except Exception as e:
            self.error_monitor.log_error(
                'process_news',
                str(e),
                {'category': category}
            )
            return []
        
        # Cache the processed articles
        if processed_articles:
            self.cache.save_news(category or 'general', processed_articles)
            self._update_frontend_data(processed_articles)
            
        return processed_articles
    
    def _process_news_fallback(self, category: str = None) -> List[Dict[Any, Any]]:
        """
        Process news without AI when Ollama is not available
        """
        self.logger.warning("Processing news in fallback mode (no AI)")
        raw_articles = self.news_fetcher.fetch_news(category)
        
        processed_articles = []
        for article in raw_articles:
            try:
                processed_article = {
                    'title': article.get('title'),
                    'description': article.get('description'),
                    'url': article.get('url'),
                    'urlToImage': article.get('urlToImage', 'images/fallback.jpg'),
                    'publishedAt': article.get('publishedAt'),
                    'source': article.get('source', {}).get('name'),
                    'category': category or 'general',
                    'isBreaking': self._is_breaking_news(article.get('publishedAt'))
                }
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                self.logger.error(f"Error in fallback processing: {str(e)}")
                continue
                
        return processed_articles
    
    def _is_breaking_news(self, published_at: str) -> bool:
        """
        Determine if news is breaking based on publish time
        """
        if not published_at:
            return False
            
        try:
            published = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            time_diff = datetime.now().astimezone() - published
            # Consider news breaking if it's less than 2 hours old
            return time_diff.total_seconds() < 7200
        except Exception:
            return False
            
    def _update_frontend_data(self, articles: List[Dict[Any, Any]]):
        """
        Update the frontend news.json file
        """
        output_dir = "public/data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, "news.json")
        
        try:
            # Load existing articles if any
            existing_articles = []
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            
            # Combine new articles with existing ones, avoiding duplicates
            seen_urls = set()
            updated_articles = []
            
            # Add new articles first
            for article in articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    updated_articles.append(article)
            
            # Add existing articles if not duplicate
            for article in existing_articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    updated_articles.append(article)
            
            # Save updated articles
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(updated_articles, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error updating frontend data: {str(e)}")
