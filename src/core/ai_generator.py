import openai
import os
from typing import List, Dict

class AIContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.max_tokens = 1500  # Approximately 1000 words

    def create_article(self, topic: str, keywords: List[str], context: Dict = None) -> str:
        """Generate an SEO-optimized article using OpenAI"""
        prompt = self._create_prompt(topic, keywords, context)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional tech journalist writing informative, engaging articles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def _create_prompt(self, topic: str, keywords: List[str], context: Dict = None) -> str:
        """Create an optimized prompt for article generation"""
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
