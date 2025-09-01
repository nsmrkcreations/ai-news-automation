"""
Quick test for news updates
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_news(category=None):
    """Fetch news from NewsAPI"""
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        print("Error: NEWS_API_KEY not found in environment variables")
        return []

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'apiKey': api_key,
        'language': 'en',
        'pageSize': 20
    }
    
    if category:
        params['category'] = category

    try:
        print(f"Fetching news for category: {category or 'all'}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        print(f"Found {len(articles)} articles")
        return articles
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []

def save_news(articles, category=None):
    """Save news to JSON file"""
    output_dir = Path("public/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "news.json"

    # Process articles
    processed_articles = []
    for article in articles:
        processed_article = {
            'title': article.get('title'),
            'description': article.get('description'),
            'url': article.get('url'),
            'urlToImage': article.get('urlToImage'),
            'publishedAt': article.get('publishedAt'),
            'source': article.get('source', {'name': 'Unknown'}),
            'category': category or 'general',
            'fetchedAt': datetime.now().isoformat()
        }
        processed_articles.append(processed_article)

    # Load existing articles if any
    existing_articles = []
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_articles = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Could not read existing news.json")

    # Combine articles, avoid duplicates using URL as key
    seen_urls = set()
    final_articles = []

    # Add new articles first
    for article in processed_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            final_articles.append(article)

    # Add existing articles if not duplicate
    for article in existing_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            final_articles.append(article)

    # Sort by publishedAt date (newest first)
    final_articles.sort(
        key=lambda x: datetime.fromisoformat(x['publishedAt'].replace('Z', '+00:00')),
        reverse=True
    )

    # Keep only the latest 100 articles
    final_articles = final_articles[:100]

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_articles, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(final_articles)} articles to {output_file}")

def main():
    """Main function"""
    print("\n=== Starting News Update ===")
    categories = os.getenv('NEWS_CATEGORIES', '').split(',')
    if not categories or not categories[0]:
        categories = ['technology', 'business', 'science']

    all_articles = []
    for category in categories:
        category = category.strip().lower()
        articles = fetch_news(category)
        if articles:
            save_news(articles, category)
            all_articles.extend(articles)

    print(f"\n✅ Update complete! Total articles: {len(all_articles)}")

if __name__ == "__main__":
    main()
