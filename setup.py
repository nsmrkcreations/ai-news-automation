"""
Script to set up the project environment
"""
import os
import sys
import subprocess
import shutil

def setup_project():
    """Set up the project environment"""
    print("Setting up AI News Automation project...")
    
    # Create required directories if they don't exist
    directories = ['logs', 'cache', 'public/data', 'public/images/news']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Copy .env.example to .env if it doesn't exist
    if not os.path.exists('.env'):
        shutil.copy2('.env.example', '.env')
        print("Created .env file from .env.example")
    
    # Install Python dependencies
    print("\nInstalling Python dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # Create initial news.json file
    if not os.path.exists('public/data/news.json'):
        with open('public/data/news.json', 'w', encoding='utf-8') as f:
            f.write('[]')
        print("Created initial news.json file")
        
    # Set up Ollama
    print("\nSetting up Ollama...")
    subprocess.run([sys.executable, 'src/setup_ollama.py'])
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Install Ollama from https://ollama.ai (optional for AI features)")
    print("2. Pull the llama3.2 model: ollama pull llama3.2")
    print("3. Run the enhanced service: python fetch_news_with_categories.py")
    print("4. Run tests using: python -m unittest discover tests")
    print("5. Start the development server: python src/webapp.py")
    print("6. In a separate terminal, start news updates: python src/update_news.py")

if __name__ == "__main__":
    setup_project()
