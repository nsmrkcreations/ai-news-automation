"""GDELT provider implementation using gdeltdoc package"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from gdeltdoc import GdeltDoc, Filters
from .news_providers import NewsProvider
from .logger import get_logger

logger = get_logger(__name__)

class GdeltNewsProvider(NewsProvider):
    def __init__(self):
        """Initialize the GDELT provider."""
        super().__init__("GDELT")
        self.gdelt = GdeltDoc()
        self.is_available = True
    
    # Theme to category mapping
        self.category_mapping = {
            'technology': {
                'themes': ['TECH', 'TECH_SOCIAL', 'TECH_AI', 'TECH_MOBILE', 'SCI_TECH'],
                'domains': ['techcrunch.com', 'wired.com', 'theverge.com', 'arstechnica.com']
            },
            'business': {
                'themes': ['BUS', 'ECON', 'BUS_FINANCE', 'MONEY', 'TRADE'],
                'domains': ['bloomberg.com', 'cnbc.com', 'wsj.com', 'reuters.com/business']
            },
            'science': {
                'themes': ['SCI', 'ENV', 'SCI_SPACE', 'TECH_SCIENCE'],
                'domains': ['scientificamerican.com', 'nature.com', 'science.org', 'newscientist.com']
            },
            'sports': {
                'themes': ['SPORTS', 'SPORTS_SOCCER', 'SPORTS_BASKETBALL'],
                'domains': ['espn.com', 'sports.yahoo.com', 'cbssports.com']
            },
            'entertainment': {
                'themes': ['ENT', 'ENT_MOVIE', 'ENT_TV', 'ENT_MUSIC'],
                'domains': ['variety.com', 'hollywoodreporter.com', 'deadline.com']
            },
            'politics': {
                'themes': ['POL', 'GOV', 'ELECTION', 'POLICY'],
                'domains': ['politico.com', 'thehill.com', 'realclearpolitics.com']
            }
        }

    def _build_filters(self, category: str = None) -> Filters:
        """Build GDELT filters based on category
        
        Args:
            category: Optional category to filter by
            
        Returns:
            GDELT filters object
        """
        # Base filters
        filters = Filters(
            start_date=datetime.now() - timedelta(days=1),  # Last 24 hours
            end_date=datetime.now(),
            country=['US'],  # US sources
            language=['English']  # English articles
        )

        if category and category in self.category_mapping:
            cat_map = self.category_mapping[category]
            theme_filter = ' OR '.join(cat_map['themes'])
            domain_filter = ' OR '.join(cat_map['domains'])
            filters.theme = theme_filter
            filters.domain = domain_filter
            
        return filters

    def _process_article(self, article: Dict[str, Any], category: str = None) -> Optional[Dict[str, Any]]:
        """Process a GDELT article into our standard format
        
        Args:
            article: Raw GDELT article
            category: Optional category being searched for
            
        Returns:
            Processed article or None if invalid
        """
        try:
            # Extract basic fields
            url = article.get('url')
            title = article.get('title')
            
            if not url or not title:
                return None
                
            # Get the best available description
            description = (
                article.get('seendescription') or
                article.get('description') or
                article.get('seentext', '')[:200]  # Fallback to first 200 chars of content
            ).strip()

            # Get best available image
            image_url = (
                article.get('socialimage') or
                article.get('image')
            )

            # Clean source name
            source_name = article.get('domain', '').replace('www.', '').split('.')[0].title()
            if not source_name:
                source_name = 'GDELT'
            
            # Determine category
            if category:
                determined_category = category
            else:
                # Try to determine from themes
                themes = article.get('themes', [])
                if isinstance(themes, str):
                    themes = [themes]
                
                for cat, mapping in self.category_mapping.items():
                    if any(theme in themes for theme in mapping['themes']):
                        determined_category = cat
                        break
                else:
                    determined_category = 'general'

            return {
                'title': title,
                'description': description,
                'url': url,
                'urlToImage': image_url,
                'publishedAt': article.get('publishedAt', datetime.now().isoformat()),
                'source': {
                    'id': 'gdelt',
                    'name': source_name
                },
                'category': determined_category,
                'fetchedAt': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing GDELT article: {str(e)}")
            return None

    def fetch_news(self, category: str = None) -> List[Dict[str, Any]]:
        """Fetch news from GDELT
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of processed news articles
        """
        if not self.is_available:
            raise Exception(f"Provider {self.name} is not available")
            
        try:
            # Build filters
            filters = self._build_filters(category)
            
            # Fetch articles
            articles = self.gdelt.article_search(filters)
            if articles is None or articles.empty:
                logger.warning("No articles returned from GDELT")
                return []
                
            # Convert to list of dicts and process
            processed = []
            for _, article in articles.iterrows():
                processed_article = self._process_article(article.to_dict(), category)
                if processed_article:
                    processed.append(processed_article)
                    
            return processed
            
        except Exception as e:
            self.mark_unavailable(e)
            logger.error(f"Error fetching from GDELT: {str(e)}")
            raise
            params = self._build_query(category)
            logger.info(f"GDELT query for category: {category}")
            
            # Make request
            articles = self._make_request(params)
            
            # Return early if no articles
            if not articles:
                logger.warning("No articles returned from GDELT")
                return []
            
            for article in articles:
                try:
                    # Extract video content if available
                    video_url = None
                    if article.get('socialimage') and '.mp4' in article['socialimage'].lower():
                        video_url = article['socialimage']
                    elif article.get('url') and ('youtube.com' in article['url'] or 'youtu.be' in article['url']):
                        youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([^\s&]+)'
                        match = re.search(youtube_pattern, article['url'])
                        if match:
                            video_url = f"https://www.youtube.com/embed/{match.group(1)}"

                    # Get the best available image
                    image_url = (
                        article.get('socialimage') or  # Prefer social image
                        article.get('image') or        # Fall back to main image
                        None                          # No image available
                    )

                    # Format date string with better error handling
                    try:
                        date_str = article.get('seendate', article.get('date', article.get('sourcedatetime')))
                        if date_str:
                            # Handle both Unix timestamp and ISO format
                            try:
                                if isinstance(date_str, (int, float)):
                                    parsed_date = datetime.fromtimestamp(int(date_str))
                                else:
                                    parsed_date = parse_date(str(date_str))
                                published_at = parsed_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                            except (ValueError, TypeError):
                                published_at = datetime.now().isoformat()
                        else:
                            published_at = datetime.now().isoformat()
                    except Exception as e:
                        logger.warning(f"Error parsing date from GDELT: {e}")
                        published_at = datetime.now().isoformat()

                    # Clean and validate title and description
                    title = article.get('title', '').strip()
                    if not title:  # Skip articles without titles
                        continue

                    description = article.get('seendescription', article.get('description', '')).strip()
                    if not description:  # Use excerpt or first part of seen text if description is missing
                        description = article.get('seentext', '')[:200].strip()

                    # Extract and clean source name
                    source_name = article.get('domain', '').replace('www.', '').split('.')[0].title()
                    if not source_name:
                        source_name = 'GDELT'

                    # Determine category from API response or content
                    determined_category = self._determine_category(article, default_category=category)

                    # Build article with validation
                    processed_article = {
                        'title': title,
                        'description': description,
                        'url': article.get('url'),
                        'urlToImage': image_url,
                        'publishedAt': published_at,
                        'source': {
                            'id': 'gdelt',
                            'name': source_name
                        },
                        'category': determined_category,
                        'fetchedAt': datetime.now().isoformat(),
                        'videoUrl': video_url,
                        'sentiment': float(article.get('tone', 0)),  # Convert to float with default 0
                        'locations': list(set(article.get('locations', []))),  # Deduplicate locations
                        'persons': list(set(article.get('persons', []))),      # Deduplicate persons
                        'organizations': list(set(article.get('organizations', [])))  # Deduplicate organizations
                    }

                    # Only add articles with required fields
                    if processed_article['url'] and processed_article['title']:
                        processed_articles.append(processed_article)
                except Exception as e:
                    logger.error(f"Error processing article: {str(e)}")
                    continue

            self.mark_available()
            return processed_articles

        except Exception as e:
            self.mark_unavailable(e)
            raise
