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

        # Load existing articles to check for duplicates
        existing_articles = []
        if os.path.exists('public/data/news.json'):
            try:
                with open('public/data/news.json', 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing articles: {str(e)}")

        # Get existing URLs
        existing_urls = {article['url'] for article in existing_articles}

        # Fetch new articles
        new_articles = aggregator.fetch_trending()
        formatted_new_articles = []
        
        # Format and filter out duplicates
        for article in new_articles:
            if article['url'] not in existing_urls:
                # Ensure article has publishedAt
                if 'publishedAt' not in article:
                    article['publishedAt'] = datetime.now(timezone.utc).isoformat() + 'Z'
                formatted = aggregator.format_for_static_site([article])[0]
                # Double check publishedAt is present
                if 'publishedAt' not in formatted:
                    formatted['publishedAt'] = article['publishedAt']
                formatted_new_articles.append(formatted)
                existing_urls.add(article['url'])

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
