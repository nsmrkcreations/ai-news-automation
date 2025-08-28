import os
import sys
import time
import schedule
from flask import Flask
from datetime import datetime

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.news_fetcher import NewsFetcher
from src.core.logger import setup_logger
from src.update_news import update_news_data

# Initialize Flask app
app = Flask(__name__, static_folder='../public', static_url_path='')
news_fetcher = NewsFetcher()
logger = setup_logger()

# Initialize environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if not NEWS_API_KEY:
    logger.error("NEWS_API_KEY environment variable is not set")
    sys.exit(1)

def update_cycle():
    """Update news data and serve the Flask app"""
    try:
        logger.info("Starting news update cycle...")
        update_news_data()
        logger.info("News update completed")
    except Exception as e:
        logger.error(f"Error during update cycle: {e}")

def run_scheduler():
    """Run the scheduler for periodic updates"""
    # Update immediately on start
    update_cycle()
    
    # Schedule updates every hour during peak hours (8 AM - 10 PM)
    for hour in range(8, 23):
        schedule.every().day.at(f"{hour:02d}:00").do(update_cycle)

    # Schedule updates every 3 hours during off-peak hours
    for hour in [0, 3, 6]:
        schedule.every().day.at(f"{hour:02d}:00").do(update_cycle)

    logger.info("Starting scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logger.info("AI News Automation starting...")
    
    # Start the Flask server in a separate thread
    from threading import Thread
    port = int(os.environ.get('PORT', 5000))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False)).start()
    
    # Run the scheduler in the main thread
    run_scheduler()
