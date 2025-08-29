import os
import json
from datetime import datetime, timezone
from core.logger import setup_logger
from core.news_aggregator import NewsAggregator

logger = setup_logger()

def update_news():
    """Update news data from the API"""
    try:
        # Initialize news aggregator
        aggregator = NewsAggregator()
        
        # Create data directory if it doesn't exist
        os.makedirs('public/data', exist_ok=True)

        # Create backup of existing news.json
        if os.path.exists('public/data/news.json'):
            try:
                import shutil
                shutil.copy2('public/data/news.json', 'public/data/news.json.bak')
            except Exception as e:
                logger.warning(f"Failed to create backup: {e}")

        # Load existing articles to check for duplicates
        existing_articles = []
        try:
            if os.path.exists('public/data/news.json'):
                with open('public/data/news.json', 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
        except Exception as e:
            logger.error(f"Error loading existing articles: {str(e)}")
            # Try to recover from backup
            if os.path.exists('public/data/news.json.bak'):
                try:
                    with open('public/data/news.json.bak', 'r', encoding='utf-8') as f:
                        existing_articles = json.load(f)
                    logger.info("Recovered articles from backup")
                except Exception as e:
                    logger.error(f"Failed to recover from backup: {e}")

        # Get existing URLs and ensure no duplicates
        existing_urls = {article.get('url', '') for article in existing_articles if article.get('url')}

        # Fetch new articles
        new_articles = aggregator.fetch_trending()
        formatted_new_articles = []
        
        # Format and filter out duplicates
        for article in new_articles:
            try:
                if article['url'] not in existing_urls:
                    # Validate required fields
                    required_fields = ['title', 'description', 'url']
                    if not all(field in article for field in required_fields):
                        logger.warning(f"Skipping article missing required fields: {article.get('url', 'unknown')}")
                        continue
                    
                    # Ensure article has publishedAt
                    if 'publishedAt' not in article:
                        article['publishedAt'] = datetime.now(timezone.utc).isoformat()
                    
                    # Format article with proper content length for reading time
                    formatted = aggregator.format_for_static_site([article])[0]
                    
                    # Calculate reading time based on content length
                    word_count = len(article.get('content', '').split()) + len(article.get('description', '').split())
                    reading_time = max(1, round(word_count / 200))  # Assume 200 words per minute
                    formatted['readingTime'] = f"{reading_time} min read"
                    
                    # Handle images properly
                    if 'urlToImage' in article and article['urlToImage']:
                        try:
                            image_path = aggregator.save_article_image(article['urlToImage'], article['url'])
                            formatted['image'] = image_path
                        except Exception as img_e:
                            logger.warning(f"Failed to save image for {article['url']}: {img_e}")
                            formatted['image'] = 'images/fallback.jpg'
                    else:
                        formatted['image'] = 'images/fallback.jpg'
                    
                    # Ensure all required fields are present with proper formatting
                    formatted['publishedAt'] = article['publishedAt'].rstrip('Z')  # Remove Z suffix if present
                    formatted['category'] = article.get('category', 'general').lower()
                    formatted['date'] = datetime.fromisoformat(formatted['publishedAt']).strftime('%B %d, %Y')
                    
                    formatted_new_articles.append(formatted)
                    existing_urls.add(article['url'])
                    logger.info(f"Successfully processed article: {article['title']}")
            except Exception as e:
                logger.error(f"Error formatting article: {str(e)}")
                continue

        # Combine new and existing articles, keep most recent 20
        all_articles = formatted_new_articles + existing_articles
        all_articles = all_articles[:20]

        # Ensure all articles have publishedAt
        now = datetime.now(timezone.utc).isoformat() + 'Z'
        for article in all_articles:
            if 'publishedAt' not in article:
                article['publishedAt'] = now
        
        # Save to JSON file
        with open('public/data/news.json', 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)

        logger.info(f"Updated news data with {len(all_articles)} articles")
        return True

    except Exception as e:
        logger.error(f"Error in update_news: {str(e)}")
        return False

if __name__ == "__main__":
    update_news()
