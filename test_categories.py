"""
Test script for category detection
"""
import logging
from src.core.category_analyzer import CategoryAnalyzer
from src.core.provider_manager import NewsProviderManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_category_detection():
    """Test category detection with sample articles"""
    
    # Sample articles with different scenarios
    test_articles = [
        {
            # Article with API-provided category
            'title': 'New AI Breakthrough in Quantum Computing',
            'description': 'Researchers achieve major advancement in quantum error correction',
            'category': 'technology',  # API-provided category
            'content': 'Full article about quantum computing and AI...'
        },
        {
            # Article without category but clear technology content
            'title': 'AI Startup Develops Revolutionary Software',
            'description': 'Machine learning solution for complex problems',
            'content': 'Article about AI and software development...'
        },
        {
            # Article with different API category name
            'title': 'Market Rally Continues as Tech Stocks Surge',
            'description': 'Major gains in technology sector',
            'category': 'business-tech',  # Different API category name
            'content': 'Article about stock market and tech companies...'
        }
    ]
    
    logger.info("Testing category detection...")
    
    for idx, article in enumerate(test_articles, 1):
        # Get category
        category = CategoryAnalyzer.get_category(article)
        
        # Get confidence scores
        scores = CategoryAnalyzer.get_confidence_scores(article)
        
        # Log results
        logger.info(f"\nArticle {idx}:")
        logger.info(f"Title: {article['title']}")
        logger.info(f"Original category: {article.get('category', 'None')}")
        logger.info(f"Detected category: {category}")
        logger.info("Category confidence scores:")
        for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if score > 0:
                logger.info(f"  {cat}: {score:.2f}")

def test_live_categorization():
    """Test category detection with live articles"""
    
    logger.info("\nTesting with live articles...")
    
    # Initialize provider manager
    manager = NewsProviderManager()
    
    try:
        # Fetch some articles
        articles = manager.fetch_news()
        
        logger.info(f"\nProcessed {len(articles)} live articles")
        
        # Get category distribution
        category_counts = {}
        for article in articles:
            cat = article.get('category', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        logger.info("\nCategory distribution:")
        for cat, count in sorted(category_counts.items()):
            logger.info(f"  {cat}: {count} articles")
            
    except Exception as e:
        logger.error(f"Error testing live categorization: {e}")

if __name__ == "__main__":
    # Test with sample articles
    test_category_detection()
    
    # Test with live articles
    test_live_categorization()
