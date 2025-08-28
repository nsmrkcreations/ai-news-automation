#!/usr/bin/env python
import sys
import subprocess
import os

def check_dependencies():
    """Verify all required dependencies are installed"""
    print("Checking dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def run_tests():
    """Run all tests"""
    print("Running tests...")
    try:
        subprocess.run([sys.executable, '-m', 'pytest'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        return False

def verify_python_files():
    """Verify all Python files compile"""
    print("Verifying Python files...")
    success = True
    for root, _, files in os.walk('.'):
        # Skip third-party packages and cache directories
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        compile(f.read(), filepath, 'exec')
                except Exception as e:
                    print(f"❌ {filepath} failed to compile: {e}")
                    success = False
    return success

def verify_deployment():
    """Run deployment verification"""
    print("Verifying deployment...")
    try:
        subprocess.run([sys.executable, 'src/validate_deployment.py'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Deployment validation failed")
        return False

def main():
    """Run all verifications"""
    checks = [
        ("Dependencies", check_dependencies),
        ("Python Files", verify_python_files),
        ("Tests", run_tests),
        ("Deployment", verify_deployment)
    ]
    
    all_passed = True
    for name, check in checks:
        print(f"\n=== Checking {name} ===")
        try:
            if not check():
                all_passed = False
                print(f"❌ {name} check failed")
        except Exception as e:
            all_passed = False
            print(f"❌ {name} check failed with error: {e}")
    
    if not all_passed:
        sys.exit(1)
    
    print("\n✅ All checks passed! Safe to commit and push.")

if __name__ == "__main__":
    main()
