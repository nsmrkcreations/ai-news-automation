import os
import time
import schedule
from src.aggregator import NewsAggregator
from src.ai_generator import AIContentGenerator
from src.publishers.wordpress import WordPressPublisher
from src.publishers.medium import MediumPublisher
from src.publishers.linkedin import LinkedInPublisher
from src.revenue_optimizer import RevenueOptimizer

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_TOKEN = os.getenv('WORDPRESS_TOKEN')
MEDIUM_TOKEN = os.getenv('MEDIUM_TOKEN')
LINKEDIN_TOKEN = os.getenv('LINKEDIN_TOKEN')
LINKEDIN_AUTHOR_URN = os.getenv('LINKEDIN_AUTHOR_URN')

news_aggregator = NewsAggregator(NEWS_API_KEY)
ai_generator = AIContentGenerator()
wordpress_publisher = WordPressPublisher(WORDPRESS_URL, WORDPRESS_TOKEN)
medium_publisher = MediumPublisher(MEDIUM_TOKEN)
linkedin_publisher = LinkedInPublisher(LINKEDIN_TOKEN, LINKEDIN_AUTHOR_URN)
revenue_optimizer = RevenueOptimizer()

def daily_content_cycle():
    try:
        print("Fetching trending news articles...")
        articles = news_aggregator.fetch_trending()

        if not articles:
            print("No articles fetched; skipping cycle.")
            return

        topic = articles[0]['title']
        keywords = news_aggregator.extract_keywords(articles)

        print(f"Generating article for topic: {topic}")
        article = ai_generator.create_article(topic, keywords)
        optimized_article = revenue_optimizer.optimize_for_adsense(article)

        print("Publishing to WordPress...")
        wp_response = wordpress_publisher.post_article(title=topic, content=optimized_article, excerpt=topic)
        wp_url = wp_response.get('link')

        print(f"Published on WordPress at: {wp_url}")

        print("Publishing snippet to Medium...")
        medium_publisher.publish_post(title=topic, content=optimized_article[:1000] + f'\n\n[Read more here]({wp_url})')

        print("Publishing snippet to LinkedIn...")
        linkedin_publisher.post_article(text=topic, article_url=wp_url)

        print("Content cycle completed.")

    except Exception as e:
        print(f"Error during content cycle: {e}")

def run_scheduler():
    schedule.every().day.at("09:00").do(daily_content_cycle)
    schedule.every().day.at("14:00").do(daily_content_cycle)
    schedule.every().day.at("19:00").do(daily_content_cycle)

    print("Starting scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("AI News Automation Bot starting...")
    run_scheduler()
