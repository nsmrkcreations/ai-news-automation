@echo off
echo Starting AI News Automation Backend Service...
echo.
echo This will:
echo - Fetch fresh news every 30 minutes
echo - Update public/data/news.json automatically
echo - Keep your website content fresh
echo.
echo Press Ctrl+C to stop the service
echo.

cd /d "%~dp0"
python run_backend.py
