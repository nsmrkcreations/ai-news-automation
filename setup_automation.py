#!/usr/bin/env python3
"""
Setup script for automated news updates with GitHub deployment
"""

import os
import sys
import time
import schedule
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NewsAutomationService:
    def __init__(self):
        self.project_path = Path(__file__).parent
        self.last_update = None
        
    def update_news_and_deploy(self):
        """Update news data and deploy to GitHub Pages"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{timestamp}] Starting news update...")
            
            # Step 1: Fetch fresh news using enhanced service
            print("Fetching news updates with enhanced service...")
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_path)
            result = subprocess.run([sys.executable, 'fetch_news_with_categories.py'], 
                                  capture_output=True, text=True, cwd=self.project_path,
                                  env=env)
            
            if result.returncode == 0:
                print("News data updated successfully")
                
                # Step 2: Deploy to GitHub Pages
                self.deploy_to_github()
                
                self.last_update = datetime.now()
                print(f"Complete update finished at {self.last_update.strftime('%H:%M:%S')}")
                
            else:
                print(f"News update failed: {result.stderr}")
                
        except Exception as e:
            print(f"Update error: {e}")
    
    def deploy_to_github(self):
        """Deploy updated news to GitHub Pages"""
        try:
            # Check if there are any changes to news files (both old and new format)
            news_files = ['public/data/news_latest.json', 'public/data/news.json']
            changes_detected = False
            
            for news_file in news_files:
                result = subprocess.run(['git', 'status', '--porcelain', news_file], 
                                      capture_output=True, text=True, cwd=self.project_path)
                if result.stdout.strip():
                    print(f"Detected changes in {news_file}: {result.stdout.strip()}")
                    changes_detected = True
            
            if not changes_detected:
                print("No changes to news data - skipping deployment")
                return
            
            # Add both news files (enhanced service creates news_latest.json)
            for news_file in news_files:
                if os.path.exists(os.path.join(self.project_path, news_file)):
                    subprocess.run(['git', 'add', news_file], 
                                 cwd=self.project_path, check=True)
            
            # Check if there's actually something to commit
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  cwd=self.project_path)
            
            if result.returncode != 0:  # There are staged changes
                # Commit with timestamp and enhanced service info
                commit_msg = f"Auto-update enhanced news data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                subprocess.run(['git', 'commit', '-m', commit_msg], 
                             cwd=self.project_path, check=True)
                
                # Push to GitHub
                subprocess.run(['git', 'push', 'origin', 'main'], 
                             cwd=self.project_path, check=True)
                
                print("Deployed to GitHub Pages")
            else:
                print("No changes to commit - news data unchanged")
            
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
        except Exception as e:
            print(f"Deployment error: {e}")
    
    def start_service(self):
        """Start the automated service"""
        print("AI News Automation Service Starting...")
        print("=" * 50)
        print("Live Website: https://nsmrkcreations.github.io/ai-news-automation/")
        print("Updates: Every 30 minutes")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
        # Check configuration
        if not os.path.exists('config.yaml'):
            print("ERROR: config.yaml not found")
            print("The enhanced service uses config.yaml instead of API keys")
            return
        
        # Schedule updates every 30 minutes
        schedule.every(30).minutes.do(self.update_news_and_deploy)
        
        # Run initial update
        self.update_news_and_deploy()
        
        # Keep service running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nService stopped by user")

def main():
    """Main entry point"""
    service = NewsAutomationService()
    service.start_service()

if __name__ == "__main__":
    main()
