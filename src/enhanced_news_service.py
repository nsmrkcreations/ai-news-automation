"""
Enhanced News Service with web scraping and AI summarization
"""
import yaml
import logging
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import our modules
from sources import RSSAdapter
from scraper import HTTPClient
from summarizer import OllamaSummarizer
from publisher import JSONPublisher, GitPublisher

class EnhancedNewsService:
    """Enhanced news service with AI summarization"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        self.config = self.load_config(config_path)
        self.setup_logging()
        
        # Initialize components
        self.http_client = HTTPClient(
            user_agent=self.config['user_agent'],
            rate_limit_delay=self.config['rate_limit_delay']
        )
        
        self.summarizer = OllamaSummarizer(self.config['ollama'])
        
        self.json_publisher = JSONPublisher(
            output_dir=self.config['output_dir'],
            filename=self.config['json_filename']
        )
        
        if self.config.get('git'):
            self.git_publisher = GitPublisher(**self.config['git'])
        else:
            self.git_publisher = None
        
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            raise
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        
        # Create logs directory
        log_file = log_config.get('file', 'logs/news_service.log')
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    async def run(self):
        """Main execution method"""
        self.logger.info("Starting Enhanced News Service")
        
        try:
            # Fetch articles from all sources
            all_articles = await self.fetch_all_articles()
            
            if not all_articles:
                self.logger.warning("No articles fetched")
                return
            
            self.logger.info(f"Fetched {len(all_articles)} new articles")
            
            # Load existing articles first to filter out duplicates before AI processing
            existing_articles = self.json_publisher.load_existing()
            self.logger.info(f"Found {len(existing_articles)} existing articles")
            
            # Filter out articles that already exist (before AI processing)
            existing_ids = {article.get('id') for article in existing_articles}
            existing_urls = {article.get('source_url') for article in existing_articles if article.get('source_url')}
            
            new_articles = []
            for article in all_articles:
                article_id = article.get('id')
                article_url = article.get('source_url')
                
                if article_id not in existing_ids and article_url not in existing_urls:
                    new_articles.append(article)
            
            self.logger.info(f"Found {len(new_articles)} truly new articles (filtered {len(all_articles) - len(new_articles)} duplicates)")
            
            if not new_articles:
                self.logger.info("No new articles to process")
                return
            
            # Summarize only NEW articles with AI
            summarized_articles = await self.summarize_articles(new_articles)
            
            # Merge with existing articles
            merged_articles = self.json_publisher.merge_articles(
                summarized_articles, existing_articles, max_articles=500
            )
            
            # Publish to JSON (enhanced format)
            success = self.json_publisher.publish(merged_articles)
            
            # Also create backward-compatible news.json
            if success:
                self.create_legacy_json(merged_articles)
                self.logger.info(f"Published {len(merged_articles)} articles to both formats")
                
                # Commit to git if configured
                if self.git_publisher:
                    commit_msg = f"Update news: {len(summarized_articles)} new articles - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    self.git_publisher.commit_and_push(
                        message=commit_msg,
                        files=[self.config['output_dir'] + '/' + self.config['json_filename']]
                    )
                
                # Print stats
                stats = self.json_publisher.get_stats()
                self.logger.info(f"Total articles: {stats['total']}")
                self.logger.info(f"Categories: {stats['categories']}")
                
            else:
                self.logger.error("Failed to publish articles")
                
        except Exception as e:
            self.logger.error(f"Error in main execution: {str(e)}")
            raise
    
    async def fetch_all_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from all configured sources"""
        all_articles = []
        
        # Use ThreadPoolExecutor for concurrent fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['concurrency']) as executor:
            # Submit tasks for each source
            future_to_source = {}
            
            for source_config in self.config['sources']:
                future = executor.submit(self.fetch_from_source, source_config)
                future_to_source[future] = source_config['id']
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_source):
                source_id = future_to_source[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    self.logger.info(f"Fetched {len(articles)} articles from {source_id}")
                except Exception as e:
                    self.logger.error(f"Error fetching from {source_id}: {str(e)}")
        
        return all_articles
    
    def fetch_from_source(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch articles from a single source"""
        articles = []
        
        try:
            # Create adapter based on discovery method
            if source_config['discovery'] == 'rss':
                adapter = RSSAdapter(source_config, self.config['user_agent'])
            else:
                self.logger.warning(f"Unsupported discovery method: {source_config['discovery']}")
                return articles
            
            # Discover URLs
            urls = list(adapter.discover())
            self.logger.info(f"Discovered {len(urls)} URLs from {source_config['id']}")
            
            # Fetch and parse articles
            for url in urls:
                try:
                    # Fetch HTML
                    html = adapter.fetch(url)
                    if not html:
                        continue
                    
                    # Parse article
                    parsed_data = adapter.parse(html, url)
                    if not parsed_data or not parsed_data.get('title'):
                        continue
                    
                    # Normalize article
                    article = adapter.normalize_article(parsed_data, url)
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {url}: {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error fetching from source {source_config['id']}: {str(e)}")
        
        return articles
    
    async def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize articles using AI or fallback"""
        summarized = []
        
        # Check if AI is enabled
        ai_enabled = self.config.get('ollama', {}).get('enabled', True)
        max_ai_articles = self.config.get('ollama', {}).get('max_articles_per_run', 20)  # Limit AI processing
        
        if not ai_enabled:
            self.logger.info(f"AI summarization disabled, using fallback for {len(articles)} articles")
            # Process articles with fallback summaries
            for article in articles:
                ai_result = self.summarizer.summarize_article(article)
                article.update({
                    'summary': ai_result.get('summary', ''),
                    'keywords': ai_result.get('keywords', []),
                    'ai_insights': ai_result.get('insights', ''),
                    'ai_enhanced': ai_result.get('ai_enhanced', False)
                })
                summarized.append(article)
        else:
            # Limit AI processing to most recent articles only
            articles_for_ai = articles[:max_ai_articles] if len(articles) > max_ai_articles else articles
            articles_for_fallback = articles[max_ai_articles:] if len(articles) > max_ai_articles else []
            
            self.logger.info(f"Starting AI summarization for {len(articles_for_ai)} articles (limited from {len(articles)} total)")
            if articles_for_fallback:
                self.logger.info(f"Using fallback for remaining {len(articles_for_fallback)} articles")
            
            # Process AI articles with timeout protection
            ai_processed = 0
            for article in articles_for_ai:
                try:
                    self.logger.info(f"AI processing {ai_processed + 1}/{len(articles_for_ai)}: {article.get('title', 'Unknown')[:30]}...")
                    
                    # Use timeout for individual article processing
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("AI processing timeout")
                    
                    # Set timeout for this article (Windows doesn't support signal, so use try/except)
                    try:
                        ai_result = self.summarizer.summarize_article(article)
                        article.update({
                            'summary': ai_result.get('summary', ''),
                            'keywords': ai_result.get('keywords', []),
                            'ai_insights': ai_result.get('insights', ''),
                            'ai_enhanced': ai_result.get('ai_enhanced', False)
                        })
                        summarized.append(article)
                        ai_processed += 1
                        
                        # Shorter delay for faster processing
                        import time
                        time.sleep(0.5)
                        
                    except Exception as ai_error:
                        self.logger.warning(f"AI failed for article, using fallback: {str(ai_error)}")
                        # Use fallback immediately
                        fallback_result = self.summarizer.fallback_summary(article)
                        article.update({
                            'summary': fallback_result.get('summary', ''),
                            'keywords': fallback_result.get('keywords', []),
                            'ai_insights': fallback_result.get('insights', ''),
                            'ai_enhanced': False
                        })
                        summarized.append(article)
                    
                except Exception as e:
                    self.logger.error(f"Error processing article: {str(e)}")
                    # Use fallback for this article
                    fallback_result = self.summarizer.fallback_summary(article)
                    article.update({
                        'summary': fallback_result.get('summary', ''),
                        'keywords': fallback_result.get('keywords', []),
                        'ai_insights': fallback_result.get('insights', ''),
                        'ai_enhanced': False
                    })
                    summarized.append(article)
            
            # Process remaining articles with fallback
            for article in articles_for_fallback:
                fallback_result = self.summarizer.fallback_summary(article)
                article.update({
                    'summary': fallback_result.get('summary', ''),
                    'keywords': fallback_result.get('keywords', []),
                    'ai_insights': fallback_result.get('insights', ''),
                    'ai_enhanced': False
                })
                summarized.append(article)
        
        ai_enhanced_count = sum(1 for article in summarized if article.get('ai_enhanced', False))
        self.logger.info(f"Completed processing {len(summarized)} articles ({ai_enhanced_count} AI-enhanced, {len(summarized) - ai_enhanced_count} fallback)")
        return summarized
    
    def create_legacy_json(self, articles: List[Dict[str, Any]]):
        """Create backward-compatible news.json file"""
        try:
            import json
            legacy_articles = []
            
            for article in articles:
                # Convert enhanced format to legacy format
                legacy_article = {
                    'id': article.get('id', ''),
                    'title': article.get('title', ''),
                    'description': article.get('summary', article.get('excerpt', '')),
                    'content': article.get('content_snippet', ''),
                    'publishedAt': article.get('published_at', ''),
                    'source': {
                        'name': article.get('source', 'Unknown Source')
                    },
                    'author': article.get('author'),
                    'url': article.get('source_url', ''),
                    'urlToImage': article.get('media', [{}])[0].get('url') if article.get('media') else None,
                    'category': article.get('category', 'general'),
                    'aiEnhanced': article.get('ai_enhanced', False)
                }
                legacy_articles.append(legacy_article)
            
            # Write legacy format
            legacy_path = Path(self.config['output_dir']) / 'news.json'
            with open(legacy_path, 'w', encoding='utf-8') as f:
                json.dump(legacy_articles, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Created legacy news.json with {len(legacy_articles)} articles")
            
        except Exception as e:
            self.logger.error(f"Error creating legacy JSON: {str(e)}")

def main():
    """Main entry point"""
    service = EnhancedNewsService()
    asyncio.run(service.run())

if __name__ == '__main__':
    main()