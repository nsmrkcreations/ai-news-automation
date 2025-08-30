#!/usr/bin/env python3
"""
Quick backend test script
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test environment setup"""
    print("🔧 Testing Environment Setup")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('NEWS_API_KEY')
    if api_key and api_key != 'YOUR_NEWSAPI_KEY_HERE':
        print(f"✅ NewsAPI Key: {api_key[:8]}...")
    else:
        print("❌ NewsAPI Key: Not set or placeholder")
        return False
    
    # Check dependencies
    try:
        import requests
        print("✅ requests library available")
    except ImportError:
        print("❌ requests library missing")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv available")
    except ImportError:
        print("❌ python-dotenv missing")
        return False
    
    return True

def test_newsapi():
    """Test NewsAPI connection"""
    print("\n📰 Testing NewsAPI Connection")
    print("=" * 40)
    
    try:
        import requests
        
        api_key = os.getenv('NEWS_API_KEY')
        url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=5&apiKey={api_key}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"✅ NewsAPI working - {len(articles)} articles fetched")
            
            if articles:
                print(f"📄 Sample: {articles[0].get('title', 'No title')[:50]}...")
            return True
        else:
            print(f"❌ NewsAPI error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ NewsAPI connection failed: {e}")
        return False

def test_news_generation():
    """Test news.json generation"""
    print("\n💾 Testing News Generation")
    print("=" * 40)
    
    try:
        import requests
        import json
        
        api_key = os.getenv('NEWS_API_KEY')
        url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=10&apiKey={api_key}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get('articles', [])
        
        # Process articles
        processed_articles = []
        for article in articles:
            processed_article = {
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'urlToImage': article.get('urlToImage'),
                'publishedAt': article.get('publishedAt'),
                'source': article.get('source', {}).get('name'),
                'category': 'general',
                'isBreaking': False
            }
            processed_articles.append(processed_article)
        
        # Save to frontend
        output_dir = Path("public/data")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "news.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_articles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Generated {len(processed_articles)} articles")
        print(f"💾 Saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ News generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI News Automation - Backend Test")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("NewsAPI", test_newsapi),
        ("News Generation", test_news_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results")
    print("=" * 30)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 All tests passed! Backend is ready.")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
