import requests
from datetime import datetime
from newsapi import NewsApiClient
from core.logger import setup_logger
import time

logger = setup_logger()

class NewsAggregator:
    def __init__(self, api_key):
        self.api = NewsApiClient(api_key=api_key)
        self.categories = ['business', 'technology', 'general', 'sports', 'entertainment']
        self.request_delay = 1  # Delay between API requests in seconds

    def fetch_trending(self):
        all_articles = []
        seen_urls = set()  # Track unique URLs
        
        # We want 20 articles total, so distribute across categories
        articles_per_category = 4  # This will give us 20 articles (4 x 5 categories)
        
        for category in self.categories:
            try:
                response = self.api.get_top_headlines(
                    language='en',
                    country='us',
                    category=category,
                    page_size=10  # Get more articles to handle potential duplicates
                )
                if response['articles']:
                    # Add category and filter duplicates
                    articles_added = 0
                    for article in response['articles']:
                        if articles_added >= articles_per_category:
                            break
                            
                        # Skip if URL already seen or if missing required fields
                        if (article['url'] in seen_urls or 
                            not article['title'] or 
                            not article['description'] or 
                            not article['url']):
                            continue
                            
                        article['category'] = category
                        all_articles.append(article)
                        seen_urls.add(article['url'])
                        articles_added += 1
                        
            except Exception as e:
                print(f"Error fetching {category} news: {e}")
        
        return all_articles

    def format_for_static_site(self, articles):
        formatted_articles = []
        for article in articles:
            formatted = {
                'title': article['title'],
                'category': article['category'],
                'description': article['description'],
                'url': article['url'],
                'image': article['urlToImage'],
                'date': datetime.now().strftime("%B %d, %Y"),
                'readingTime': '3 min read'  # Simplified
            }
            formatted_articles.append(formatted)
        return formatted_articles
