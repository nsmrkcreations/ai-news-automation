import os
import json
import requests
from datetime import datetime, timedelta

def validate_deployment():
    """Validate the deployment by checking critical components"""
    errors = []
    
    # Check if public directory exists
    if not os.path.exists('public'):
        errors.append("Public directory is missing")
        return errors
        
    # Check for required files
    required_files = [
        'public/index.html',
        'public/css/styles.css',
        'public/js/main.js',
        'public/data/news.json',
        'public/CNAME'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            errors.append(f"Required file missing: {file_path}")
            
    # Validate news data
    try:
        with open('public/data/news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
            
        if not isinstance(news_data, list):
            errors.append("News data is not in the correct format")
        elif len(news_data) == 0:
            errors.append("No news articles found in news.json")
        else:
            # Add publishedAt if missing and validate dates
            current_time = datetime.utcnow()
            for article in news_data:
                if 'publishedAt' not in article:
                    article['publishedAt'] = current_time.isoformat() + 'Z'
                    
                # Validate and fix image URLs
                if 'image' in article:
                    try:
                        response = requests.head(article['image'], timeout=5)
                        if response.status_code != 200:
                            # Try HTTPS if HTTP fails
                            if article['image'].startswith('http:'):
                                https_url = 'https:' + article['image'][5:]
                                response = requests.head(https_url, timeout=5)
                                if response.status_code == 200:
                                    article['image'] = https_url
                    except:
                        # If image validation fails, use a fallback image
                        article['image'] = 'images/fallback.jpg'
            
            # Save the updated articles back to the file
            with open('public/data/news.json', 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
                
    except Exception as e:
        errors.append(f"Error validating news data: {str(e)}")
        
    return errors

if __name__ == "__main__":
    errors = validate_deployment()
    if errors:
        print("❌ Deployment validation failed:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("✅ Deployment validation passed!")
        exit(0)
