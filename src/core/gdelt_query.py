"""
GDELT query builder using GDELT 2.0 API format
"""
from typing import Dict, Optional
import urllib.parse

def build_gdelt_query(category: str = None) -> Dict[str, str]:
    """Build a GDELT query based on category
    
    Args:
        category: The news category to filter by
        
    Returns:
        Dictionary with query parameters for GDELT API
    """
    # Base parameters
    params = {
        'format': 'json',
        'maxrecords': '50',
        'timespan': '24h',  # Last 24 hours
        'sort': 'DateDesc',  # Most recent first
        'sourcecountry': 'US',  # US sources
        'trans': 'GoogleTranslate',  # Use translation if needed
    }
    
    # Build query string
    query_parts = [
        'sourcecountry:US',
        'sourcelang:eng',
        'sourcetype:news'
    ]
    
    # Category specific queries
    if category:
        category_queries = {
            'technology': ['(theme:TECH OR theme:SCI_TECH OR domain:"techcrunch.com" OR domain:"theverge.com" OR domain:"wired.com")'],
            'business': ['(theme:BUS OR theme:ECON OR domain:"bloomberg.com" OR domain:"cnbc.com" OR domain:"wsj.com")'],
            'science': ['(theme:SCI OR theme:ENV OR domain:"scientificamerican.com" OR domain:"nature.com" OR domain:"science.org")'],
            'sports': ['(theme:SPORTS OR domain:"espn.com" OR domain:"cbssports.com" OR domain:"sports.yahoo.com")'],
            'entertainment': ['(theme:ENT OR domain:"variety.com" OR domain:"hollywoodreporter.com" OR domain:"deadline.com")'],
            'politics': ['(theme:POL OR theme:GOV OR domain:"politico.com" OR domain:"thehill.com" OR domain:"realclearpolitics.com")'],
            'general': ['(domain:"reuters.com" OR domain:"apnews.com" OR domain:"npr.org")']
        }
        
        if category in category_queries:
            query_parts.append(category_queries[category][0])
    
    # Combine query parts
    query = ' AND '.join(query_parts)
    
    # Add query to parameters
    params['query'] = query
    
    return params
