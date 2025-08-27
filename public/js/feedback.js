document.addEventListener('DOMContentLoaded', () => {
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', handleFeedbackSubmission);
    }
});

/**
 * Handles the feedback form submission
 * @param {Event} event - The form submission event
 */
async function handleFeedbackSubmission(event) {
    event.preventDefault();

    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;

    // Get form data
    const formData = {
        feedbackType: form.querySelector('#feedbackType').value,
        title: form.querySelector('#title').value.trim(),
        description: form.querySelector('#description').value.trim(),
        url: form.querySelector('#url').value.trim(),
        email: form.querySelector('#email').value.trim()
    };

    // Basic validation
    if (!validateFeedbackData(formData)) {
        showNotification('Please fill in all required fields correctly.', 'error');
        return;
    }

    try {
        // Disable submit button and show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

        // TODO: Replace with actual API endpoint
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('Failed to submit feedback');
        }

        // Clear form and show success message
        form.reset();
        showNotification('Thank you for your feedback!', 'success');

    } catch (error) {
        console.error('Feedback submission error:', error);
        showNotification('Failed to submit feedback. Please try again later.', 'error');

    } finally {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

/**
 * Validates the feedback form data
 * @param {Object} data - The form data to validate
 * @returns {boolean} - Whether the data is valid
 */
function validateFeedbackData(data) {
    const { feedbackType, title, description, email } = data;

    // Check required fields
    if (!feedbackType || !title || !description) {
        return false;
    }

    // Title should be between 5 and 100 characters
    if (title.length < 5 || title.length > 100) {
        return false;
    }

    // Description should be at least 20 characters
    if (description.length < 20) {
        return false;
    }

    // Validate email if provided
    if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
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

// Add field validation and character counter for description
document.addEventListener('DOMContentLoaded', () => {
    const descriptionField = document.getElementById('description');
    if (descriptionField) {
        descriptionField.addEventListener('input', updateCharacterCount);
    }
});

/**
 * Updates the character count for the description field
 * @param {Event} event - The input event
 */
function updateCharacterCount(event) {
    const textarea = event.target;
    const charCount = textarea.value.length;
    const minChars = 20;
    
    let counterElement = textarea.nextElementSibling;
    if (!counterElement || !counterElement.classList.contains('char-counter')) {
        counterElement = document.createElement('div');
        counterElement.className = 'char-counter';
        textarea.parentNode.insertBefore(counterElement, textarea.nextSibling);
    }

    counterElement.innerHTML = `${charCount} characters (minimum ${minChars})`;
    counterElement.className = `char-counter ${charCount < minChars ? 'invalid' : 'valid'}`;
}
