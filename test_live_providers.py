"""
Test script to verify live API integration with each news provider
"""
import os
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
from src.core.fetchers.news_api_fetcher import NewsAPIFetcher
from src.core.fetchers.guardian_fetcher import GuardianFetcher
from src.core.fetchers.gdelt_fetcher import GDELTFetcher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_live_provider(provider_name: str, fetcher_instance) -> None:
    """Test a provider with live API calls"""
    logger.info(f"\nTesting live {provider_name} API...")
    
    try:
        # Test with technology category
        articles = fetcher_instance.fetch_news(category='technology')
        
        if not articles:
            logger.error(f"No articles returned from {provider_name}")
            return
            
        # Save first 5 articles as sample
        output_file = f"live_{provider_name.lower()}_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles[:5], f, indent=2, ensure_ascii=False)
            
        logger.info(f"Got {len(articles)} articles, saved 5 samples to {output_file}")
        
        # Display first article as sample
        logger.info("\nSample article format:")
        print(json.dumps(articles[0], indent=2, ensure_ascii=False))
        
        # Verify required fields
        required_fields = [
            'title', 'description', 'url', 'urlToImage', 'publishedAt',
            'source', 'category', 'provider', 'fetchedAt'
        ]
        
        missing_fields = []
        article = articles[0]
        for field in required_fields:
            if field not in article or article[field] is None:
                missing_fields.append(field)
                
        if missing_fields:
            logger.warning(f"Missing/null required fields in {provider_name}: {', '.join(missing_fields)}")
        else:
            logger.info("All required fields present and properly formatted")
            
        # Additional format checks
        if not isinstance(article['source'], dict):
            logger.error("source field is not a dictionary")
        elif not all(k in article['source'] for k in ['id', 'name']):
            logger.error("source missing required id or name fields")
            
        try:
            datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
        except ValueError:
            logger.error("publishedAt is not in ISO format")
            
        try:
            datetime.fromisoformat(article['fetchedAt'].replace('Z', '+00:00'))
        except ValueError:
            logger.error("fetchedAt is not in ISO format")
            
    except Exception as e:
        logger.error(f"Error testing {provider_name}: {str(e)}")

def main():
    # Load environment variables
    load_dotenv()
    
    # Test NewsAPI
    try:
        logger.info("Initializing NewsAPI fetcher...")
        news_api = NewsAPIFetcher()
        test_live_provider("NewsAPI", news_api)
    except Exception as e:
        logger.error(f"Could not test NewsAPI: {str(e)}")
    
    # Test Guardian
    try:
        logger.info("Initializing Guardian fetcher...")
        guardian = GuardianFetcher()
        test_live_provider("Guardian", guardian)
    except Exception as e:
        logger.error(f"Could not test Guardian: {str(e)}")
    
    # Test GDELT
    try:
        logger.info("Initializing GDELT fetcher...")
        gdelt = GDELTFetcher()
        test_live_provider("GDELT", gdelt)
    except Exception as e:
        logger.error(f"Could not test GDELT: {str(e)}")

if __name__ == "__main__":
    main()
