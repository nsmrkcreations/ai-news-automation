@echo off
echo Setting up Windows Task Scheduler for AI News Automation
echo.

REM Create the task to run every 30 minutes
schtasks /create /tn "AI News Automation" /tr "python \"%~dp0setup_automation.py\"" /sc minute /mo 30 /st 09:00 /et 23:59 /ru SYSTEM

if %errorlevel% equ 0 (
    echo ✅ Task created successfully!
    echo.
    echo The service will:
    echo - Run every 30 minutes from 9 AM to 11:59 PM
    echo - Fetch fresh news and update your website
    echo - Automatically deploy to GitHub Pages
    echo.
    echo To manage the task:
    echo - View: schtasks /query /tn "AI News Automation"
    echo - Delete: schtasks /delete /tn "AI News Automation" /f
    echo.
) else (
    echo ❌ Failed to create task. Run as Administrator.
)

pause
