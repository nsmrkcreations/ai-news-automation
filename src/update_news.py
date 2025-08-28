from flask import Flask, jsonify, request
from datetime import datetime, timezone
import os
import json
from core.news_fetcher import NewsFetcher
from core.logger import setup_logger
from aggregator import NewsAggregator

app = Flask(__name__, static_folder='../public', static_url_path='')
news_fetcher = NewsFetcher()
logger = setup_logger()

def update_news_data():
    # Initialize news aggregator with API key
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        logger.warning("NEWS_API_KEY environment variable is not set. Skipping news fetch.")
        return
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

    print(f"Updated news data with {len(all_articles)} articles")

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/api/news')
def get_news():
    """Get news articles since a given timestamp"""
    try:
        since = request.args.get('since', 0, type=float)
        articles = news_fetcher.get_news_since(since)
        return jsonify(articles)
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/news/categories/<category>')
def get_news_by_category(category):
    """Get news articles for a specific category"""
    try:
        articles = news_fetcher.get_news_by_category(category)
        return jsonify(articles)
    except Exception as e:
        logger.error(f"Error fetching category news: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # First update the news data
    update_news_data()
    
    # Then start the Flask server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
