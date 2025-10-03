#!/usr/bin/env python3
"""
Simple contact form server for NewSurgeAI
Handles contact form submissions and sends emails
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER', 'nsmrkCreations@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # App password for Gmail
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'nsmrkCreations@gmail.com')

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files"""
    return send_from_directory('public', path)

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submissions"""
    try:
        # Get form data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Send email
        success = send_contact_email(data)
        
        if success:
            logger.info(f"Contact form submitted by {data['name']} ({data['email']})")
            return jsonify({'message': 'Message sent successfully!'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        logger.error(f"Error handling contact form: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def send_contact_email(data):
    """Send contact form email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"NewSurgeAI Contact: {data['subject']}"
        
        # Email body
        body = f"""
New contact form submission from NewSurgeAI website:

Name: {data['name']}
Email: {data['email']}
Subject: {data['subject']}

Message:
{data['message']}

---
Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
IP Address: {request.remote_addr}
User Agent: {request.headers.get('User-Agent', 'Unknown')}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        if EMAIL_PASSWORD:
            # Use SMTP with authentication
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        else:
            # Log the email instead of sending (for development)
            logger.info(f"Email would be sent:\n{body}")
            return True
            
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Check if we have email configuration
    if not EMAIL_PASSWORD:
        logger.warning("EMAIL_PASSWORD not set. Emails will be logged instead of sent.")
        logger.info("To enable email sending, set EMAIL_PASSWORD in .env file")
    
    # Run the server
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting contact server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)