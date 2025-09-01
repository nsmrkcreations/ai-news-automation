import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_update_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_news_update():
    try:
        from src.update_news import update_all_news
        logger.info("Starting news update test...")
        update_all_news()
        logger.info("News update test completed successfully")
        return True
    except Exception as e:
        logger.error(f"News update test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("="*50)
    logger.info(f"Starting news update test at {datetime.now()}")
    success = test_news_update()
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Test {status} at {datetime.now()}")
    logger.info("="*50 + "\n")
