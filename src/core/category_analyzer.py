"""
Category analyzer for news articles with priority-based detection
"""
import re
from typing import Dict, Any, Optional, List
from collections import Counter

class CategoryAnalyzer:
    """Analyzes articles to determine their categories using multiple methods"""
    
    # Standard category mapping
    CATEGORY_MAPPING = {
        # Map various API category names to our standard ones
        'tech': 'technology',
        'sci': 'science',
        'health': 'health',
        'sport': 'sports',
        'business': 'business',
        'politics': 'politics',
        'entertainment': 'entertainment',
        'opinion': 'opinion',
        'world': 'world',
        'finance': 'markets',
        'financial': 'markets',
        'market': 'markets',
        'stock': 'markets'
    }
    
    # Category keywords and patterns
    CATEGORY_PATTERNS = {
        'technology': [
            r'\b(tech|technology|AI|software|cyber|digital|blockchain|crypto|programming|computer|mobile|gadget|innovation)\b',
            r'\b(robot|automation|machine learning|artificial intelligence|cloud|coding|developer|startup)\b'
        ],
        'science': [
            r'\b(science|research|study|experiment|discovery|physics|chemistry|biology|astronomy|space)\b',
            r'\b(scientist|laboratory|quantum|theory|hypothesis|scientific|universe|nasa|breakthrough)\b'
        ],
        'health': [
            r'\b(health|medical|medicine|doctor|patient|disease|treatment|therapy|vaccine|hospital)\b',
            r'\b(healthcare|wellness|mental health|clinical|surgery|pharmaceutical|drug|covid|virus)\b'
        ],
        'sports': [
            r'\b(sport|game|match|tournament|championship|athlete|team|player|coach|score)\b',
            r'\b(football|soccer|basketball|tennis|baseball|cricket|racing|olympics|league|win)\b'
        ],
        'business': [
            r'\b(business|company|economy|corporate|industry|enterprise|commercial|retail)\b',
            r'\b(profit|revenue|merger|acquisition|startup|entrepreneur|CEO|commerce|employment)\b'
        ],
        'markets': [
            r'\b(stock|market|trading|NYSE|NASDAQ|BSE|NSE|Dow Jones|S&P 500|Nifty|Sensex)\b',
            r'\b(shares|equity|bond|commodity|forex|currency|IPO|dividend|portfolio|bull|bear)\b',
            r'\b(Wall Street|Dalal Street|Mumbai|financial|investment|fund|hedge|mutual)\b',
            r'\b(earnings|quarterly|annual|report|analyst|rating|upgrade|downgrade|target)\b'
        ],
        'politics': [
            r'\b(politic|government|election|president|congress|senate|policy|law|democracy|vote)\b',
            r'\b(campaign|minister|parliament|diplomatic|legislation|party|senator|democrat|republican)\b'
        ],
        'entertainment': [
            r'\b(entertainment|movie|film|music|celebrity|actor|actress|song|concert|show)\b',
            r'\b(tv|television|series|netflix|streaming|hollywood|star|award|performance|media)\b'
        ],
        'world': [
            r'\b(world|global|international|foreign|country|nation|diplomatic|treaty|summit|UN)\b',
            r'\b(war|peace|crisis|conflict|refugee|climate|agreement|trade|relation|embassy)\b'
        ]
    }

    @classmethod
    def get_category(cls, article: Dict[str, Any]) -> str:
        """
        Determine article category using priority-based approach:
        1. Use API-provided category if available
        2. Analyze article content if no category provided
        3. Fall back to 'general' if no category can be determined
        
        Args:
            article: Article dictionary containing various fields
            
        Returns:
            Determined category string
        """
        # 1. Check for API-provided category
        if article.get('category'):
            normalized = cls._normalize_category(article['category'])
            if normalized:
                return normalized
                
        # 2. Try to detect category from content
        return cls._detect_category(article) or 'general'

    @classmethod
    def _normalize_category(cls, category: str) -> Optional[str]:
        """Normalize category names from different providers"""
        category = category.lower().strip()
        
        # Direct match
        if category in cls.CATEGORY_PATTERNS:
            return category
            
        # Check mapping
        for pattern, standard in cls.CATEGORY_MAPPING.items():
            if pattern in category:
                return standard
                
        return None

    @classmethod
    def _detect_category(cls, article: Dict[str, Any]) -> Optional[str]:
        """
        Detect category by analyzing article content
        
        Args:
            article: Article dictionary with title, description, and content
            
        Returns:
            Detected category or None if uncertain
        """
        # Combine all relevant text fields
        text = ' '.join(filter(None, [
            article.get('title', ''),
            article.get('description', ''),
            article.get('content', '')
        ])).lower()
        
        # Count matches for each category
        category_scores = Counter()
        
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                category_scores[category] += matches
                
        # Return category with highest score if it meets threshold
        if category_scores:
            top_category = category_scores.most_common(1)[0]
            if top_category[1] >= 2:  # Minimum score threshold
                return top_category[0]
                
        return None

    @classmethod
    def get_confidence_scores(cls, article: Dict[str, Any]) -> Dict[str, float]:
        """
        Get confidence scores for each category
        
        Args:
            article: Article dictionary
            
        Returns:
            Dictionary of category:confidence_score pairs
        """
        text = ' '.join(filter(None, [
            article.get('title', ''),
            article.get('description', ''),
            article.get('content', '')
        ])).lower()
        
        scores = {}
        total_matches = 0
        
        # Count matches for each category
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            category_matches = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                category_matches += matches
                total_matches += matches
            scores[category] = category_matches
            
        # Convert to confidence scores
        if total_matches > 0:
            return {k: v/total_matches for k, v in scores.items()}
        return {k: 0.0 for k in cls.CATEGORY_PATTERNS.keys()}
