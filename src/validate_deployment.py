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
            # Check if articles are recent (within last 24 hours)
            try:
                # First check if all articles have publishedAt field
                for article in news_data:
                    if 'publishedAt' not in article:
                        errors.append("Article missing publishedAt field")
                        raise ValueError("Missing publishedAt field")
                
                latest_article = max(news_data, key=lambda x: x['publishedAt'])
                date_str = latest_article['publishedAt']
                
                # Try multiple date format parsings
                try:
                    if 'Z' in date_str:
                        date_str = date_str.replace('Z', '+00:00')
                    elif '+' not in date_str and '-' not in date_str[-6:]:
                        date_str = f"{date_str}+00:00"
                    latest_date = datetime.fromisoformat(date_str)
                except ValueError:
                    # Try parsing without timezone
                    try:
                        latest_date = datetime.fromisoformat(date_str)
                    except ValueError:
                        raise ValueError(f"Cannot parse date format: {date_str}")
                
                current_time = datetime.now(latest_date.tzinfo if latest_date.tzinfo else None)
                if current_time - latest_date > timedelta(hours=24):
                    errors.append("News articles are more than 24 hours old")
            except Exception as e:
                errors.append(f"Error validating news data dates: {str(e)}")
                
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
