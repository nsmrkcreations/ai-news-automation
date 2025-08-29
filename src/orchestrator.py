#!/usr/bin/env python
import os
import sys
import time
import schedule
from datetime import datetime
from threading import Thread

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logger import setup_logger
from update_news import update_news

logger = setup_logger()

# Initialize environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if not NEWS_API_KEY:
    logger.error("NEWS_API_KEY environment variable is not set")
    sys.exit(1)

def update_cycle():
    """Update news data"""
    try:
        logger.info("Starting news update cycle...")
        if update_news():
            logger.info("News update completed successfully")
        else:
            logger.error("News update failed")
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
    
    if os.environ.get('RUN_ONCE') == 'true':
        # Just run the update once (for CI/CD)
        update_cycle()
    else:
        # Run the scheduler for continuous updates
        run_scheduler()
