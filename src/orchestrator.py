"""
Main orchestrator for the news automation system
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from .core.logger import get_logger
from .core.news_fetcher import NewsFetcher
from .core.ai_generator import AIGenerator
from .core.cache import CacheManager, EnhancedCache
from .core.rate_limiter import RateLimiter
from .core.error_monitor import ErrorMonitor

class NewsOrchestrator:
    def __init__(self):
        # Set up logging
        self.logger = get_logger(__name__)
        
        try:
            # Initialize components with retry logic
            self.news_fetcher = self._init_with_retry(NewsFetcher)
            self.ai_generator = self._init_with_retry(AIGenerator)
            self.cache = self._init_with_retry(EnhancedCache)
            
            # Set up rate limiter with configurable limits
            daily_limit = int(os.getenv("DAILY_API_LIMIT", "100"))
            self.rate_limiter = RateLimiter(
                calls=daily_limit,
                time_window=86400  # 24 hours in seconds
            )
            
            # Set up error monitoring with persistence
            self.error_monitor = ErrorMonitor()
            
            # Initialize health state
            self.last_successful_run = None
            self.consecutive_failures = 0
            self.health_status = "initializing"
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {str(e)}")
            raise
            
    def _init_with_retry(self, component_class, max_retries=3):
        """Initialize a component with retry logic.
        
        Args:
            component_class: Class to instantiate
            max_retries: Maximum number of retry attempts
        """
        for attempt in range(max_retries):
            try:
                return component_class()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                self.logger.warning(
                    f"Failed to initialize {component_class.__name__}, "
                    f"attempt {attempt + 1}/{max_retries}: {str(e)}"
                )
                time.sleep(2 ** attempt)  # Exponential backoff
        
    def process_news(self, category: str = None) -> List[Dict[Any, Any]]:
        """
        Main process to fetch, summarize, and store news with robust error handling
        and fallback mechanisms.
        
        Args:
            category: Optional category to filter news by
            
        Returns:
            List of processed news articles
        """
        start_time = datetime.now()
        self.health_status = "processing"
        
        try:
            # Check cache first
            cache_key = category or 'all'
            cached_news = self.cache.get_news(cache_key)
            
            try:
                # Validate cached data
                if cached_news and self._validate_news_data(cached_news):
                    self.logger.info(f"Returning valid cached news for category: {category or 'all'}")
                    self._update_health_metrics(True)
                    return cached_news
            except Exception as cache_error:
                self.logger.warning(f"Cache validation failed: {str(cache_error)}")

            # Check rate limit with burst allowance
            if not self.rate_limiter.try_acquire():
                self.logger.warning("Rate limit reached, attempting fallback options")
                
                # Try to use slightly expired cache if available
                if cached_news:
                    self.logger.info("Using expired cache due to rate limit")
                    return cached_news
                
                # If no cache, try fallback provider
                return self._process_news_fallback(category)

            # Fetch raw news with retries
            raw_articles = self._fetch_with_retry(category)
            
            if not raw_articles:
                self.error_monitor.log_error(
                    'news_fetch',
                    'No articles returned from any provider',
                    {'category': category}
                )
                # Return expired cache as last resort
                return cached_news if cached_news else []

            processed_articles = []
            for article in raw_articles:
                try:
                    # Process article with AI
                    summary, detected_category, is_breaking, ai_enhanced = self.ai_generator.summarize_article(article)

                    # Use the category detected by the AI generator, which follows our priority logic
                    # The AI generator already handles API category > AI detection > keyword analysis
                    final_category = detected_category

                    # Create standardized article format
                    title = article.get('title')
                    if ai_enhanced:
                        title = f"✐⭑ {title}"  # Add edit with star indicator from icon set

                    processed_article = {
                        'title': title,
                        'description': summary or article.get('description'),
                        'url': article.get('url'),
                        'urlToImage': article.get('urlToImage', '/images/placeholder.jpg'),
                        'publishedAt': article.get('publishedAt'),
                        'source': {
                            'id': article.get('source', {}).get('id'),
                            'name': article.get('source', {}).get('name', 'Unknown Source')
                        },
                        'category': detected_category,  # Use the category determined by AI generator
                        'aiEnhanced': ai_enhanced,  # Add AI enhancement flag
                        'isBreaking': is_breaking or self._is_breaking_news(article.get('publishedAt')),
                        'fetchedAt': datetime.now().isoformat()
                    }

                    # Validate article before adding
                    if self._validate_article(processed_article):
                        processed_articles.append(processed_article)
                        self.logger.info(f"Processed article: {article.get('title')} [{final_category}]")
                    else:
                        self.error_monitor.log_error(
                            'article_validation',
                            'Article failed validation',
                            {'article': article.get('title'), 'category': final_category}
                        )

                except Exception as e:
                    self.error_monitor.log_error(
                        'article_processing',
                        str(e),
                        {'article': article.get('title'), 'category': category}
                    )
                    continue
                    
            # Update cache with new articles
            if processed_articles:
                self.cache.set(cache_key, processed_articles)
                self._update_health_metrics(True)
                
            return processed_articles
            
        except Exception as e:
            self.logger.error(f"News processing failed: {str(e)}")
            self._update_health_metrics(False)
            self.consecutive_failures += 1
            raise

    def _validate_article(self, article: Dict[str, Any]) -> bool:
        """Validate a single article's structure and content."""
        try:
            from .core.validation import validate_article
            return validate_article(article)
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
            
    def _validate_news_data(self, articles: List[Dict[str, Any]]) -> bool:
        """Validate a list of articles."""
        try:
            from .core.validation import validate_news_data
            return validate_news_data(articles)
        except Exception as e:
            self.logger.error(f"News data validation error: {str(e)}")
            return False
            
    def _fetch_with_retry(self, category: str = None, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Fetch news with retry logic."""
        for attempt in range(max_retries):
            try:
                articles = self.news_fetcher.fetch_news(category)
                if articles:
                    return articles
            except Exception as e:
                self.logger.warning(
                    f"Fetch attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
                
        return []
        
    def _update_health_metrics(self, success: bool):
        """Update health monitoring metrics."""
        self.last_successful_run = datetime.now() if success else self.last_successful_run
        
        if success:
            self.consecutive_failures = 0
            self.health_status = "healthy"
        else:
            self.consecutive_failures += 1
            if self.consecutive_failures >= 3:
                self.health_status = "degraded"
            elif self.consecutive_failures >= 5:
                self.health_status = "failing"
    
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
        Update the frontend news.json file with proper sorting and deduplication
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
            
            # Create a dictionary of articles by URL for quick lookup
            articles_by_url = {}
            
            # Process new articles first (they take precedence)
            for article in articles:
                url = article['url']
                articles_by_url[url] = article
            
            # Add existing articles if not already present
            for article in existing_articles:
                url = article['url']
                if url not in articles_by_url:
                    articles_by_url[url] = article
            
            # Convert back to list and sort by publishedAt date (newest first)
            updated_articles = list(articles_by_url.values())
            updated_articles.sort(
                key=lambda x: datetime.fromisoformat(x['publishedAt'].replace('Z', '+00:00')),
                reverse=True
            )
            
            # Keep only the last 100 articles to prevent the file from growing too large
            updated_articles = updated_articles[:100]
            
            # Save updated articles
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(updated_articles, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error updating frontend data: {str(e)}")
