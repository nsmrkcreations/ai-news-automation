#!/usr/bin/env python3
"""
Local Backend Service for AI News Automation
Runs on your personal computer to fetch and process news
"""

import os
import sys
import time
import schedule
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from core.news_fetcher import NewsFetcher
from core.ai_generator import AIGenerator
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LocalNewsService:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.ai_generator = AIGenerator()
        
    def update_news(self):
        """Fetch and process news, update frontend data"""
        try:
            logger.info("🔄 Starting news update...")
            
            # Categories to fetch
            categories = ['technology', 'business', 'science', 'general']
            all_articles = []
            
            for category in categories:
                try:
                    logger.info(f"📰 Fetching {category} news...")
                    articles = self.news_fetcher.fetch_news(category)
                    
                    for article in articles[:5]:  # Limit to 5 per category
                        try:
                            # Check if AI is available
                            if self.ai_generator.check_ollama_status():
                                summary, detected_category, is_breaking = self.ai_generator.summarize_article(article)
                            else:
                                logger.warning("⚠️ Ollama not available, using original descriptions")
                                summary = article.get('description', '')
                                detected_category = category
                                is_breaking = False
                            
                            processed_article = {
                                'title': article.get('title'),
                                'description': summary or article.get('description'),
                                'url': article.get('url'),
                                'urlToImage': article.get('urlToImage'),
                                'publishedAt': article.get('publishedAt'),
                                'source': article.get('source', {}).get('name'),
                                'category': detected_category or category,
                                'isBreaking': is_breaking
                            }
                            
                            all_articles.append(processed_article)
                            logger.info(f"✅ Processed: {article.get('title')[:50]}...")
                            
                        except Exception as e:
                            logger.error(f"❌ Error processing article: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"❌ Error fetching {category}: {e}")
                    continue
            
            # Save to frontend
            if all_articles:
                self.save_to_frontend(all_articles)
                logger.info(f"✅ Updated {len(all_articles)} articles")
            else:
                logger.warning("⚠️ No articles processed")
                
        except Exception as e:
            logger.error(f"❌ News update failed: {e}")
    
    def save_to_frontend(self, articles):
        """Save articles to frontend data file"""
        output_dir = Path("public/data")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "news.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Saved to {output_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save: {e}")

def main():
    """Main service loop"""
    print("🚀 Starting AI News Automation Backend Service")
    print("📍 Running locally on your computer")
    print("🌐 Frontend will be deployed to GitHub Pages")
    print("=" * 50)
    
    # Check environment
    if not os.getenv('NEWS_API_KEY') or os.getenv('NEWS_API_KEY') == 'YOUR_NEWSAPI_KEY_HERE':
        print("⚠️  WARNING: Please set your NEWS_API_KEY in .env file")
        print("   Get your key from: https://newsapi.org/")
        return
    
    service = LocalNewsService()
    
    # Schedule updates
    schedule.every(30).minutes.do(service.update_news)  # Every 30 minutes
    schedule.every().hour.at(":00").do(service.update_news)  # Every hour
    
    # Run initial update
    print("🔄 Running initial news update...")
    service.update_news()
    
    print("⏰ Scheduled updates every 30 minutes")
    print("🔄 Press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n👋 Backend service stopped")

if __name__ == "__main__":
    main()
