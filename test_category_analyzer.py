"""
Test the category analyzer independently
"""
import logging
from src.core.category_analyzer import CategoryAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_category_analyzer():
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
            # Mixed content article (business/tech)
            'title': 'Market Rally Continues as Tech Stocks Surge',
            'description': 'Major gains in technology sector led by AI companies',
            'category': 'business-tech',  # Different API category name
            'content': 'Article about stock market and tech companies...'
        },
        {
            # Article about sports
            'title': 'Champions League Final Set for Epic Showdown',
            'description': 'Two top teams prepare for ultimate football battle',
            'content': 'Coverage of the upcoming championship game...'
        },
        {
            # Health article
            'title': 'New Cancer Treatment Shows Promise',
            'description': 'Medical breakthrough in immunotherapy',
            'content': 'Research details about medical advances...'
        }
    ]
    
    logger.info("Testing category analyzer...")
    
    for idx, article in enumerate(test_articles, 1):
        # Get category and confidence scores
        detected_category = CategoryAnalyzer.get_category(article)
        scores = CategoryAnalyzer.get_confidence_scores(article)
        
        # Log results
        logger.info(f"\nArticle {idx}:")
        logger.info(f"Title: {article['title']}")
        logger.info(f"Original category: {article.get('category', 'None')}")
        logger.info(f"Detected category: {detected_category}")
        logger.info("Category confidence scores:")
        for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if score > 0:
                logger.info(f"  {cat}: {score:.2f}")

if __name__ == "__main__":
    test_category_analyzer()
