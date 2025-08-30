import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Quick test
api_key = os.getenv('NEWS_API_KEY')
url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={api_key}"

try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        print(f"Articles: {len(articles)}")
        
        # Save to file
        os.makedirs('public/data', exist_ok=True)
        with open('public/data/news.json', 'w') as f:
            json.dump(articles[:3], f, indent=2)
        print("✅ Saved to public/data/news.json")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Failed: {e}")
