from typing import List, Dict, Tuple, Optional
import os
import re
import requests
from pathlib import Path
from newspaper import Article
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet
import random
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import hashlib
from bs4 import BeautifulSoup

class AIContentGenerator:
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')
            
        # Create media directories if they don't exist
        self.images_dir = Path('site/assets/images/posts')
        self.videos_dir = Path('site/assets/videos/posts')
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Video platforms patterns
        self.video_patterns = {
            'youtube': r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]+)',
            'vimeo': r'(?:https?:\/\/)?(?:www\.)?(?:vimeo\.com\/)(\d+)',
            'dailymotion': r'(?:https?:\/\/)?(?:www\.)?(?:dailymotion\.com\/video\/)([a-zA-Z0-9]+)',
        }

    def create_article(self, topic: str, keywords: List[str], context: Dict = None) -> Dict[str, str]:
        """Generate an article by intelligently combining and restructuring news content"""
        try:
            image_info = None
            content = ""
            
            if context and 'url' in context:
                # Extract content from the source article
                article = Article(context['url'])
                article.download()
                article.parse()
                article.nlp()  # This generates keywords, summary, etc.
                
                # Try to get the image from the article
                if article.top_image:
                    image_info = self._download_and_save_image(article.top_image, topic)
                
                # Extract videos
                videos = self._extract_videos_from_article(article)
                
                # Get the main points from the article
                summary = article.summary
                
                # Restructure the content
                sentences = sent_tokenize(summary)
                introduction = self._generate_introduction(topic, keywords)
                body = self._restructure_content(sentences, keywords)
                conclusion = self._generate_conclusion(keywords)
                
                # Build the content with videos
                content_parts = [introduction, ""]
                
                # Add videos after introduction if available
                for video in videos:
                    if video['type'] == 'video_file':
                        content_parts.append(f'<video width="100%" controls>\n  <source src="{video["path"]}" type="video/mp4">\n  Your browser does not support the video tag.\n</video>\n')
                    else:
                        content_parts.append(f'<iframe width="100%" height="400" src="{video["embed_url"]}" frameborder="0" allowfullscreen></iframe>\n')
                
                content_parts.extend([body, "", conclusion])
                content = "\n\n".join(content_parts)
            else:
                # Generate a simpler article based on the topic and keywords
                content = self._create_basic_article(topic, keywords)
            
            # If no image was found in the article, try to get a relevant image from keywords
            if not image_info and content:
                image_query = ' '.join(keywords[:2])  # Use first two keywords for image search
                image_info = self._get_tech_stock_image(image_query)
            
            # Format the content with the image if available
            if image_info:
                # Add image at the top of the article with proper markdown
                content = f"![{image_info['alt']}]({image_info['path']})\n\n{content}"
            
            return {
                'content': content,
                'image': image_info,
                'videos': videos if videos else None
            }
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return {'content': None, 'image': None}

    def _generate_introduction(self, topic: str, keywords: List[str]) -> str:
        """Generate an engaging introduction"""
        templates = [
            f"In a significant development in the tech world, {topic.lower()}.",
            f"Recent advances in technology have brought attention to {topic.lower()}.",
            f"A new breakthrough has emerged as {topic.lower()}."
        ]
        return random.choice(templates)
    
    def _restructure_content(self, sentences: List[str], keywords: List[str]) -> str:
        """Restructure the content to create a coherent article"""
        # Group sentences by relevance to keywords
        relevant_sentences = []
        other_sentences = []
        
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                relevant_sentences.append(sentence)
            else:
                other_sentences.append(sentence)
        
        # Combine sentences in a logical order
        article_body = " ".join(relevant_sentences)
        if other_sentences:
            article_body += "\n\n" + " ".join(other_sentences)
            
        return article_body
    
    def _generate_conclusion(self, keywords: List[str]) -> str:
        """Generate a conclusion based on the keywords"""
        templates = [
            f"This development marks a significant step forward in {', '.join(keywords[:2])}.",
            f"The implications of this advancement will likely reshape how we think about {keywords[0]}.",
            f"As these technologies continue to evolve, we can expect to see more innovations in {', '.join(keywords[:2])}."
        ]
        return random.choice(templates)
    
    def _create_basic_article(self, topic: str, keywords: List[str]) -> str:
        """Create a basic article when no source URL is available"""
        introduction = self._generate_introduction(topic, keywords)
        
        # Generate some basic content based on keywords
        paragraphs = []
        for keyword in keywords[:3]:  # Use up to 3 keywords to generate paragraphs
            templates = [
                f"One of the key aspects of this development involves {keyword}.",
                f"Experts are particularly interested in the implications for {keyword}.",
                f"The advancement in {keyword} represents a significant milestone."
            ]
            paragraphs.append(random.choice(templates))
        
        body = "\n\n".join(paragraphs)
        conclusion = self._generate_conclusion(keywords)
        
        return f"{introduction}\n\n{body}\n\n{conclusion}"
        
    def _download_and_save_image(self, image_url: str, topic: str) -> Dict[str, str]:
        """Download and save an image, returning its path and alt text"""
        try:
            # Generate a unique filename
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:10]
            date_str = datetime.now().strftime('%Y%m%d')
            image_ext = self._get_image_extension(image_url)
            filename = f"{date_str}_{url_hash}{image_ext}"
            
            # Create the full path
            image_path = self.images_dir / filename
            
            # Download and save the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Return the image information
            return {
                'path': f"/assets/images/posts/{filename}",
                'alt': topic
            }
            
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None
            
    def _get_tech_stock_image(self, query: str) -> Dict[str, str]:
        """Get a relevant stock image for the article"""
        # For now, use a default tech image
        default_images = [
            "https://images.unsplash.com/photo-1518770660439-4636190af475",  # Tech
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa",  # Digital
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c",  # Computer
        ]
        
        try:
            image_url = random.choice(default_images)
            return self._download_and_save_image(image_url, query)
        except Exception as e:
            print(f"Error getting stock image: {e}")
            return None
            
    def _get_image_extension(self, url: str) -> str:
        """Get the image extension from URL or default to .jpg"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        if path.endswith('.png'):
            return '.png'
        elif path.endswith('.gif'):
            return '.gif'
        elif path.endswith('.jpeg'):
            return '.jpeg'
        else:
            return '.jpg'
            
    def _extract_video_info(self, url: str) -> Optional[Dict[str, str]]:
        """Extract video information from a URL"""
        for platform, pattern in self.video_patterns.items():
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                if platform == 'youtube':
                    return {
                        'type': 'youtube',
                        'id': video_id,
                        'embed_url': f"https://www.youtube.com/embed/{video_id}",
                        'thumbnail': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    }
                elif platform == 'vimeo':
                    return {
                        'type': 'vimeo',
                        'id': video_id,
                        'embed_url': f"https://player.vimeo.com/video/{video_id}",
                    }
                elif platform == 'dailymotion':
                    return {
                        'type': 'dailymotion',
                        'id': video_id,
                        'embed_url': f"https://www.dailymotion.com/embed/video/{video_id}",
                    }
        return None
        
    def _download_video(self, url: str, title: str) -> Optional[Dict[str, str]]:
        """Download a video file if possible"""
        try:
            # Only attempt to download direct video files
            video_extensions = ['.mp4', '.webm', '.ogg']
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if not any(path.endswith(ext) for ext in video_extensions):
                return None
                
            # Generate filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            date_str = datetime.now().strftime('%Y%m%d')
            ext = os.path.splitext(path)[1]
            filename = f"{date_str}_{url_hash}{ext}"
            
            # Create the full path
            video_path = self.videos_dir / filename
            
            # Download and save the video
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return {
                'type': 'video_file',
                'path': f"/assets/videos/posts/{filename}",
                'title': title
            }
            
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None
            
    def _extract_videos_from_article(self, article: Article) -> List[Dict[str, str]]:
        """Extract videos from an article"""
        videos = []
        
        # Check article.movies (from newspaper3k)
        for video_url in article.movies:
            video_info = self._extract_video_info(video_url)
            if video_info:
                videos.append(video_info)
            else:
                # Try downloading if it's a direct video file
                video_file = self._download_video(video_url, article.title)
                if video_file:
                    videos.append(video_file)
        
        # Parse HTML for additional video content
        if article.html:
            soup = BeautifulSoup(article.html, 'lxml')
            
            # Find iframes (embedded videos)
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                video_info = self._extract_video_info(src)
                if video_info:
                    videos.append(video_info)
            
            # Find video tags
            for video in soup.find_all('video'):
                src = video.get('src') or (video.find('source', recursive=False) or {}).get('src')
                if src:
                    video_file = self._download_video(src, article.title)
                    if video_file:
                        videos.append(video_file)
        
        return videos
        prompt = f"""Write an engaging and informative article about {topic}.

Key requirements:
- Length: 700-1000 words
- Include these keywords naturally: {', '.join(keywords)}
- Use proper headings and structure
- Include a compelling introduction
- End with a conclusion
- Focus on accuracy and readability
- Write in a journalistic style
- Make it SEO-friendly

Structure the article with:
1. Engaging headline
2. Introduction (hook the reader)
3. Main body (2-3 sections)
4. Conclusion
"""
        if context and 'related_topics' in context:
            prompt += f"\nConsider mentioning these related topics if relevant: {', '.join(context['related_topics'])}"
        
        return prompt
