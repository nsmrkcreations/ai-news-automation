import yaml
from pathlib import Path
from typing import List, Dict
import re
from bs4 import BeautifulSoup
import random

class AdSenseManager:
    def __init__(self):
        self.config_path = Path('site/_config/ads.yml')
        self.load_config()
        
    def load_config(self):
        """Load AdSense configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading AdSense config: {e}")
            self.config = {
                'adsense': {'enable': False},
                'ad_units': {},
                'placement': {
                    'paragraph_gap': 4,
                    'min_content_length': 300,
                    'max_ads_per_page': 3
                }
            }

    def get_adsense_head_code(self) -> str:
        """Get AdSense initialization code for head section"""
        if not self.config['adsense']['enable']:
            return ""
            
        client_id = self.config['adsense']['client_id']
        return f"""
<!-- Google AdSense -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={client_id}"
     crossorigin="anonymous"></script>
"""

    def get_auto_ads_code(self) -> str:
        """Get auto ads code if enabled"""
        if not self.config['adsense']['enable'] or not self.config['adsense'].get('auto_ads'):
            return ""
            
        return "<!-- Auto ads enabled -->"

    def insert_ads_in_content(self, content: str) -> str:
        """Insert ads into content at appropriate positions"""
        if not self.config['adsense']['enable']:
            return content
            
        try:
            # Parse content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            paragraphs = soup.find_all('p')
            
            # Check if content is long enough for ads
            if len(content.split()) < self.config['placement']['min_content_length']:
                return content
                
            # Calculate ad positions
            gap = self.config['placement']['paragraph_gap']
            max_ads = self.config['placement']['max_ads_per_page']
            positions = list(range(gap, len(paragraphs), gap))[:max_ads]
            
            # Insert ads at calculated positions
            for pos in reversed(positions):
                if pos < len(paragraphs):
                    ad_unit = self._generate_ad_unit('in_article')
                    if ad_unit:
                        new_tag = soup.new_tag('div')
                        new_tag.string = ad_unit
                        paragraphs[pos].insert_after(new_tag)
            
            # Add after-content ad
            if len(paragraphs) > 3:  # Only add if article is long enough
                after_content_ad = self._generate_ad_unit('after_content')
                if after_content_ad:
                    new_tag = soup.new_tag('div')
                    new_tag.string = after_content_ad
                    soup.append(new_tag)
            
            return str(soup)
            
        except Exception as e:
            print(f"Error inserting ads: {e}")
            return content

    def _generate_ad_unit(self, position: str) -> str:
        """Generate HTML for an ad unit"""
        if not self.config['adsense']['enable']:
            return ""
            
        ad_unit = self.config['ad_units'].get(position)
        if not ad_unit:
            return ""
            
        return f"""
<!-- {position} Ad -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="{self.config['adsense']['client_id']}"
     data-ad-slot="{ad_unit['id']}"
     data-ad-format="{ad_unit['format']}"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({{}});
</script>
"""

    def get_sidebar_ad(self) -> str:
        """Get sidebar ad code"""
        return self._generate_ad_unit('sidebar')

    def prepare_content_for_ads(self, content: Dict[str, str]) -> Dict[str, str]:
        """Prepare content by inserting ads at appropriate positions"""
        if not content or not isinstance(content, dict):
            return content
            
        if not self.config['adsense']['enable']:
            return content
            
        # Detect device type (simplified version)
        is_mobile = self._detect_mobile_user_agent()
        max_ads = self.config['rules']['mobile' if is_mobile else 'desktop']['max_ads']
            
        # Insert ads into the main content
        if 'content' in content:
            # Add before-content ad if enabled
            if self.config['placement'].get('before_content'):
                before_ad = self._generate_ad_unit('before_content')
                if before_ad:
                    content['content'] = before_ad + "\n\n" + content['content']
            
            # Insert in-content ads
            content['content'] = self.insert_ads_in_content(content['content'], max_ads)
            
            # Add native ad if enabled
            if self.config['placement'].get('native_content_index'):
                native_ad = self._generate_ad_unit('native')
                if native_ad:
                    # Insert native ad at specified position
                    paragraphs = content['content'].split('\n\n')
                    index = min(self.config['placement']['native_content_index'], len(paragraphs))
                    paragraphs.insert(index, native_ad)
                    content['content'] = '\n\n'.join(paragraphs)
            
            # Add matched content if enabled
            if self.config['placement'].get('matched_content'):
                matched_content = self._generate_ad_unit('matched_content')
                if matched_content:
                    content['content'] += f"\n\n{matched_content}"
            
        # Add floating ad if enabled and not on mobile
        floating_enabled = (self.config['placement'].get('floating_ad') and 
                          not (is_mobile and self.config['rules']['mobile'].get('disable_floating')))
        
        # Add all ad metadata
        content['adsense'] = {
            'enabled': True,
            'head_code': self.get_adsense_head_code(),
            'auto_ads': self.get_auto_ads_code(),
            'sidebar_ad': self.get_sidebar_ad(),
            'floating_ad': self._generate_ad_unit('floating') if floating_enabled else None,
            'before_content': self._generate_ad_unit('before_content') if self.config['placement'].get('before_content') else None
        }
            
        return content
        
    def _detect_mobile_user_agent(self) -> bool:
        """Simple mobile detection (can be enhanced with actual user agent detection)"""
        return False  # Default to desktop for now
