// Contact form handling
document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contactForm');
    const submitButton = contactForm?.querySelector('button[type="submit"]');

    if (contactForm) {
        contactForm.addEventListener('submit', handleSubmit);
    }

    function handleSubmit(e) {
        e.preventDefault();

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        }

        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData.entries());

        // Validate form data
        if (!validateForm(data)) {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
            }
            return;
        }

        // Send the form data
        sendContactForm(data)
            .then(response => {
                showNotification('success', 'Thank you for your message! We\'ll get back to you soon.');
                contactForm.reset();
            })
            .catch(error => {
                showNotification('error', 'Sorry, there was a problem sending your message. Please try again later.');
            })
            .finally(() => {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send Message';
                }
            });
    }

    function validateForm(data) {
        const errors = [];

        if (!data.name?.trim()) {
            errors.push('Name is required');
        }

        if (!data.email?.trim()) {
            errors.push('Email is required');
        } else if (!isValidEmail(data.email)) {
            errors.push('Please enter a valid email address');
        }

        if (!data.subject) {
            errors.push('Please select a subject');
        }

        if (!data.message?.trim()) {
            errors.push('Message is required');
        }

        if (errors.length > 0) {
            showNotification('error', errors.join('<br>'));
            return false;
        }

        return true;
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    async function sendContactForm(data) {
        // In a real application, this would send the data to a server
        // For now, we'll simulate a successful submission
        return new Promise((resolve) => {
            setTimeout(resolve, 1500);
        });
    }

    function showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
                <p>${message}</p>
            </div>
            <button class="close-notification" aria-label="Close notification">
                <i class="fas fa-times"></i>
            </button>
        `;

        document.body.appendChild(notification);

        // Add close button functionality
        const closeButton = notification.querySelector('.close-notification');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                notification.remove();
            });
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
});
