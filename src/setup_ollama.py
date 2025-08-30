"""
Script to check and set up Ollama
"""
import os
import sys
import subprocess
import requests
import time
import logging
from typing import Tuple

def check_ollama() -> Tuple[bool, str]:
    """
    Check if Ollama is installed and running
    Returns:
        Tuple of (is_installed, status_message)
    """
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            return True, "Ollama is running"
    except requests.exceptions.ConnectionError:
        pass
    
    # Check if Ollama is installed but not running
    if sys.platform == "win32":
        result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, "Ollama is installed but not running"
    else:
        result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, "Ollama is installed but not running"
    
    return False, "Ollama is not installed"

def install_ollama():
    """
    Install Ollama based on the platform
    """
    if sys.platform == "win32":
        print("Please install Ollama manually from https://ollama.ai/download")
        print("After installation, run: ollama pull llama2")
    else:
        try:
            # Install Ollama
            subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], check=True)
            print("Ollama installed successfully")
            
            # Start Ollama
            subprocess.Popen(["ollama", "serve"])
            time.sleep(5)  # Wait for Ollama to start
            
            # Pull the model
            subprocess.run(["ollama", "pull", "llama2"], check=True)
            print("Llama2 model pulled successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"Error installing Ollama: {str(e)}")
            sys.exit(1)

def main():
    """
    Main function to check and set up Ollama
    """
    print("Checking Ollama installation...")
    installed, status = check_ollama()
    
    if not installed:
        print("Ollama is not installed. Installing now...")
        install_ollama()
    else:
        print(status)
        
        if "not running" in status.lower():
            print("Starting Ollama...")
            if sys.platform == "win32":
                print("Please start Ollama manually")
            else:
                subprocess.Popen(["ollama", "serve"])
                time.sleep(5)
    
    # Final check
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("Ollama is now running and ready to use")
        else:
            print("Ollama is installed but there might be issues. Please check manually")
    except requests.exceptions.ConnectionError:
        print("Could not connect to Ollama. Please start it manually")

if __name__ == "__main__":
    main()
