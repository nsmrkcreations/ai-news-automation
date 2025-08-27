import os
import json
from datetime import datetime
from aggregator import NewsAggregator

def update_news_data():
    # Initialize news aggregator with API key
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        raise ValueError("NEWS_API_KEY environment variable is not set")
    aggregator = NewsAggregator(api_key)

    # Create data directory if it doesn't exist
    os.makedirs('public/data', exist_ok=True)

    # Load existing articles to check for duplicates
    existing_articles = []
    if os.path.exists('public/data/news.json'):
        try:
            with open('public/data/news.json', 'r', encoding='utf-8') as f:
                existing_articles = json.load(f)
        except:
            pass

    # Get existing URLs
    existing_urls = {article['url'] for article in existing_articles}

    # Fetch new articles
    new_articles = aggregator.fetch_trending()
    formatted_new_articles = []
    
    # Format and filter out duplicates
    for article in new_articles:
        if article['url'] not in existing_urls:
            formatted = aggregator.format_for_static_site([article])[0]
            formatted_new_articles.append(formatted)
            existing_urls.add(article['url'])

    # Combine new and existing articles, keep most recent 20
    all_articles = formatted_new_articles + existing_articles
    all_articles = all_articles[:20]

    # Save to JSON file
    with open('public/data/news.json', 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"Updated news data with {len(all_articles)} articles")

if __name__ == "__main__":
    update_news_data()
