"""
Test script to verify standardized output format from each news provider
"""
import os
import json
from datetime import datetime
import logging
from src.core.fetchers.base import NewsFetcherBase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockFetcher(NewsFetcherBase):
    def __init__(self, provider_name, sample_data):
        self.provider = provider_name
        self.sample_data = sample_data
        
    def fetch_news(self, category=None):
        if self.provider == 'newsapi':
            return self._process_newsapi()
        elif self.provider == 'guardian':
            return self._process_guardian()
        elif self.provider == 'gdelt':
            return self._process_gdelt()
            
    def _process_newsapi(self):
        articles = self.sample_data['newsapi']['articles']
        return [self.standardize_article(article, 'technology') for article in articles]
        
    def _process_guardian(self):
        articles = self.sample_data['guardian']['response']['results']
        return [self.standardize_article(article, 'technology') for article in articles]
        
    def _process_gdelt(self):
        articles = self.sample_data['gdelt']
        return [self.standardize_article(article, 'technology') for article in articles]
        
    def standardize_article(self, raw_article, category=None):
        base = super().standardize_article(raw_article, category)
        
        if self.provider == 'newsapi':
            base.update({
                'title': raw_article.get('title', '').strip(),
                'description': raw_article.get('description', '').strip(),
                'url': raw_article.get('url', ''),
                'urlToImage': raw_article.get('urlToImage', base['urlToImage']),
                'publishedAt': raw_article.get('publishedAt', base['publishedAt']),
                'source': raw_article.get('source', base['source']),
                'content': raw_article.get('content'),
                'author': raw_article.get('author'),
                'provider': 'newsapi'
            })
        elif self.provider == 'guardian':
            fields = raw_article.get('fields', {})
            base.update({
                'title': raw_article.get('webTitle', '').strip(),
                'description': fields.get('trailText', '').strip(),
                'url': raw_article.get('webUrl', ''),
                'urlToImage': fields.get('thumbnail', base['urlToImage']),
                'publishedAt': raw_article.get('webPublicationDate', base['publishedAt']),
                'source': {
                    'id': 'guardian',
                    'name': 'The Guardian'
                },
                'content': fields.get('bodyText'),
                'author': fields.get('byline'),
                'provider': 'guardian'
            })
        elif self.provider == 'gdelt':
            # Convert GDELT timestamp format to ISO format
            seendate = raw_article.get('seendate', '')
            if seendate:
                try:
                    # Convert from 'YYYYMMDDTHHmmssZ' to ISO format
                    dt = datetime.strptime(seendate, '%Y%m%dT%H%M%SZ')
                    seendate = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    seendate = base['publishedAt']
            
            base.update({
                'title': raw_article.get('title', '').strip(),
                'description': raw_article.get('description', '').strip(),
                'url': raw_article.get('url', ''),
                'urlToImage': raw_article.get('image', base['urlToImage']),
                'publishedAt': seendate,
                'source': {
                    'id': raw_article.get('sourcecountry', 'unknown'),
                    'name': raw_article.get('domain', 'Unknown')
                },
                'content': raw_article.get('text'),
                'provider': 'gdelt'
            })
            
        return base

def test_provider(provider_name: str, fetcher: MockFetcher) -> None:
    """Test a specific provider's output format"""
    logger.info(f"\nTesting {provider_name} output format...")
    
    try:
        articles = fetcher.fetch_news(category='technology')
        
        if not articles:
            logger.error(f"No articles returned from {provider_name}")
            return
            
        # Save standardized output
        output_file = f"standardized_{provider_name.lower()}_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved standardized output from {provider_name} to {output_file}")
        
        # Display standardized format
        logger.info("\nStandardized article format:")
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
    # Load sample data
    with open('tests/sample_provider_data.json', 'r', encoding='utf-8') as f:
        sample_data = json.load(f)
    
    # Test each provider with sample data
    providers = ['newsapi', 'guardian', 'gdelt']
    
    for provider in providers:
        fetcher = MockFetcher(provider, sample_data)
        test_provider(provider, fetcher)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
