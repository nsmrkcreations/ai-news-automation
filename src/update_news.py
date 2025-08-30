"""
Script to update news data periodically
"""
import os
import schedule
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
from orchestrator import NewsOrchestrator

# Load environment variables
load_dotenv()

def update_all_news():
    """Update news for all categories"""
    try:
        orchestrator = NewsOrchestrator()
        categories = os.getenv('NEWS_CATEGORIES', '').split(',')
        
        # Update each category
        for category in categories:
            orchestrator.process_news(category.strip())
            
        logging.info(f"News update completed at {datetime.now().isoformat()}")
    except Exception as e:
        logging.error(f"Error updating news: {str(e)}")

def main():
    """Main function to schedule news updates"""
    # Initial update
    update_all_news()
    
    # Schedule regular updates
    news_interval = int(os.getenv('NEWS_UPDATE_INTERVAL', 30))
    schedule.every(news_interval).minutes.do(update_all_news)
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
