"""
Script to update news data periodically
"""
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging
import json
from core.provider_manager import NewsProviderManager

# Configure logging
def setup_logging():
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/update_news.log', mode='a')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Load environment variables
load_dotenv()



def save_news(articles):
    """Save news to JSON file"""
    try:
        output_dir = Path("public/data")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "news.json"

        # Load existing articles if any
        existing_articles = []
        if output_file.exists():
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Could not read existing news.json")

        # Combine articles, avoid duplicates using URL as key
        seen_urls = set()
        final_articles = []

        # Add new articles first (they're already processed)
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                final_articles.append(article)

        # Add existing articles if not duplicate
        for article in existing_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                final_articles.append(article)

        # Sort by publishedAt date (newest first - latest to old)
        final_articles.sort(
            key=lambda x: datetime.fromisoformat(x['publishedAt'].replace('Z', '+00:00')) if x.get('publishedAt') else datetime.min,
            reverse=True
        )

        # Keep only the latest 250 articles
        final_articles = final_articles[:250]

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_articles, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(final_articles)} articles to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving news: {str(e)}")
        return False

def update_all_news():
    """Update news for all categories"""
    try:
        categories = os.getenv('NEWS_CATEGORIES', 'technology,business,science,sports,entertainment,politics,markets').split(',')
        
        successful_updates = []
        failed_updates = []
        all_articles = []
        
        # Create news provider manager
        provider_manager = NewsProviderManager()
        
        # Update each category
        for category in categories:
            category = category.strip().lower()
            try:
                logger.info(f"Updating news for category: {category}")
                articles = provider_manager.fetch_news(category)
                if articles:
                    all_articles.extend(articles)
                    successful_updates.append(category)
                    logger.info(f"Successfully updated {len(articles)} articles for {category}")
                else:
                    failed_updates.append(category)
                    logger.warning(f"No articles found for category: {category}")
            except Exception as category_error:
                failed_updates.append(category)
                logger.error(f"Error updating {category}: {str(category_error)}")
        
        # Save all articles
        if all_articles:
            if save_news(all_articles):
                logger.info("Successfully saved all articles")
            else:
                logger.error("Failed to save articles")
                return False

        # Log final status
        logger.info(f"News update completed at {datetime.now().isoformat()}")
        logger.info(f"Successful categories: {', '.join(successful_updates)}")
        if failed_updates:
            logger.warning(f"Failed categories: {', '.join(failed_updates)}")
            
        return len(failed_updates) == 0
            
    except Exception as e:
        logger.error(f"Critical error updating news: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_all_news()
    if not success:
        exit(1)
