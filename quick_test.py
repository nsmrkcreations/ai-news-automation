import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def merge_with_existing_news(new_articles, max_age_days=7):
    """Merge new articles with existing ones, keeping articles from last week"""
    news_file = 'public/data/news.json'
    existing_articles = []
    
    # Load existing articles if file exists
    if os.path.exists(news_file):
        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                existing_articles = json.load(f)
        except:
            existing_articles = []
    
    # Filter out articles older than max_age_days
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    filtered_existing = []
    
    for article in existing_articles:
        try:
            article_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
            if article_date >= cutoff_date:
                filtered_existing.append(article)
        except:
            # Keep articles with invalid dates for safety
            filtered_existing.append(article)
    
    # Combine new and existing articles
    all_articles = new_articles + filtered_existing
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    
    for article in all_articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    # Sort by publication date (newest first)
    unique_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
    
    # Limit to reasonable number (50 articles max)
    return unique_articles[:50]

# Fetch fresh news
api_key = os.getenv('NEWS_API_KEY')
url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=20&apiKey={api_key}"

try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        new_articles = data.get('articles', [])
        print(f"New articles fetched: {len(new_articles)}")
        
        # Merge with existing articles (keep 1 week of data)
        all_articles = merge_with_existing_news(new_articles, max_age_days=7)
        print(f"Total articles after merge: {len(all_articles)}")
        
        # Save merged data
        os.makedirs('public/data', exist_ok=True)
        with open('public/data/news.json', 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, indent=2, ensure_ascii=False)
        
        print("✅ Saved merged news data (1 week retention)")
        print(f"📊 Articles by age:")
        
        # Show age distribution
        now = datetime.now()
        age_counts = {'today': 0, 'yesterday': 0, 'this_week': 0}
        
        for article in all_articles:
            try:
                article_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                days_old = (now - article_date).days
                
                if days_old == 0:
                    age_counts['today'] += 1
                elif days_old == 1:
                    age_counts['yesterday'] += 1
                elif days_old <= 7:
                    age_counts['this_week'] += 1
            except:
                pass
        
        print(f"   Today: {age_counts['today']}")
        print(f"   Yesterday: {age_counts['yesterday']}")
        print(f"   This week: {age_counts['this_week']}")
        
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Failed: {e}")
