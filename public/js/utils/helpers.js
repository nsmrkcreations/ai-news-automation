// Utility Helper Functions

/**
 * Format date to readable string
 * @param {string|Date} dateInput - Date string or Date object
 * @returns {string} Formatted date string
 */
function formatDate(dateInput) {
    try {
        const date = new Date(dateInput);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays} days ago`;
        } else {
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
    } catch (error) {
        return 'Unknown date';
    }
}

/**
 * Format time to relative string (e.g., "2 hours ago")
 * @param {string|Date} dateInput - Date string or Date object
 * @returns {string} Relative time string
 */
function formatRelativeTime(dateInput) {
    try {
        const date = new Date(dateInput);
        const now = new Date();
        const diffTime = now - date;
        const diffMinutes = Math.floor(diffTime / (1000 * 60));
        const diffHours = Math.floor(diffTime / (1000 * 60 * 60));
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffMinutes < 1) {
            return 'Just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes}m ago`;
        } else if (diffHours < 24) {
            return `${diffHours}h ago`;
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return formatDate(dateInput);
        }
    } catch (error) {
        return 'Unknown time';
    }
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength = 150) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
}

/**
 * Sanitize HTML content
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
function sanitizeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if device is mobile
 * @returns {boolean} True if mobile device
 */
function isMobile() {
    return window.innerWidth <= APP_CONFIG.BREAKPOINTS.MOBILE;
}

/**
 * Check if device is tablet
 * @returns {boolean} True if tablet device
 */
function isTablet() {
    return window.innerWidth > APP_CONFIG.BREAKPOINTS.MOBILE && 
           window.innerWidth <= APP_CONFIG.BREAKPOINTS.TABLET;
}

/**
 * Get current date formatted for display
 * @returns {string} Formatted current date
 */
function getCurrentDate() {
    const now = new Date();
    return now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Validate email address
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Show loading state
 * @param {HTMLElement} element - Element to show loading on
 */
function showLoading(element = null) {
    const loadingOverlay = document.querySelector(SELECTORS.LOADING_OVERLAY);
    if (loadingOverlay) {
        loadingOverlay.classList.remove(CSS_CLASSES.HIDDEN);
    }
    
    if (element) {
        element.classList.add(CSS_CLASSES.LOADING);
    }
}

/**
 * Hide loading state
 * @param {HTMLElement} element - Element to hide loading from
 */
function hideLoading(element = null) {
    const loadingOverlay = document.querySelector(SELECTORS.LOADING_OVERLAY);
    if (loadingOverlay) {
        loadingOverlay.classList.add(CSS_CLASSES.HIDDEN);
    }
    
    if (element) {
        element.classList.remove(CSS_CLASSES.LOADING);
    }
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message = ERROR_MESSAGES.GENERIC_ERROR) {
    const errorElement = document.querySelector(SELECTORS.ERROR_MESSAGE);
    const errorText = document.querySelector(SELECTORS.ERROR_TEXT);
    
    if (errorElement && errorText) {
        errorText.textContent = message;
        errorElement.classList.remove(CSS_CLASSES.HIDDEN);
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorElement = document.querySelector(SELECTORS.ERROR_MESSAGE);
    if (errorElement) {
        errorElement.classList.add(CSS_CLASSES.HIDDEN);
    }
}

/**
 * Show success notification
 * @param {string} message - Success message
 */
function showSuccess(message) {
    // Create temporary success notification
    const notification = document.createElement('div');
    notification.className = 'success-notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success-color);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Animate element into view
 * @param {HTMLElement} element - Element to animate
 * @param {string} animationClass - Animation class to add
 */
function animateIn(element, animationClass = CSS_CLASSES.FADE_IN_UP) {
    if (element) {
        element.classList.add(animationClass);
        setTimeout(() => element.classList.remove(animationClass), 600);
    }
}

/**
 * Smooth scroll to element
 * @param {HTMLElement|string} target - Element or selector to scroll to
 * @param {number} offset - Offset from top
 */
function scrollToElement(target, offset = 0) {
    const element = typeof target === 'string' ? document.querySelector(target) : target;
    if (element) {
        const elementPosition = element.offsetTop - offset;
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} Success status
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        return success;
    }
}

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Check if element is in viewport
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} True if in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Local storage helpers with error handling
 */
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
            return false;
        }
    },
    
    get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Failed to read from localStorage:', error);
            return null;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
            return false;
        }
    },
    
    clear() {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Failed to clear localStorage:', error);
            return false;
        }
    }
};

/**
 * Network status helpers
 */
const NetworkStatus = {
    isOnline() {
        return navigator.onLine;
    },
    
    onStatusChange(callback) {
        window.addEventListener('online', () => callback(true));
        window.addEventListener('offline', () => callback(false));
    }
};

/**
 * Image loading helper with fallback
 * @param {string} src - Image source URL
 * @param {string} fallback - Fallback image URL
 * @returns {Promise<string>} Resolved image URL
 */
function loadImageWithFallback(src, fallback = FALLBACK_IMAGES.NEWS_PLACEHOLDER) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(src);
        img.onerror = () => resolve(fallback);
        img.src = src;
    });
}
