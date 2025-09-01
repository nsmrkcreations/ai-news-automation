@echo off
cd /d %~dp0
echo Starting AI News Automation...
python setup_automation.py >> logs\automation_%date:~10,4%%date:~4,2%%date:~7,2%.log 2>&1
