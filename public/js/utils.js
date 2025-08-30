/**
 * Utility functions for the News Application
 */

// Throttle function to limit the rate at which a function can fire
const throttle = (func, limit) => {
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
};

// Debounce function to delay a function's execution
const debounce = (func, wait) => {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
};

// Format date to relative time (e.g., "2 hours ago")
const formatRelativeTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    let interval = Math.floor(seconds / 31536000);
    if (interval > 1) return `${interval} years ago`;
    if (interval === 1) return '1 year ago';
    
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) return `${interval} months ago`;
    if (interval === 1) return '1 month ago';
    
    interval = Math.floor(seconds / 86400);
    if (interval > 1) return `${interval} days ago`;
    if (interval === 1) return 'yesterday';
    
    interval = Math.floor(seconds / 3600);
    if (interval > 1) return `${interval} hours ago`;
    if (interval === 1) return '1 hour ago';
    
    interval = Math.floor(seconds / 60);
    if (interval > 1) return `${interval} minutes ago`;
    
    return 'just now';
};

// Truncate text to a certain length
const truncateText = (text, maxLength = 150) => {
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength)}...`;
};

// Check if device is mobile
const isMobile = () => {
    return window.innerWidth <= 768;
};

// Add loading state to button
const setButtonLoading = (button, isLoading) => {
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner"></span> Loading...';
    } else {
        button.disabled = false;
        button.textContent = button.getAttribute('data-original-text') || button.textContent;
    }
};

// Copy text to clipboard
const copyToClipboard = (text) => {
    return new Promise((resolve, reject) => {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(resolve).catch(reject);
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            document.body.appendChild(textarea);
            textarea.select();
            
            try {
                document.execCommand('copy');
                resolve();
            } catch (err) {
                reject(err);
            }
            
            document.body.removeChild(textarea);
        }
    });
};

// Generate a unique ID
const generateId = (prefix = '') => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

// Format number with commas
const formatNumber = (num) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

// Get URL parameters
const getUrlParameter = (name) => {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp(`[\\?&]${name}=([^&#]*)`);
    const results = regex.exec(window.location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

// Smooth scroll to element
const scrollToElement = (selector, offset = 0) => {
    const element = document.querySelector(selector);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        window.scrollTo({
            top: elementPosition - offset,
            behavior: 'smooth'
        });
    }
};

// Toggle element visibility
const toggleElement = (selector, show = true) => {
    const element = document.querySelector(selector);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
};

// Add class to element
const addClass = (selector, className) => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => el.classList.add(className));
};

// Remove class from element
const removeClass = (selector, className) => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => el.classList.remove(className));
};

// Toggle class on element
const toggleClass = (selector, className) => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => el.classList.toggle(className));
};

// Check if element is in viewport
const isInViewport = (element) => {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
};

// Load script dynamically
const loadScript = (url, callback) => {
    const script = document.createElement('script');
    script.src = url;
    script.async = true;
    script.onload = callback;
    document.body.appendChild(script);
};

// Load CSS dynamically
const loadCSS = (url) => {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
};

// Export all utility functions
export {
    throttle,
    debounce,
    formatRelativeTime,
    truncateText,
    isMobile,
    setButtonLoading,
    copyToClipboard,
    generateId,
    formatNumber,
    getUrlParameter,
    scrollToElement,
    toggleElement,
    addClass,
    removeClass,
    toggleClass,
    isInViewport,
    loadScript,
    loadCSS
};
