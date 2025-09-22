#!/usr/bin/env python3
"""
Enhanced News Service with AI Summarization and Web Scraping
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from enhanced_news_service import EnhancedNewsService

def main():
    """Main entry point for enhanced news fetching with AI"""
    try:
        print("Starting Enhanced News Service with AI Summarization...")
        
        # Create and run enhanced service
        service = EnhancedNewsService('config.yaml')
        asyncio.run(service.run())
        
        print("Enhanced news service completed successfully!")
        
    except KeyboardInterrupt:
        print("\nEnhanced news service interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error in enhanced news service: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
