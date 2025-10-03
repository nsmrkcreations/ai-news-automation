/**
 * Contact Form Handler
 * Handles form submission and email sending
 */

class ContactFormHandler {
    constructor() {
        this.form = null;
        this.submitButton = null;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupForm());
        } else {
            this.setupForm();
        }
    }

    setupForm() {
        // Find the contact form
        this.form = document.querySelector('form[action="#"]');
        if (!this.form) {
            console.warn('Contact form not found');
            return;
        }

        this.submitButton = this.form.querySelector('button[type="submit"]');

        // Add event listener for form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(event) {
        event.preventDefault();

        // Get form data
        const formData = new FormData(this.form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            subject: formData.get('subject'),
            message: formData.get('message')
        };

        // Validate form data
        if (!this.validateForm(data)) {
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        try {
            // Send email using EmailJS
            await this.sendEmail(data);
            this.showSuccess();
            this.form.reset();
        } catch (error) {
            console.error('Error sending email:', error);
            this.showError('Failed to send message. Please try again or contact us directly at nsmrkCreations@gmail.com');
        } finally {
            this.setLoadingState(false);
        }
    }

    validateForm(data) {
        const errors = [];

        if (!data.name || data.name.trim().length < 2) {
            errors.push('Please enter your full name');
        }

        if (!data.email || !this.isValidEmail(data.email)) {
            errors.push('Please enter a valid email address');
        }

        if (!data.subject) {
            errors.push('Please select a subject');
        }

        if (!data.message || data.message.trim().length < 10) {
            errors.push('Please enter a message (at least 10 characters)');
        }

        if (errors.length > 0) {
            this.showError(errors.join('\n'));
            return false;
        }

        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    async sendEmail(data) {
        try {
            // Try to send via our API first
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                const result = await response.json();
                return result;
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to send message');
            }
        } catch (error) {
            console.warn('API failed, using mailto fallback:', error);

            // Fallback to mailto
            const subject = encodeURIComponent(`NewSurgeAI Contact: ${data.subject}`);
            const body = encodeURIComponent(
                `Name: ${data.name}\n` +
                `Email: ${data.email}\n` +
                `Subject: ${data.subject}\n\n` +
                `Message:\n${data.message}\n\n` +
                `---\n` +
                `Sent from NewSurgeAI Contact Form`
            );

            const mailtoLink = `mailto:nsmrkCreations@gmail.com?subject=${subject}&body=${body}`;

            // Open email client
            window.open(mailtoLink, '_blank');

            // Return success for user feedback
            return Promise.resolve({ message: 'Email client opened. Please send the email manually.' });
        }
    }

    setLoadingState(loading) {
        if (!this.submitButton) return;

        if (loading) {
            this.submitButton.disabled = true;
            this.submitButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
            `;
        } else {
            this.submitButton.disabled = false;
            this.submitButton.innerHTML = `
                <i class="material-icons mr-2 text-sm">send</i>
                Send Message
            `;
        }
    }

    showSuccess() {
        this.showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`;

        if (type === 'success') {
            notification.className += ' bg-green-500 text-white';
        } else if (type === 'error') {
            notification.className += ' bg-red-500 text-white';
        } else {
            notification.className += ' bg-blue-500 text-white';
        }

        notification.innerHTML = `
            <div class="flex items-start">
                <div class="flex-1">
                    <p class="text-sm font-medium">${message.replace(/\n/g, '<br>')}</p>
                </div>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i class="material-icons text-lg">close</i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }
}

// Initialize contact form handler
new ContactFormHandler();