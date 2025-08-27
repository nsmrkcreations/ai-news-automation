from dotenv import load_dotenv
import os
from src.core.news_aggregator import NewsAggregator
from src.core.ai_generator import AIContentGenerator
from src.core.content_manager import ContentManager

def test_pipeline():
    """Test the complete news pipeline with a single article"""
    print("Starting test pipeline...")
    
    # Load environment variables
    load_dotenv()
    
    # Set testing mode
    os.environ['TESTING'] = 'true'
    
    # Initialize components
    news = NewsAggregator()
    ai = AIContentGenerator()
    content = ContentManager()
    
    try:
        # Test NewsAPI
        print("\nTesting NewsAPI connection...")
        articles = news.fetch_trending(category='technology', page_size=1)
        if articles:
            print("✓ Successfully fetched news")
            article = articles[0]
            print(f"Sample headline: {article['title']}")
        else:
            print("× No articles found")
            return
        
        # Test content generation
        print("\nTesting content generation...")
        keywords = news.extract_keywords([article])
        ai_content = ai.create_article(
            topic=article['title'],
            keywords=keywords,
            context={'url': article['url']}
        )
        if ai_content and ai_content['content']:
            print("✓ Successfully generated content")
            print(f"Content length: {len(ai_content['content'].split())} words")
            if ai_content.get('image'):
                print(f"✓ Image included: {ai_content['image']['path']}")
            if ai_content.get('videos'):
                print(f"✓ Videos found: {len(ai_content['videos'])}")
                for video in ai_content['videos']:
                    if video['type'] == 'video_file':
                        print(f"  - Local video: {video['path']}")
                    else:
                        print(f"  - {video['type'].title()} video: {video['embed_url']}")
        else:
            print("× Failed to generate content")
            return
            
        # Test content creation
        print("\nTesting content management...")
        post_data = {
            'title': article['title'],
            'article': ai_content,
            'categories': ['technology'],
            'keywords': keywords,
            'image': article.get('urlToImage', '')
        }
        post_path = content.create_post(post_data)
        print(f"✓ Created post at: {post_path}")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\n× Error during test: {str(e)}")

if __name__ == "__main__":
    test_pipeline()
