"""
AI Generator module for article summarization and categorization using Ollama
"""
import os
import json
import requests
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class AIGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = os.getenv('OLLAMA_MODEL', 'llama2')
        self.max_retries = 3
        
    def _make_ollama_request(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        """
        Make a request to Ollama API with retry logic
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7
                        }
                    },
                    timeout=30
                )
                response.raise_for_status()
                return response.json().get('response', '').strip()
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("All attempts failed")
                    return None
                continue
            
    def summarize_article(self, article: Dict[str, Any]) -> Tuple[str, str, bool]:
        """
        Summarize article and determine if it's breaking news
        Returns:
            Tuple of (summary, category, is_breaking)
        """
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Combine available text
            full_text = f"Title: {title}\n\nDescription: {description}\n\nContent: {content}"
            
            # Create prompts
            summary_prompt = (
                "Please provide a concise, engaging summary of this news article in about 2-3 sentences. "
                "Focus on the main points and any significant implications:\n\n"
                f"{full_text}"
            )
            
            category_prompt = (
                "Based on this article, classify it into exactly ONE of these categories: "
                "technology, business, science, world, general. "
                "Respond with ONLY the category name in lowercase:\n\n"
                f"{full_text}"
            )
            
            breaking_prompt = (
                "Analyze if this is breaking news based on its urgency, significance, and impact. "
                "Consider factors like immediate public interest, major developments, or significant events. "
                "Respond with ONLY 'true' or 'false':\n\n"
                f"{full_text}"
            )
            
            # Get AI responses
            summary = self._make_ollama_request(summary_prompt, max_tokens=200) or description
            category = self._make_ollama_request(category_prompt, max_tokens=50)
            breaking_response = self._make_ollama_request(breaking_prompt, max_tokens=50)
            
            # Process category
            valid_categories = ['technology', 'business', 'science', 'world', 'general']
            category = category.lower() if category else 'general'
            if category not in valid_categories:
                category = 'general'
            
            # Process breaking news status
            is_breaking = breaking_response.lower() == 'true' if breaking_response else False
            
            return summary, category, is_breaking
            
        except Exception as e:
            logger.error(f"Error in AI processing: {str(e)}")
            return description, 'general', False
            
    def check_ollama_status(self) -> bool:
        """
        Check if Ollama is running and the model is available
        """
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags")
            response.raise_for_status()
            
            # Check if our model is available
            models = response.json()
            return any(model.get('name') == self.model for model in models)
            
        except requests.exceptions.RequestException:
            return False
