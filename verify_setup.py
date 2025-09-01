"""
Verify setup and test news automation
"""
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

def verify_setup():
    """Verify all components are properly set up"""
    print("🔍 Verifying AI News Automation setup...")
    print("=" * 50)
    
    # Check environment variables
    load_dotenv()
    required_vars = ['NEWS_API_KEY', 'NEWS_CATEGORIES', 'NEWS_UPDATE_INTERVAL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("❌ Missing environment variables:", ', '.join(missing_vars))
        return False
    print("✅ Environment variables verified")
    
    # Check directories
    required_dirs = ['logs', 'cache', 'public/data']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"❌ Missing directory: {dir_path}")
            return False
    print("✅ Directory structure verified")
    
    # Check news.json
    news_file = 'public/data/news.json'
    if os.path.exists(news_file):
        try:
            with open(news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                print(f"✅ news.json exists with {len(data)} articles")
            else:
                print("❌ news.json has invalid format")
                return False
        except json.JSONDecodeError:
            print("❌ news.json is not valid JSON")
            return False
    else:
        print("⚠️ news.json doesn't exist yet (will be created on first update)")
    
    # Verify Python packages
    try:
        import requests
        import schedule
        print("✅ Required Python packages verified")
    except ImportError as e:
        print(f"❌ Missing Python package: {e.name}")
        return False
    
    print("=" * 50)
    print("✅ Setup verification complete!")
    return True

if __name__ == "__main__":
    if verify_setup():
        print("\n🚀 Ready to run! Check Task Scheduler to verify the task is enabled.")
