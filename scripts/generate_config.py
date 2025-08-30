#!/usr/bin/env python3
"""
Configuration Generator for AI News Automation
Generates config.js with environment variables to mask sensitive IDs
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def generate_config():
    """Generate config.js file with environment variables"""
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration values
    ga_id = os.getenv('GA_MEASUREMENT_ID', 'G-DX7CWQ62HW')
    adsense_publisher = os.getenv('ADSENSE_PUBLISHER_ID', 'ca-pub-1318338562171737')
    
    # Generate config.js content
    config_content = f"""/**
 * Configuration file for AI News Automation
 * Generated from environment variables - DO NOT EDIT MANUALLY
 */

window.APP_CONFIG = {{
    // Google Analytics ID
    GA_MEASUREMENT_ID: '{ga_id}',
    
    // Google AdSense Publisher ID
    ADSENSE_PUBLISHER_ID: '{adsense_publisher}',
    
    // AdSense Configuration - using auto ads
    ADSENSE_AUTO_ADS: true,
    
    // Site configuration
    SITE_NAME: 'NewSurgeAI',
    VERSION: '1.0.0',
    GENERATED_AT: '{os.getenv("BUILD_TIME", "development")}'
}};

// Development warning
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
    console.log('🔧 Development mode - using environment configuration');
}}
"""
    
    # Write to public directory
    public_dir = Path(__file__).parent.parent / 'public' / 'js'
    config_path = public_dir / 'config.js'
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ Configuration generated: {config_path}")
        print(f"   GA ID: {ga_id}")
        print(f"   AdSense: {adsense_publisher}")
        
    except Exception as e:
        print(f"❌ Failed to generate config: {e}")
        return False
    
    return True

if __name__ == '__main__':
    generate_config()
