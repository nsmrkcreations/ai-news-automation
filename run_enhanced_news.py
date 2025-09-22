#!/usr/bin/env python3
"""
CLI runner for Enhanced News Service
"""
import argparse
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from enhanced_news_service import EnhancedNewsService

def main():
    parser = argparse.ArgumentParser(description='Enhanced News Service with AI Summarization')
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path (default: config.yaml)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without publishing or committing')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        # Create service
        service = EnhancedNewsService(config_path=args.config)
        
        # Set logging level if verbose
        if args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Run service
        print("🚀 Starting Enhanced News Service...")
        asyncio.run(service.run())
        print("✅ News service completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Service interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()