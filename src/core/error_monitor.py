"""
Error monitoring and alerting system
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict
import json

class ErrorMonitor:
    def __init__(self):
        self.error_log_path = "logs/errors.json"
        self.alert_threshold = 5  # Number of errors before alerting
        self.time_window = timedelta(minutes=30)  # Time window for error counting
        self.errors = self._load_errors()
        
        # Email configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.alert_email = os.getenv('ALERT_EMAIL')
        
    def _load_errors(self) -> List[Dict]:
        """Load existing errors from file"""
        try:
            if os.path.exists(self.error_log_path):
                with open(self.error_log_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading error log: {str(e)}")
        return []
        
    def _save_errors(self):
        """Save errors to file"""
        try:
            os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)
            with open(self.error_log_path, 'w') as f:
                json.dump(self.errors, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving error log: {str(e)}")
            
    def _clean_old_errors(self):
        """Remove errors outside the time window"""
        cutoff_time = datetime.now() - self.time_window
        self.errors = [
            error for error in self.errors
            if datetime.fromisoformat(error['timestamp']) > cutoff_time
        ]
        
    def log_error(self, error_type: str, message: str, context: Dict = None):
        """
        Log an error and send alert if threshold is reached
        """
        self._clean_old_errors()
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'context': context or {}
        }
        
        self.errors.append(error_entry)
        self._save_errors()
        
        # Check if we need to send an alert
        if len(self.errors) >= self.alert_threshold:
            self._send_alert()
            
    def _send_alert(self):
        """
        Send alert email about errors
        """
        if not all([self.smtp_user, self.smtp_pass, self.alert_email]):
            logging.error("Email configuration missing. Cannot send alert.")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = f"AI News Automation Alert - {len(self.errors)} errors in last {self.time_window.minutes} minutes"
            
            # Create email body
            body = "Recent errors:\n\n"
            for error in self.errors[-10:]:  # Show last 10 errors
                body += f"Time: {error['timestamp']}\n"
                body += f"Type: {error['type']}\n"
                body += f"Message: {error['message']}\n"
                if error['context']:
                    body += f"Context: {json.dumps(error['context'], indent=2)}\n"
                body += "\n---\n\n"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
                
            logging.info("Alert email sent successfully")
            
        except Exception as e:
            logging.error(f"Error sending alert email: {str(e)}")
            
    def get_error_summary(self) -> Dict:
        """
        Get summary of recent errors
        """
        self._clean_old_errors()
        
        error_types = {}
        for error in self.errors:
            error_type = error['type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        return {
            'total_errors': len(self.errors),
            'unique_error_types': len(error_types),
            'error_distribution': error_types,
            'time_window_minutes': self.time_window.minutes
        }
