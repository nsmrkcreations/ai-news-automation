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
            print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] Starting news update...")
            
            # Step 1: Fetch fresh news
            result = subprocess.run([sys.executable, 'quick_test.py'], 
                                  capture_output=True, text=True, cwd=self.project_path)
            
            if result.returncode == 0:
                print("✅ News data updated successfully")
                
                # Step 2: Deploy to GitHub Pages
                self.deploy_to_github()
                
                self.last_update = datetime.now()
                print(f"✅ Complete update finished at {self.last_update.strftime('%H:%M:%S')}")
                
            else:
                print(f"❌ News update failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Update error: {e}")
    
    def deploy_to_github(self):
        """Deploy updated news to GitHub Pages"""
        try:
            # Check if there are any changes to news.json (modified or untracked)
            result = subprocess.run(['git', 'status', '--porcelain', 'public/data/news.json'], 
                                  capture_output=True, text=True, cwd=self.project_path)
            
            if not result.stdout.strip():
                print("📰 No changes to news data - skipping deployment")
                return
            
            print(f"📝 Detected changes: {result.stdout.strip()}")
            
            # Add only the news.json file
            subprocess.run(['git', 'add', 'public/data/news.json'], 
                         cwd=self.project_path, check=True)
            
            # Check if there's actually something to commit
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  cwd=self.project_path)
            
            if result.returncode != 0:  # There are staged changes
                # Commit with timestamp
                commit_msg = f"Auto-update news data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                subprocess.run(['git', 'commit', '-m', commit_msg], 
                             cwd=self.project_path, check=True)
                
                # Push to GitHub
                subprocess.run(['git', 'push', 'origin', 'main'], 
                             cwd=self.project_path, check=True)
                
                print("🚀 Deployed to GitHub Pages")
            else:
                print("📰 No changes to commit - news data unchanged")
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git operation failed: {e}")
        except Exception as e:
            print(f"❌ Deployment error: {e}")
    
    def start_service(self):
        """Start the automated service"""
        print("🚀 AI News Automation Service Starting...")
        print("=" * 50)
        print("📍 Live Website: https://nsmrkcreations.github.io/ai-news-automation/")
        print("⏰ Updates: Every 30 minutes")
        print("🔄 Press Ctrl+C to stop")
        print("=" * 50)
        
        # Check environment
        if not os.getenv('NEWS_API_KEY'):
            print("❌ ERROR: NEWS_API_KEY not found in .env file")
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
            print("\n👋 Service stopped by user")

def main():
    """Main entry point"""
    service = NewsAutomationService()
    service.start_service()

if __name__ == "__main__":
    main()
