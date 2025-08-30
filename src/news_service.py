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
from pathlib import Path
from update_news import update_all_news

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
            # Change to the script directory
            os.chdir(Path(__file__).parent.parent)
            
            # Initial update
            update_all_news()
            
            # Update interval in minutes
            update_interval = int(os.getenv('NEWS_UPDATE_INTERVAL', 30))
            last_update = time.time()
            
            while self.running:
                # Check if it's time for an update
                if time.time() - last_update >= update_interval * 60:
                    update_all_news()
                    last_update = time.time()
                
                # Sleep for a minute
                time.sleep(60)
                
        except Exception as e:
            servicemanager.LogErrorMsg(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(NewsUpdaterService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(NewsUpdaterService)
