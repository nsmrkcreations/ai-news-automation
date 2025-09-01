@echo off
set PYTHONPATH=%~dp0
cd /d %~dp0

echo [%date% %time%] Starting news update... >> news_update.log

:: Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Running with system Python. >> news_update.log
)

:: Run the update script
python src/update_news.py >> news_update.log 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] News update completed successfully. >> news_update.log
) else (
    echo [%date% %time%] News update failed with error code %ERRORLEVEL%. >> news_update.log
)

exit /b %ERRORLEVEL%
