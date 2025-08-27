document.addEventListener('DOMContentLoaded', () => {
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSubmission);
    }
});

/**
 * Handles the newsletter form submission
 * @param {Event} event - The form submission event
 */
async function handleNewsletterSubmission(event) {
    event.preventDefault();

    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;

    // Get form data
    const formData = {
        email: form.querySelector('#email').value.trim(),
        interests: Array.from(form.querySelectorAll('input[name="interests"]:checked'))
            .map(checkbox => checkbox.value),
        frequency: form.querySelector('input[name="frequency"]:checked').value,
        consent: form.querySelector('input[name="consent"]').checked
    };

    // Basic validation
    if (!validateNewsletterData(formData)) {
        showNotification('Please fill in all required fields correctly.', 'error');
        return;
    }

    try {
        // Disable submit button and show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subscribing...';

        // TODO: Replace with actual API endpoint
        const response = await fetch('/api/newsletter/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to subscribe to newsletter');
        }

        // Show success message and reset form
        form.reset();
        showNotification('Successfully subscribed to the newsletter!', 'success');

        // Show additional confirmation message
        showSubscriptionConfirmation(formData.email);

    } catch (error) {
        console.error('Newsletter subscription error:', error);
        showNotification('Failed to subscribe. Please try again later.', 'error');

    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

/**
 * Validates the newsletter form data
 * @param {Object} data - The form data to validate
 * @returns {boolean} - Whether the data is valid
 */
function validateNewsletterData(data) {
    const { email, interests, frequency, consent } = data;

    // Email validation
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return false;
    }

    // Must select at least one interest
    if (!interests || interests.length === 0) {
        return false;
    }

    // Must select a frequency
    if (!frequency) {
        return false;
    }

    // Must consent to privacy policy
    if (!consent) {
        return false;
    }

    return true;
}

/**
 * Shows a notification message to the user
 * @param {string} message - The message to display
 * @param {string} type - The type of notification ('success' or 'error')
 */
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    // Add notification to the page
    document.body.appendChild(notification);

    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.classList.add('notification-fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

/**
 * Shows a subscription confirmation message
 * @param {string} email - The subscriber's email address
 */
function showSubscriptionConfirmation(email) {
    const confirmationSection = document.createElement('section');
    confirmationSection.className = 'subscription-confirmation';
    confirmationSection.innerHTML = `
        <div class="confirmation-content">
            <i class="fas fa-envelope-open-text"></i>
            <h2>Check Your Inbox!</h2>
            <p>We've sent a confirmation email to:</p>
            <p class="subscriber-email">${email}</p>
            <p>Please click the confirmation link in the email to complete your subscription.</p>
            <div class="confirmation-tips">
                <p><strong>Can't find the email?</strong></p>
                <ul>
                    <li>Check your spam folder</li>
                    <li>Add newsletter@newssurgeai.com to your contacts</li>
                    <li>The email should arrive within 5 minutes</li>
                </ul>
            </div>
        </div>
    `;

    // Replace the form with the confirmation message
    const formSection = document.querySelector('.newsletter-form-section');
    formSection.innerHTML = '';
    formSection.appendChild(confirmationSection);
}

// Add event listeners for form interactions
document.addEventListener('DOMContentLoaded', () => {
    // Update submit button state based on form validity
    const form = document.getElementById('newsletterForm');
    if (form) {
        const submitButton = form.querySelector('button[type="submit"]');
        const requiredFields = form.querySelectorAll('input[required]');
        const checkboxes = form.querySelectorAll('input[name="interests"]');

        function updateSubmitButton() {
            const isValid = Array.from(requiredFields).every(field => field.value || field.checked) &&
                           Array.from(checkboxes).some(checkbox => checkbox.checked);
            submitButton.disabled = !isValid;
        }

        requiredFields.forEach(field => {
            field.addEventListener('input', updateSubmitButton);
            field.addEventListener('change', updateSubmitButton);
        });

        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSubmitButton);
        });

        // Initial button state
        updateSubmitButton();
    }
});
