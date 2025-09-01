import os
import json
import requests
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class AIGenerator:
    def __init__(self):
        self.ollama_url = 'http://localhost:11434/api/generate'
        self.model = os.getenv('OLLAMA_MODEL', 'llama2')
        self.max_retries = 3

    def _make_ollama_request(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        'model': self.model,
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'num_predict': max_tokens,
                            'temperature': 0.7
                        }
                    },
                    timeout=30
                )
                response.raise_for_status()
                return response.json().get('response', '').strip()
            except requests.exceptions.RequestException as e:
                logger.error(f'Attempt {attempt + 1} failed: {str(e)}')
                if attempt == self.max_retries - 1:
                    logger.error('All attempts failed')
                    return None
                continue

    def _calculate_summary_length(self, text_length: int) -> int:
        if text_length <= 500:  # Short articles
            return 100
        elif text_length <= 1000:  # Medium articles
            return 150
        elif text_length <= 2000:  # Long articles
            return 200
        else:  # Very long articles
            return 250

    def _detect_category_from_content(self, text: str) -> str:
        text = text.lower()
        
        # Define keywords per category
        category_keywords = {
            'technology': [
                'technology', 'software', 'ai', 'robot', 'app', 'cyber', 'digital',
                'computer', 'blockchain', 'startup', 'innovation', 'quantum', 'battery'
            ],
            'business': [
                'business', 'market', 'stock', 'economy', 'finance', 'trade', 
                'investment', 'company', 'industry', 'corporate', 'profit'
            ],
            'science': [
                'science', 'research', 'study', 'discovery', 'scientists',
                'physics', 'chemistry', 'biology', 'medicine', 'space'
            ],
            'world': [
                'world', 'international', 'global', 'foreign', 'diplomat',
                'country', 'nation', 'government', 'president', 'minister'
            ]
        }
        
        # Count keyword matches for each category
        category_scores = {cat: 0 for cat in category_keywords}
        
        # Score each category by counting keyword occurrences
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    category_scores[category] += 1
        
        # Return category with highest score, or 'general' if no strong matches
        max_score = max(category_scores.values())
        if max_score > 0:
            for category, score in category_scores.items():
                if score == max_score:
                    return category
        
        return 'general'

    def summarize_article(self, article: Dict[str, Any]) -> Tuple[str, str, bool, bool]:
        """
        Summarize an article using AI.
        
        Returns:
            Tuple of (summary, category, is_breaking, ai_enhanced)
            where ai_enhanced indicates if AI successfully processed the article
        """
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            api_category = article.get('category', '').lower() if article.get('category') else ''

            # Combine available text and calculate length
            full_text = f'Title: {title}\n\nDescription: {description}\n\nContent: {content}'
            text_length = len(full_text.split())
            target_length = self._calculate_summary_length(text_length)

            # Create prompts
            summary_prompt = (
                f'Please provide a comprehensive summary of this news article in {target_length} words. '
                'Include key details, context, and implications. '
                'Make sure the summary gives readers a complete understanding of: '
                '1. What happened or was announced '
                '2. Why it\'s important or its potential impact '
                '3. Key background or context needed to understand the news '
                '4. Any significant conclusions or next steps\n\n'
                f'{full_text}'
            )

            category_prompt = (
                'Based on this article, classify it into exactly ONE of these categories: '
                'technology, business, science, world, general. '
                'Respond with ONLY the category name in lowercase:\n\n'
                f'{full_text}'
            )

            breaking_prompt = (
                'Analyze if this is breaking news based on its urgency, significance, and impact. '
                'Consider factors like immediate public interest, major developments, or significant events. '
                'Respond with ONLY true or false:\n\n'
                f'{full_text}'
            )

            # Get AI responses with appropriate token limits
            target_tokens = target_length * 2  # Approximate tokens for target word count
            summary = self._make_ollama_request(summary_prompt, max_tokens=target_tokens)
            if not summary or len(summary.split()) < target_length * 0.8:  # If summary is too short
                summary = description

            # Handle category priority
            valid_categories = ['technology', 'business', 'science', 'world', 'general']
            final_category = 'general'

            # 1. Try API category first
            if api_category and api_category in valid_categories:
                final_category = api_category
            else:
                # 2. Try AI categorization
                ai_category = self._make_ollama_request(category_prompt, max_tokens=50)
                if ai_category and ai_category.lower() in valid_categories:
                    final_category = ai_category.lower()
                else:
                    # 3. Use keyword analysis as fallback
                    detected_category = self._detect_category_from_content(full_text)
                    if detected_category in valid_categories:
                        final_category = detected_category

            # Get breaking news status
            breaking_response = self._make_ollama_request(breaking_prompt, max_tokens=50)
            is_breaking = breaking_response.lower() == 'true' if breaking_response else False

            # Log category determination process
            logger.info(f"Category determination for '{title[:50]}...': "
                       f"API={api_category}, AI={ai_category if 'ai_category' in locals() else 'N/A'}, "
                       f"Final={final_category}")

            # Determine if AI successfully enhanced the article
            ai_enhanced = bool(summary and summary != description)
            
            return summary, final_category, is_breaking, ai_enhanced

        except Exception as e:
            logger.error(f'Error in AI processing: {str(e)}')
            return description, 'general', False, False
