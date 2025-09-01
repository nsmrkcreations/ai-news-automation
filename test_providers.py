"""
Test script to verify output format from each news provider
"""
import os
import json
from datetime import datetime
import logging
from src.core.fetchers.news_api_fetcher import NewsAPIFetcher
from src.core.fetchers.guardian_fetcher import GuardianFetcher
from src.core.fetchers.gdelt_fetcher import GDELTFetcher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_provider(provider_name: str, fetcher_instance) -> None:
    """Test a specific provider and save its output"""
    logger.info(f"\nTesting {provider_name}...")
    
    try:
        # Fetch technology news as a test category
        articles = fetcher_instance.fetch_news(category='technology')
        
        if not articles:
            logger.error(f"No articles returned from {provider_name}")
            return
            
        # Save provider-specific output
        output_file = f"provider_test_{provider_name.lower()}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles[:5], f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(articles[:5])} sample articles from {provider_name} to {output_file}")
        
        # Display first article as sample
        logger.info("\nSample article format:")
        print(json.dumps(articles[0], indent=2, ensure_ascii=False))
        
        # Verify required fields
        required_fields = [
            'title', 'description', 'url', 'urlToImage', 'publishedAt',
            'source', 'category', 'provider', 'fetchedAt'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not articles[0].get(field):
                missing_fields.append(field)
                
        if missing_fields:
            logger.warning(f"Missing required fields in {provider_name}: {', '.join(missing_fields)}")
        else:
            logger.info("All required fields present and formatted correctly")
            
    except Exception as e:
        logger.error(f"Error testing {provider_name}: {str(e)}")

def main():
    # Test NewsAPI
    try:
        news_api = NewsAPIFetcher()
        test_provider("NewsAPI", news_api)
    except Exception as e:
        logger.error(f"Could not initialize NewsAPI fetcher: {str(e)}")
    
    # Test Guardian
    try:
        guardian = GuardianFetcher()
        test_provider("Guardian", guardian)
    except Exception as e:
        logger.error(f"Could not initialize Guardian fetcher: {str(e)}")
    
    # Test GDELT
    try:
        gdelt = GDELTFetcher()
        test_provider("GDELT", gdelt)
    except Exception as e:
        logger.error(f"Could not initialize GDELT fetcher: {str(e)}")

if __name__ == "__main__":
    main()
