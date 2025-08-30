"""
Script to install dependencies and run tests
"""
import subprocess
import sys
import os

def install_dependencies():
    """Install required packages"""
    packages = [
        'requests==2.31.0',
        'python-dotenv==1.0.0',
        'schedule==1.2.0',
        'fastapi==0.104.1',
        'uvicorn==0.24.0',
        'python-multipart==0.0.6',
        'pytest==7.4.2',
        'pytest-cov==4.1.0',
        'flake8==6.1.0',
        'mypy==1.5.1',
        'python-dateutil==2.8.2'
    ]
    
    if sys.platform == 'win32':
        packages.append('pywin32==306')
    
    print("Installing dependencies...")
    for package in packages:
        subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)

def run_tests():
    """Run the test suite"""
    print("\nRunning tests...")
    subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_comprehensive.py', '-v'], check=True)

if __name__ == "__main__":
    try:
        install_dependencies()
        run_tests()
    except subprocess.CalledProcessError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)
