"""
Windows service script for running the news updater
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from update_news import update_all_news

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NewsUpdaterService(win32serviceutil.ServiceFramework):
    _svc_name_ = "NewsUpdaterService"
    _svc_display_name_ = "News Updater Service"
    _svc_description_ = "Service to periodically update news from various sources"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        """Run the service"""
        try:
            # Change to the script directory and load environment variables
            root_dir = Path(__file__).parent.parent.absolute()
            os.chdir(root_dir)
            load_dotenv(os.path.join(root_dir, '.env'))
            
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(root_dir, 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            logger.info("Starting News Updater Service")
            logger.info(f"Working directory: {os.getcwd()}")
            
            # Initial update
            try:
                update_all_news()
                logger.info("Initial news update completed successfully")
            except Exception as e:
                logger.error(f"Initial news update failed: {str(e)}")
            
            # Update interval in minutes
            update_interval = int(os.getenv('NEWS_UPDATE_INTERVAL', 30))
            logger.info(f"Update interval set to {update_interval} minutes")
            last_update = time.time()
            
            while self.running:
                try:
                    # Check if it's time for an update
                    if time.time() - last_update >= update_interval * 60:
                        logger.info("Starting scheduled news update")
                        update_all_news()
                        last_update = time.time()
                        logger.info("Scheduled news update completed")
                    
                    # Sleep for a minute
                    time.sleep(60)
                    
                except Exception as e:
                    logger.error(f"Error during news update: {str(e)}")
                    # Wait for 5 minutes before retrying after an error
                    time.sleep(300)
                
        except Exception as e:
            error_msg = f"Critical service error: {str(e)}"
            logger.error(error_msg)
            servicemanager.LogErrorMsg(error_msg)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NewsUpdaterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NewsUpdaterService)
