// Link handling utilities
const linkHandler = {
    isExternalLink(url) {
        try {
            const currentHost = window.location.hostname;
            const urlHost = new URL(url, window.location.origin).hostname;
            return currentHost !== urlHost && urlHost !== '';
        } catch (e) {
            console.error('Error checking external link:', e);
            return false;
        }
    },

    validateUrl(url) {
        try {
            const parsedUrl = new URL(url, window.location.origin);
            // Only allow http and https protocols
            if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
                throw new Error('Invalid protocol');
            }
            return parsedUrl.toString();
        } catch (e) {
            console.error('Invalid URL:', e);
            return '#';
        }
    },

    handleExternalLink(event, url) {
        event.preventDefault();
        
        // Show warning for external links
        const proceed = confirm('You are about to leave NewsSurgeAI. Continue to external site?');
        
        if (proceed) {
            // Open in new tab with security attributes
            window.open(
                url,
                '_blank',
                'noopener,noreferrer'
            );
        }
    },

    trackLinkClick(url, category = 'navigation') {
        try {
            // If Google Analytics is available
            if (window.gtag) {
                gtag('event', 'click', {
                    'event_category': category,
                    'event_label': url,
                    'transport_type': 'beacon'
                });
            }
        } catch (e) {
            console.error('Error tracking link click:', e);
        }
    },

    // History API wrapper
    navigate(path, title = '') {
        try {
            const url = this.validateUrl(path);
            window.history.pushState({ path }, title, url);
            this.trackLinkClick(url);
            return true;
        } catch (e) {
            console.error('Navigation failed:', e);
            return false;
        }
    },

    setupLinkHandlers() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;

            const url = link.href;
            if (!url) return;

            // Track all link clicks
            this.trackLinkClick(url);

            // Handle external links
            if (this.isExternalLink(url)) {
                this.handleExternalLink(e, url);
            }
        });

        // Handle back/forward navigation
        window.addEventListener('popstate', (event) => {
            if (event.state?.path) {
                // Update the UI based on the new path
                updateUIForPath(event.state.path);
            }
        });
    }
};

function updateUIForPath(path) {
    // Remove active class from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Find and activate the correct nav link
    const activeLink = document.querySelector(`a[href="${path}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Update content based on path
    const category = path.replace('#', '') || 'all';
    if (typeof filterAndDisplayNews === 'function') {
        filterAndDisplayNews(category);
    }
}

export default linkHandler;
