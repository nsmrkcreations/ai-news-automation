import os
import json
from datetime import datetime
from pathlib import Path
from aggregator import NewsAggregator
from ai_generator import AIContentGenerator

class StaticSiteBuilder:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.site_dir = Path('./site')
        self.posts_dir = self.site_dir / 'posts'
        self.images_dir = self.site_dir / 'images'
        self.setup_directories()

    def setup_directories(self):
        """Create necessary directories"""
        self.site_dir.mkdir(exist_ok=True)
        self.posts_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)

    def generate_post(self, article_data):
        """Generate a static post from article data"""
        date = datetime.now().strftime('%Y-%m-%d')
        slug = article_data['title'].lower().replace(' ', '-')
        
        content = f"""---
layout: post
title: "{article_data['title']}"
date: {date}
categories: [news, {article_data['category']}]
image: "{article_data['image_path']}"
---

{article_data['content']}
"""
        post_path = self.posts_dir / f"{date}-{slug}.md"
        post_path.write_text(content)
        return post_path

    def build(self):
        """Build the static site"""
        # Initialize components
        news = NewsAggregator(self.news_api_key)
        ai = AIContentGenerator(self.openai_api_key)

        # Fetch and process news
        articles = news.fetch_trending()
        for article in articles:
            keywords = news.extract_keywords([article])
            content = ai.create_article(article['title'], keywords)
            
            # Generate post
            post_data = {
                'title': article['title'],
                'category': 'technology',  # We can make this dynamic
                'content': content,
                'image_path': article.get('urlToImage', '')
            }
            self.generate_post(post_data)

        # Generate index page
        self.generate_index()

    def generate_index(self):
        """Generate the main index.html"""
        index_content = """---
layout: default
title: NewsSurgeAI - Latest Tech News
---

<div class="posts">
  {% for post in site.posts %}
    <article class="post">
      <h2><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h2>
      {% if post.image %}
        <img src="{{ post.image }}" alt="{{ post.title }}">
      {% endif %}
      <div class="entry">
        {{ post.excerpt }}
      </div>
      <a href="{{ site.baseurl }}{{ post.url }}" class="read-more">Read More</a>
    </article>
  {% endfor %}
</div>
"""
        index_path = self.site_dir / 'index.html'
        index_path.write_text(index_content)

if __name__ == '__main__':
    builder = StaticSiteBuilder()
    builder.build()
