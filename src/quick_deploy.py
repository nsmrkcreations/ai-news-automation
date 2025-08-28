import os
import json
from datetime import datetime, timezone
from core.logger import setup_logger
from aggregator import NewsAggregator

logger = setup_logger()

def quick_deploy():
    """Quick deployment without starting the web server"""
    # Initialize news aggregator with API key
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.warning("NEWS_API_KEY environment variable is not set. Skipping news fetch.")
        return False

    try:
        # Create data directory
        os.makedirs('public/data', exist_ok=True)

        # Initialize with empty data if no existing file
        if not os.path.exists('public/data/news.json'):
            with open('public/data/news.json', 'w', encoding='utf-8') as f:
                json.dump([], f)

        logger.info("Deployment completed successfully")
        return True
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    if quick_deploy():
        print("✅ Deployment successful")
        exit(0)
    else:
        print("❌ Deployment failed")
        exit(1)
