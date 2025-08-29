import os
import re

def read_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def update_html_files():
    # Read the template
    template = read_template('public/templates/header.html')
    
    # Page configurations
    pages = {
        'index.html': {
            'title': 'AI-Powered News Aggregator',
            'description': 'Stay informed with AI-curated news from trusted sources',
            'active': 'HOME'
        },
        'categories.html': {
            'title': 'News Categories',
            'description': 'Browse news by category - technology, business, science, and more',
            'active': 'CATEGORIES'
        },
        'about.html': {
            'title': 'About Us',
            'description': 'Learn about NewsSurgeAI - AI-powered news aggregation',
            'active': 'ABOUT'
        },
        'contact.html': {
            'title': 'Contact Us',
            'description': 'Get in touch with NewsSurgeAI team',
            'active': 'CONTACT'
        },
        'category.html': {
            'title': 'Category News',
            'description': 'Latest news from your selected category',
            'active': 'CATEGORIES'
        },
        'privacy.html': {
            'title': 'Privacy Policy',
            'description': 'NewsSurgeAI privacy policy and data handling practices',
            'active': ''
        },
        'terms.html': {
            'title': 'Terms of Service',
            'description': 'NewsSurgeAI terms of service and usage conditions',
            'active': ''
        },
        'faq.html': {
            'title': 'FAQ',
            'description': 'Frequently asked questions about NewsSurgeAI',
            'active': ''
        },
        'feedback.html': {
            'title': 'Feedback',
            'description': 'Share your feedback about NewsSurgeAI',
            'active': ''
        },
        'newsletter.html': {
            'title': 'Newsletter',
            'description': 'Subscribe to NewsSurgeAI newsletter',
            'active': ''
        }
    }
    
    # Process each HTML file
    for filename, config in pages.items():
        filepath = os.path.join('public', filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace the header section
        new_header = template
        new_header = new_header.replace('%TITLE%', config['title'])
        new_header = new_header.replace('%DESCRIPTION%', config['description'])
        
        # Set active states
        for nav_item in ['HOME', 'CATEGORIES', 'ABOUT', 'CONTACT']:
            if nav_item == config['active']:
                new_header = new_header.replace(f'%{nav_item}_ACTIVE%', 'active')
            else:
                new_header = new_header.replace(f'%{nav_item}_ACTIVE%', '')
        
        # Replace old header with new one
        content = re.sub(
            r'<!DOCTYPE html>[\s\S]*?</header>',
            new_header,
            content
        )
        
        # Write the updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    update_html_files()
