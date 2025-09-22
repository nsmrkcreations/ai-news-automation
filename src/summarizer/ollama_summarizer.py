"""
Ollama-based AI summarization service
"""
import subprocess
import json
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OllamaSummarizer:
    """AI summarizer using Ollama"""
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get('enabled', True)
        self.model = config.get('model', 'llama3.2')
        self.timeout = config.get('timeout_seconds', 15)
        self.max_tokens = config.get('max_tokens', 150)
        self.use_cli = config.get('cli', False)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        
    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize article using Ollama or fallback
        
        Args:
            article: Article dictionary
            
        Returns:
            Dict with summary and keywords
        """
        # If AI is disabled, use fallback immediately
        if not self.enabled:
            logger.info("AI summarization disabled, using fallback")
            return self.fallback_summary(article)
            
        try:
            # Prepare content for summarization
            content = f"Title: {article.get('title', '')}\n"
            content += f"Excerpt: {article.get('excerpt', '')}\n"
            content += f"Content: {article.get('content_snippet', '')}"
            
            # Create prompt
            prompt = self.create_prompt(content, article.get('category', 'general'))
            
            # Get AI response with timeout
            if self.use_cli:
                response = self.call_ollama_cli(prompt)
            else:
                response = self.call_ollama_http(prompt)
            
            if response:
                result = self.parse_response(response)
                result['ai_enhanced'] = True
                return result
            else:
                logger.warning("AI response failed, using fallback")
                return self.fallback_summary(article)
                
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return self.fallback_summary(article)
    
    def create_prompt(self, content: str, category: str) -> str:
        """Create summarization prompt"""
        category_context = {
            'technology': 'Focus on technological innovations, implications, and industry impact.',
            'business': 'Emphasize business implications, market impact, and economic significance.',
            'science': 'Highlight scientific discoveries, research findings, and their implications.',
            'markets': 'Focus on market movements, financial implications, and investor impact.',
            'politics': 'Emphasize political implications, policy changes, and governance impact.',
            'health': 'Focus on health implications, medical significance, and public health impact.',
            'sports': 'Highlight athletic achievements, competition results, and sports industry news.',
            'entertainment': 'Focus on entertainment industry news, cultural impact, and celebrity updates.',
            'general': 'Provide a balanced summary of the key information and main points.'
        }
        
        context = category_context.get(category, 'Provide a balanced summary of the key information.')
        
        # Ultra-short prompt for fast response
        return f"""Summarize this {category} news in JSON:

{content[:400]}

Format: {{"summary": "2 sentences max", "keywords": ["word1", "word2", "word3"], "insights": "1 key insight"}}

Be concise."""
    
    def call_ollama_cli(self, prompt: str) -> Optional[str]:
        """Call Ollama via CLI"""
        try:
            cmd = ['ollama', 'run', self.model]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(input=prompt, timeout=self.timeout)
                
                if process.returncode == 0:
                    return stdout.strip()
                else:
                    logger.error(f"Ollama CLI error: {stderr}")
                    return None
            except subprocess.TimeoutExpired:
                logger.error("Ollama CLI timeout")
                process.kill()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.terminate()
                return None
                
        except FileNotFoundError:
            logger.error("Ollama CLI not found. Please install Ollama.")
            return None
        except Exception as e:
            logger.error(f"Ollama CLI error: {str(e)}")
            return None
    
    def call_ollama_http(self, prompt: str) -> Optional[str]:
        """Call Ollama via HTTP API"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": self.max_tokens,
                    "temperature": 0.3,  # Lower temperature for more consistent output
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            logger.debug(f"Sending request to {url} with model {self.model}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            if not ai_response:
                logger.warning("Empty response from Ollama")
                return None
            
            logger.debug(f"Received response length: {len(ai_response)} characters")
            logger.debug(f"Response preview: {ai_response[:100]}...")
            
            return ai_response
            
        except requests.exceptions.Timeout:
            logger.error(f"Ollama HTTP timeout after {self.timeout} seconds")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama HTTP request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Ollama HTTP error: {str(e)}")
            return None
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse Ollama response"""
        try:
            # Clean the response
            response = response.strip()
            
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                
                # Clean up common JSON issues
                json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                json_str = ' '.join(json_str.split())  # Remove extra whitespace
                
                try:
                    parsed = json.loads(json_str)
                    
                    # Validate and clean the parsed data
                    summary = parsed.get('summary', '').strip()
                    keywords = parsed.get('keywords', [])
                    insights = parsed.get('insights', '').strip()
                    
                    # Ensure keywords is a list
                    if isinstance(keywords, str):
                        keywords = [k.strip() for k in keywords.split(',')]
                    elif not isinstance(keywords, list):
                        keywords = []
                    
                    # Clean keywords
                    keywords = [k.strip().lower() for k in keywords if k.strip()][:5]
                    
                    # Ensure we have content
                    if not summary:
                        summary = self._extract_summary_from_text(response)
                    
                    return {
                        'summary': summary[:300],  # Limit length
                        'keywords': keywords,
                        'insights': insights[:200]  # Limit length
                    }
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing failed: {str(e)}, trying text extraction")
                    return self._extract_from_text(response)
            else:
                # No JSON found, extract from text
                return self._extract_from_text(response)
                
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return self._extract_from_text(response)
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract summary from plain text response"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Try to find summary-like content
        summary_lines = []
        for line in lines:
            if len(line) > 20 and not line.startswith('{') and not line.startswith('}'):
                summary_lines.append(line)
                if len(summary_lines) >= 3:
                    break
        
        summary = ' '.join(summary_lines) if summary_lines else text[:200]
        
        # Extract potential keywords from the text
        words = text.lower().split()
        keywords = [word.strip('.,!?()[]') for word in words 
                   if len(word) > 4 and word.isalpha()][:5]
        
        return {
            'summary': summary[:300],
            'keywords': keywords,
            'insights': f"This article provides important information about the topic."
        }
    
    def _extract_summary_from_text(self, text: str) -> str:
        """Extract a summary from text when JSON parsing fails"""
        sentences = text.split('. ')
        # Take first 2-3 meaningful sentences
        good_sentences = [s.strip() for s in sentences 
                         if len(s.strip()) > 20 and not s.strip().startswith('{')][:3]
        
        if good_sentences:
            summary = '. '.join(good_sentences)
            if not summary.endswith('.'):
                summary += '.'
            return summary
        else:
            return text[:200] + '...' if len(text) > 200 else text
    
    def fallback_summary(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback summary when AI fails"""
        excerpt = article.get('excerpt', '')
        title = article.get('title', '')
        content_snippet = article.get('content_snippet', '')
        
        # Create simple summary from available content
        if excerpt and len(excerpt) > 50:
            # Use excerpt as summary, limit to 2-3 sentences
            sentences = excerpt.split('. ')[:3]
            summary = '. '.join(sentences)
            if not summary.endswith('.'):
                summary += '.'
        elif content_snippet and len(content_snippet) > 50:
            # Use content snippet, limit to 2-3 sentences
            sentences = content_snippet.split('. ')[:3]
            summary = '. '.join(sentences)
            if not summary.endswith('.'):
                summary += '.'
        elif title:
            summary = f"This article discusses {title.lower()}. Read the full article for more details."
        else:
            summary = "News article with important updates on current developments."
        
        # Extract simple keywords from title and content
        keywords = []
        text_for_keywords = f"{title} {excerpt}".lower()
        
        # Common news keywords to look for
        common_keywords = ['technology', 'business', 'market', 'company', 'government', 
                          'economy', 'research', 'study', 'report', 'analysis', 'data',
                          'growth', 'development', 'innovation', 'investment', 'revenue']
        
        # Extract keywords from title first
        if title:
            words = title.lower().split()
            title_keywords = [word.strip('.,!?()[]') for word in words 
                            if len(word) > 4 and word.isalpha()][:3]
            keywords.extend(title_keywords)
        
        # Add relevant common keywords found in text
        for keyword in common_keywords:
            if keyword in text_for_keywords and keyword not in keywords:
                keywords.append(keyword)
                if len(keywords) >= 5:
                    break
        
        # Fill remaining slots with category-based keywords
        category = article.get('category', 'general')
        category_keywords = {
            'technology': ['tech', 'digital', 'software', 'AI', 'innovation'],
            'business': ['finance', 'corporate', 'industry', 'market', 'economy'],
            'science': ['research', 'study', 'discovery', 'scientific', 'analysis'],
            'markets': ['trading', 'stocks', 'financial', 'investment', 'economic'],
            'health': ['medical', 'healthcare', 'treatment', 'patients', 'clinical'],
            'sports': ['athletic', 'competition', 'team', 'performance', 'championship']
        }
        
        if category in category_keywords:
            for kw in category_keywords[category]:
                if kw not in keywords and len(keywords) < 5:
                    keywords.append(kw)
        
        # Ensure we have at least some keywords
        if not keywords:
            keywords = [category, 'news', 'update']
        
        return {
            'summary': summary[:300],  # Limit summary length
            'keywords': keywords[:5],  # Limit to 5 keywords
            'insights': f"This {category} article provides updates on current developments in the field.",
            'ai_enhanced': False
        }