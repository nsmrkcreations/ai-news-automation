// Breaking News Ticker Component
class BreakingNewsTicker {
    constructor() {
        this.tickerElement = document.querySelector(SELECTORS.BREAKING_TICKER);
        this.tickerText = document.querySelector(SELECTORS.TICKER_TEXT);
        this.breakingNews = [];
        this.currentIndex = 0;
        this.intervalId = null;
        this.isVisible = false;
    }

    /**
     * Initialize the breaking news ticker
     */
    init() {
        if (!this.tickerElement || !this.tickerText) {
            console.warn('Breaking news ticker elements not found');
            return;
        }

        // Hide ticker initially
        this.hide();
        
        // Set up auto-rotation
        this.startRotation();
    }

    /**
     * Update breaking news content
     * @param {Array} articles - Array of breaking news articles
     */
    updateBreakingNews(articles) {
        // Filter for breaking news only
        this.breakingNews = articles.filter(article => article.isBreaking);
        
        if (this.breakingNews.length > 0) {
            this.currentIndex = 0;
            this.displayCurrentNews();
            this.show();
            this.restartRotation();
        } else {
            this.hide();
        }
    }

    /**
     * Display current breaking news item
     */
    displayCurrentNews() {
        if (this.breakingNews.length === 0 || !this.tickerText) return;
        
        const currentNews = this.breakingNews[this.currentIndex];
        const newsText = `${currentNews.title} - ${currentNews.source}`;
        
        // Animate text change
        this.tickerText.style.opacity = '0';
        
        setTimeout(() => {
            this.tickerText.textContent = newsText;
            this.tickerText.style.opacity = '1';
        }, 200);
    }

    /**
     * Move to next breaking news item
     */
    nextNews() {
        if (this.breakingNews.length === 0) return;
        
        this.currentIndex = (this.currentIndex + 1) % this.breakingNews.length;
        this.displayCurrentNews();
    }

    /**
     * Start automatic rotation of breaking news
     */
    startRotation() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        
        this.intervalId = setInterval(() => {
            if (this.breakingNews.length > 1) {
                this.nextNews();
            }
        }, 5000); // Change every 5 seconds
    }

    /**
     * Restart rotation (useful when content updates)
     */
    restartRotation() {
        this.startRotation();
    }

    /**
     * Stop automatic rotation
     */
    stopRotation() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Show breaking news ticker
     */
    show() {
        if (this.tickerElement && !this.isVisible) {
            this.tickerElement.classList.remove(CSS_CLASSES.HIDDEN);
            this.isVisible = true;
            
            // Animate in
            this.tickerElement.style.transform = 'translateY(-100%)';
            setTimeout(() => {
                this.tickerElement.style.transform = 'translateY(0)';
            }, 100);
        }
    }

    /**
     * Hide breaking news ticker
     */
    hide() {
        if (this.tickerElement && this.isVisible) {
            this.tickerElement.style.transform = 'translateY(-100%)';
            
            setTimeout(() => {
                this.tickerElement.classList.add(CSS_CLASSES.HIDDEN);
                this.isVisible = false;
            }, 300);
        }
    }

    /**
     * Add click handler to ticker for navigation
     */
    addClickHandler() {
        if (this.tickerElement) {
            this.tickerElement.addEventListener('click', () => {
                if (this.breakingNews.length > 0) {
                    const currentNews = this.breakingNews[this.currentIndex];
                    if (currentNews.url) {
                        // Track click
                        this.trackEvent('breaking_news_click', {
                            title: currentNews.title,
                            source: currentNews.source
                        });
                        
                        window.open(currentNews.url, '_blank', 'noopener,noreferrer');
                    }
                }
            });
            
            this.tickerElement.style.cursor = 'pointer';
        }
    }

    /**
     * Track analytics event
     * @param {string} eventName - Event name
     * @param {Object} eventData - Event data
     */
    trackEvent(eventName, eventData) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, eventData);
        }
        
        console.log('Event tracked:', eventName, eventData);
    }

    /**
     * Destroy ticker and clean up
     */
    destroy() {
        this.stopRotation();
        this.hide();
        this.breakingNews = [];
    }
}
