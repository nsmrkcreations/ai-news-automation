# Contact Form Setup Guide

The contact form on your NewSurgeAI website is now functional! Here's how to set it up and use it.

## Quick Start

1. **Start the contact server:**
   ```bash
   # On Windows
   start_contact_server.bat
   
   # Or manually
   python contact_server.py
   ```

2. **Open your website:**
   - Go to `http://localhost:5000` in your browser
   - Navigate to the Contact section
   - Fill out and submit the form

## Email Configuration (Optional but Recommended)

To receive actual emails instead of just logs, set up Gmail app password:

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to your Google Account settings
2. Enable 2-Factor Authentication if not already enabled

### Step 2: Create App Password
1. Go to Google Account > Security > App passwords
2. Generate a new app password for "Mail"
3. Copy the 16-character password

### Step 3: Update Environment Variables
1. Copy `.env.example` to `.env`
2. Update these values in `.env`:
   ```
   EMAIL_USER=nsmrkCreations@gmail.com
   EMAIL_PASSWORD=your_16_character_app_password_here
   RECIPIENT_EMAIL=nsmrkCreations@gmail.com
   ```

## How It Works

1. **User fills out the contact form** with:
   - Full Name
   - Email Address
   - Subject (dropdown)
   - Message

2. **Form validation** ensures all fields are filled correctly

3. **Email sending** happens via:
   - Primary: Python Flask server with SMTP
   - Fallback: Opens user's email client with pre-filled message

4. **User feedback** shows success/error messages

## Features

- ✅ Form validation
- ✅ Loading states
- ✅ Success/error notifications
- ✅ Email fallback if server fails
- ✅ Responsive design
- ✅ Dark mode support
- ✅ Spam protection (basic rate limiting)

## Testing

1. Start the server: `python contact_server.py`
2. Open `http://localhost:5000`
3. Go to Contact section
4. Fill out and submit the form
5. Check console logs or your email

## Troubleshooting

### Form shows "Not Found" error
- Make sure the contact server is running
- Check that you're accessing `http://localhost:5000` (not just opening the HTML file)

### Emails not being sent
- Check your `.env` file has correct email credentials
- Verify Gmail app password is correct
- Check server logs for error messages

### Form doesn't submit
- Check browser console for JavaScript errors
- Ensure all required fields are filled
- Try the mailto fallback option

## Production Deployment

For production, consider:
1. Using a proper web server (nginx, Apache)
2. Setting up SSL certificates
3. Using environment variables for sensitive data
4. Adding rate limiting and spam protection
5. Using a dedicated email service (SendGrid, Mailgun)

## Files Created/Modified

- `contact_server.py` - Flask server for handling form submissions
- `public/js/contact.js` - Client-side form handling
- `start_contact_server.bat` - Easy server startup
- `requirements.txt` - Added Flask dependencies
- `.env.example` - Added email configuration
- `public/index.html` - Added contact.js script

Your contact form is now ready to use! 🎉