"""
Script to verify API keys and provider setup
"""
import os
import sys
from dotenv import load_dotenv
from src.core.gdelt_provider import GdeltNewsProvider
from src.core.guardian_provider import GuardianNewsProvider
from src.core.newsapi_provider import NewsAPIProvider

# Load environment variables from .env file
load_dotenv()

def check_api_keys():
    """Check if all required API keys are set"""
    required_keys = {
        'GUARDIAN_API_KEY': os.getenv('GUARDIAN_API_KEY'),
        'NEWSAPI_KEY': os.getenv('NEWS_API_KEY')  # Updated to match .env file
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    
    if missing_keys:
        print("Missing required API keys:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease set these environment variables before running the tests.")
        sys.exit(1)
    else:
        print("All required API keys are set.")

def test_providers():
    """Test each provider's basic functionality"""
    providers = {
        'GDELT': GdeltNewsProvider(),
        'Guardian': GuardianNewsProvider(),
        'NewsAPI': NewsAPIProvider()
    }
    
    print("\nTesting providers:")
    for name, provider in providers.items():
        print(f"\nTesting {name} provider:")
        print(f"- Available: {provider.is_available}")
        if hasattr(provider, 'api_key'):
            print(f"- API Key: {'Set' if provider.api_key else 'Not set'}")
        print(f"- Base URL: {provider.base_url}")
        if not provider.is_available:
            print(f"- Error: {provider.last_error}")

if __name__ == '__main__':
    print("Checking news provider setup...")
    check_api_keys()
    test_providers()
