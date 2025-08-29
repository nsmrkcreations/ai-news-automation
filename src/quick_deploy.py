import os
import json
from datetime import datetime, timezone
from core.logger import setup_logger
from aggregator import NewsAggregator

logger = setup_logger()

def ensure_file_exists(filepath, default_content=""):
    """Ensure a file exists with default content if it doesn't"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(default_content)

def quick_deploy():
    """Quick deployment without starting the web server"""
    try:
        # Create required directories
        os.makedirs('public/data', exist_ok=True)
        os.makedirs('public/css', exist_ok=True)
        os.makedirs('public/js', exist_ok=True)
        os.makedirs('public/images', exist_ok=True)

        # Ensure all required files exist
        ensure_file_exists('public/index.html', '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Surge AI</title>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#ffffff">
</head>
<body>
    <div id="connection-status"></div>
    <div id="news-container"></div>
    <script src="js/main.js" type="module"></script>
    <script src="js/sw.js"></script>
</body>
</html>''')

        # Create manifest.json
        ensure_file_exists('public/manifest.json', '''{
            "name": "News Surge AI",
            "short_name": "NewsSurge",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#ffffff",
            "icons": [
                {
                    "src": "images/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                }
            ]
        }''')

        # Create or update news data
        news_aggregator = NewsAggregator()
        news_data = []
        for category in news_aggregator.categories:
            try:
                articles = news_aggregator.fetch_trending(category=category)
                news_data.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching {category} news: {str(e)}")
        
        with open('public/data/news.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        
        # Copy CNAME if it exists in the root
        if os.path.exists('CNAME'):
            ensure_file_exists('public/CNAME', open('CNAME', 'r').read())

        logger.info("Deployment completed successfully")
        return True
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        return False

if __name__ == "__main__":
    if quick_deploy():
        print("✅ Deployment successful")
        exit(0)
    else:
        print("❌ Deployment failed")
        exit(1)
