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

        # Ensure all required files exist
        ensure_file_exists('public/data/news.json', '[]')
        ensure_file_exists('public/index.html', '<!DOCTYPE html><html><head><title>News Surge AI</title></head><body><div id="news"></div></body></html>')
        ensure_file_exists('public/css/styles.css', 'body { font-family: Arial, sans-serif; }')
        ensure_file_exists('public/js/main.js', 'console.log("News Surge AI loaded");')
        
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
