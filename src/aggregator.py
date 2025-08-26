import requests

class NewsAggregator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.endpoint = 'https://newsapi.org/v2/top-headlines'

    def fetch_trending(self, category='technology', country='us', page_size=20):
        params = {
            'apiKey': self.api_key,
            'category': category,
            'country': country,
            'pageSize': page_size
        }
        response = requests.get(self.endpoint, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        return articles

    def extract_keywords(self, articles):
        keywords = set()
        for article in articles:
            title = article.get('title', '')
            words = title.split()
            for word in words:
                if len(word) > 4:
                    keywords.add(word.lower())
        return list(keywords)
