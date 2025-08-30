#!/usr/bin/env python3
"""
Debug backend news generation issues
"""

import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_step_by_step():
    """Debug each step individually"""
    print("🔍 Debugging Backend Step by Step")
    print("=" * 50)
    
    # Step 1: Environment
    print("1. Environment Variables:")
    api_key = os.getenv('NEWS_API_KEY')
    print(f"   NEWS_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    if api_key:
        print(f"   Key preview: {api_key[:8]}...")
    
    # Step 2: Dependencies
    print("\n2. Dependencies:")
    try:
        import requests
        print("   ✅ requests")
    except ImportError as e:
        print(f"   ❌ requests: {e}")
        return False
    
    try:
        import json
        print("   ✅ json")
    except ImportError as e:
        print(f"   ❌ json: {e}")
        return False
    
    # Step 3: NewsAPI Test
    print("\n3. NewsAPI Connection:")
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=3&apiKey={api_key}"
        print(f"   URL: {url[:50]}...")
        
        response = requests.get(url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Error Response: {response.text}")
            return False
        
        data = response.json()
        print(f"   ✅ Response received")
        print(f"   Articles count: {len(data.get('articles', []))}")
        
        articles = data.get('articles', [])
        if articles:
            first_article = articles[0]
            print(f"   Sample title: {first_article.get('title', 'No title')[:50]}...")
        
    except Exception as e:
        print(f"   ❌ NewsAPI Error: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: File Writing
    print("\n4. File Writing Test:")
    try:
        output_dir = Path("public/data")
        print(f"   Output directory: {output_dir}")
        
        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)
        print("   ✅ Directory created/exists")
        
        # Test file write
        test_file = output_dir / "test.json"
        with open(test_file, 'w') as f:
            json.dump({"test": "data"}, f)
        print("   ✅ File write successful")
        
        # Clean up
        test_file.unlink()
        print("   ✅ Test file cleaned up")
        
    except Exception as e:
        print(f"   ❌ File Error: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Full News Generation
    print("\n5. Full News Generation:")
    try:
        # Fetch articles
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get('articles', [])
        
        # Process articles
        processed_articles = []
        for i, article in enumerate(articles[:5]):  # Limit to 5
            try:
                processed_article = {
                    'id': i + 1,
                    'title': article.get('title', 'No title'),
                    'description': article.get('description', 'No description'),
                    'url': article.get('url', ''),
                    'urlToImage': article.get('urlToImage', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'category': 'general',
                    'isBreaking': False
                }
                processed_articles.append(processed_article)
                print(f"   ✅ Processed article {i+1}: {processed_article['title'][:30]}...")
                
            except Exception as e:
                print(f"   ⚠️ Error processing article {i+1}: {e}")
                continue
        
        # Save to file
        output_file = output_dir / "news.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_articles, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Saved {len(processed_articles)} articles to {output_file}")
        
        # Verify file
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        print(f"   ✅ Verification: {len(saved_data)} articles in file")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Generation Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run debug"""
    success = debug_step_by_step()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Backend should work.")
        print("📁 Check public/data/news.json for generated news")
    else:
        print("❌ Some tests failed. Check errors above.")
    
    return success

if __name__ == "__main__":
    main()
