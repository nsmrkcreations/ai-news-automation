import os
import json
import requests
from typing import List, Dict
from datetime import datetime
from pathlib import Path

class NewsAggregator:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = 'https://newsapi.org/v2/top-headlines'
        self.categories = os.getenv('NEWS_CATEGORIES', 'technology,science,business,ai').split(',')
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.testing = os.getenv('TESTING', 'false').lower() == 'true'

    def fetch_trending(self, category: str = None, country: str = 'us', page_size: int = 10) -> List[Dict]:
        """Fetch trending news articles with improved quality filters"""
        # Try cache first in testing mode
        if self.testing:
            cached_data = self._get_cached_data(category, country)
            if cached_data:
                return cached_data[:page_size]

        params = {
            'apiKey': self.api_key,
            'pageSize': page_size * 2,  # Fetch more to filter
            'language': 'en',
            'country': country,
            'sortBy': 'relevancy'  # Prioritize relevant news
        }
        
        if category:
            params['category'] = category

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            
            # Filter and enhance articles
            filtered_articles = []
            for article in articles:
                # Skip articles without required fields
                if not all(article.get(field) for field in ['title', 'url', 'description']):
                    continue
                
                # Skip articles with very short content
                if len(article.get('description', '')) < 50:
                    continue
                
                # Detect duplicate content
                title_lower = article['title'].lower()
                if any(a['title'].lower() == title_lower for a in filtered_articles):
                    continue
                
                # Add breaking news detection
                is_breaking = any(word in title_lower for word in ['breaking', 'urgent', 'just in', 'update'])
                article['isBreaking'] = is_breaking
                
                filtered_articles.append(article)
                
                if len(filtered_articles) >= page_size:
                    break
            
            # Cache results in testing mode
            if self.testing:
                self._cache_data(filtered_articles, category, country)
            
            return filtered_articles
        except Exception as e:
            print(f"Error fetching news: {e}")
            if self.testing:
                print("Attempting to use cached data...")
                cached_data = self._get_cached_data(category, country)
                if cached_data:
                    return cached_data[:page_size]
            return []
            
    def _get_cache_file(self, category: str, country: str) -> Path:
        """Get the cache file path for the given parameters"""
        category = category or 'all'
        return self.cache_dir / f"news_cache_{category}_{country}.json"
        
    def _get_cached_data(self, category: str, country: str) -> List[Dict]:
        """Get cached news data if available and not expired"""
        cache_file = self._get_cache_file(category, country)
        if not cache_file.exists():
            return []
            
        try:
            data = json.loads(cache_file.read_text())
            # Check if cache is from today
            cache_date = datetime.fromisoformat(data['timestamp']).date()
            if cache_date == datetime.now().date():
                return data['articles']
        except Exception as e:
            print(f"Error reading cache: {e}")
        return []
        
    def _cache_data(self, articles: List[Dict], category: str, country: str):
        """Cache the news data"""
        cache_file = self._get_cache_file(category, country)
        data = {
            'timestamp': datetime.now().isoformat(),
            'articles': articles
        }
        try:
            cache_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error writing cache: {e}")

    def extract_keywords(self, articles: List[Dict]) -> List[str]:
        """Extract relevant keywords from articles"""
        keywords = set()
        for article in articles:
            # Extract from title and description
            for text in [article.get('title', ''), article.get('description', '')]:
                words = text.lower().split()
                keywords.update([word for word in words if len(word) > 4])
        
        # Remove common words and return top keywords
        common_words = {'about', 'after', 'again', 'their', 'these', 'those', 'where', 'which'}
        keywords = keywords - common_words
        return list(keywords)[:10]  # Return top 10 keywords

    def save_article_image(self, image_url: str, article_url: str) -> str:
        """Download and save article image, return the local path"""
        try:
            # Quick validation of image URL
            if not image_url or not image_url.startswith('http'):
                return 'images/fallback.jpg'

            # Create images directory if it doesn't exist
            image_dir = Path('public/images/news')
            image_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename from article URL
            from hashlib import md5
            filename = md5(article_url.encode()).hexdigest()[:10] + '.jpg'
            image_path = image_dir / filename
            
            # Don't redownload if image exists
            if image_path.exists():
                return f'images/news/{filename}'
            
            # Download and save image with timeout
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(image_url, timeout=5, headers=headers)
            response.raise_for_status()
            
            # Verify it's actually an image
            if 'image' not in response.headers.get('content-type', ''):
                return 'images/fallback.jpg'
            
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            return f'images/news/{filename}'
        except Exception as e:
            print(f"Error saving image for {article_url}: {e}")
            return 'images/fallback.jpg'

    def clean_text(self, text: str) -> str:
        """Clean and validate text content"""
        if not text:
            return ""
        # Remove excessive whitespace
        text = " ".join(text.split())
        # Remove any control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")
        return text.strip()

    def detect_category(self, article: Dict) -> str:
        """Detect article category from content"""
        keywords = {
            'technology': ['tech', 'software', 'ai', 'robot', 'smartphone', 'computer', 'digital'],
            'business': ['market', 'stock', 'economy', 'trade', 'finance', 'company'],
            'science': ['research', 'study', 'scientist', 'discovery', 'space', 'physics'],
            'health': ['medical', 'health', 'disease', 'treatment', 'drug', 'patient'],
            'politics': ['government', 'election', 'policy', 'political', 'minister', 'president'],
            'sports': ['game', 'player', 'team', 'sport', 'championship', 'tournament']
        }
        
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Count keyword matches for each category
        matches = {
            category: sum(1 for word in words if word in text)
            for category, words in keywords.items()
        }
        
        # Return category with most matches, default to 'general'
        return max(matches.items(), key=lambda x: x[1])[0] if any(matches.values()) else 'general'

    def format_for_static_site(self, articles: List[Dict]) -> List[Dict]:
        """Format articles for static site generation with enhanced validation"""
        formatted = []
        for article in articles:
            try:
                # Basic validation
                if not article.get('title') or not article.get('url'):
                    continue

                # Clean text fields
                title = self.clean_text(article.get('title', ''))
                description = self.clean_text(article.get('description', ''))
                content = self.clean_text(article.get('content', ''))

                # Calculate accurate reading time
                total_words = len(f"{title} {description} {content}".split())
                reading_time = max(1, round(total_words / 200))  # Assume 200 words per minute

                # Parse and validate date
                try:
                    pub_date = article.get('publishedAt', datetime.now().isoformat())
                    if 'Z' in pub_date:
                        pub_date = pub_date.replace('Z', '+00:00')
                    formatted_date = datetime.fromisoformat(pub_date).strftime('%B %d, %Y')
                except Exception:
                    pub_date = datetime.now().isoformat()
                    formatted_date = datetime.now().strftime('%B %d, %Y')

                # Detect category if not provided
                category = article.get('category', self.detect_category(article))

                formatted_article = {
                    'title': title,
                    'description': description or title,  # Use title as fallback
                    'content': content,
                    'url': article['url'],
                    'publishedAt': pub_date,
                    'source': article.get('source', {}).get('name', 'Unknown Source'),
                    'category': category.lower(),
                    'readingTime': f"{reading_time} min read",
                    'date': formatted_date,
                    'isBreaking': bool(article.get('isBreaking')),  # Support breaking news flag
                    'keywords': self.extract_keywords([article])  # Add keywords for better categorization
                }
                formatted.append(formatted_article)
            except Exception as e:
                print(f"Error formatting article {article.get('url', 'unknown')}: {e}")
                continue
        
        return formatted
