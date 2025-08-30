// Main Application Controller
class NewsApp {
    constructor() {
        this.articles = [];
        this.filteredArticles = [];
        this.currentCategory = APP_CONFIG.CATEGORIES.ALL;
        this.displayedCount = 0;
        this.isLoading = false;
        
        // Initialize components
        this.breakingNewsTicker = new BreakingNewsTicker();
        this.heroSection = new HeroSection();
        
        // DOM elements
        this.newsGrid = document.querySelector(SELECTORS.NEWS_GRID);
        this.loadMoreBtn = document.querySelector(SELECTORS.LOAD_MORE_BTN);
        this.filterButtons = document.querySelectorAll(SELECTORS.FILTER_BUTTONS);
        this.navLinks = document.querySelectorAll(SELECTORS.NAV_LINKS);
        this.mobileMenuToggle = document.querySelector(SELECTORS.MOBILE_MENU_TOGGLE);
        this.nav = document.querySelector(SELECTORS.NAV);
        this.header = document.querySelector(SELECTORS.HEADER);
        
        // Bind methods
        this.handleScroll = throttle(this.handleScroll.bind(this), 100);
        this.handleResize = debounce(this.handleResize.bind(this), 250);
        this.loadNews = this.loadNews.bind(this);
        this.retryLoad = this.retryLoad.bind(this);
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            this.setupEventListeners();
            this.setupUI();
            this.initializeComponents();
            
            // Load initial news data
            await this.loadNews();
            
            // Set up periodic refresh
            this.setupPeriodicRefresh();
            
            console.log('NewsApp initialized successfully');
        } catch (error) {
            console.error('Failed to initialize NewsApp:', error);
            this.showError(ERROR_MESSAGES.GENERIC_ERROR);
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Scroll events
        window.addEventListener(EVENTS.SCROLL, this.handleScroll);
        window.addEventListener(EVENTS.RESIZE, this.handleResize);
        
        // Network status
        NetworkStatus.onStatusChange(this.handleNetworkChange.bind(this));
        
        // Filter buttons
        this.filterButtons.forEach(btn => {
            btn.addEventListener(EVENTS.CLICK, (e) => {
                const category = e.target.dataset.category;
                this.filterByCategory(category);
            });
        });
        
        // Navigation links
        this.navLinks.forEach(link => {
            link.addEventListener(EVENTS.CLICK, (e) => {
                e.preventDefault();
                const category = e.target.dataset.category;
                this.filterByCategory(category);
                this.updateActiveNavLink(e.target);
                
                // Close mobile menu if open
                if (isMobile()) {
                    this.closeMobileMenu();
                }
            });
        });
        
        // Load more button
        if (this.loadMoreBtn) {
            this.loadMoreBtn.addEventListener(EVENTS.CLICK, () => {
                this.loadMoreArticles();
            });
        }
        
        // Mobile menu toggle
        if (this.mobileMenuToggle) {
            this.mobileMenuToggle.addEventListener(EVENTS.CLICK, () => {
                this.toggleMobileMenu();
            });
        }
        
        // Retry button
        const retryBtn = document.querySelector(SELECTORS.RETRY_BTN);
        if (retryBtn) {
            retryBtn.addEventListener(EVENTS.CLICK, this.retryLoad);
        }
        
        // Newsletter form
        const newsletterForm = document.querySelector(SELECTORS.NEWSLETTER_FORM);
        if (newsletterForm) {
            newsletterForm.addEventListener(EVENTS.SUBMIT, this.handleNewsletterSubmit.bind(this));
        }
    }

    /**
     * Set up UI components
     */
    setupUI() {
        // Set current date
        const dateElement = document.querySelector(SELECTORS.CURRENT_DATE);
        if (dateElement) {
            dateElement.textContent = getCurrentDate();
        }
        
        // Initialize mobile menu state
        this.closeMobileMenu();
    }

    /**
     * Initialize components
     */
    initializeComponents() {
        this.breakingNewsTicker.init();
        this.breakingNewsTicker.addClickHandler();
        this.heroSection.init();
    }

    /**
     * Load news data from API
     */
    async loadNews() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        showLoading();
        hideError();
        
        try {
            // Try to load from cache first
            const cachedData = this.loadFromCache();
            if (cachedData) {
                this.articles = cachedData;
                this.processArticles();
                hideLoading();
                this.isLoading = false;
                return;
            }
            
            // Fetch from API
            const response = await fetch(APP_CONFIG.API_ENDPOINTS.NEWS_DATA, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const articles = await response.json();
            
            if (!Array.isArray(articles)) {
                throw new Error('Invalid data format received');
            }
            
            this.articles = articles;
            this.saveToCache(articles);
            this.processArticles();
            
            console.log(`Loaded ${articles.length} articles`);
            
        } catch (error) {
            console.error('Failed to load news:', error);
            
            // Try to load from cache as fallback
            const cachedData = this.loadFromCache();
            if (cachedData) {
                this.articles = cachedData;
                this.processArticles();
                showSuccess('Showing cached articles (offline mode)');
            } else {
                this.showError(ERROR_MESSAGES.DATA_LOAD_ERROR);
            }
        } finally {
            hideLoading();
            this.isLoading = false;
        }
    }

    /**
     * Process loaded articles
     */
    processArticles() {
        if (this.articles.length === 0) {
            this.showError(ERROR_MESSAGES.NO_ARTICLES);
            return;
        }
        
        // Sort articles by date (newest first)
        this.articles.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
        
        // Update components
        this.updateBreakingNews();
        this.updateHeroSection();
        this.filterByCategory(this.currentCategory);
    }

    /**
     * Update breaking news ticker
     */
    updateBreakingNews() {
        this.breakingNewsTicker.updateBreakingNews(this.articles);
    }

    /**
     * Update hero section
     */
    updateHeroSection() {
        this.heroSection.updateContent(this.articles);
    }

    /**
     * Filter articles by category
     * @param {string} category - Category to filter by
     */
    filterByCategory(category) {
        this.currentCategory = category;
        
        // Filter articles
        if (category === APP_CONFIG.CATEGORIES.ALL) {
            this.filteredArticles = [...this.articles];
        } else {
            this.filteredArticles = this.articles.filter(article => 
                article.category === category
            );
        }
        
        // Update UI
        this.updateActiveFilterButton(category);
        this.displayArticles();
        
        // Track filter event
        this.trackEvent('category_filter', { category });
    }

    /**
     * Display articles in the grid
     */
    displayArticles() {
        if (!this.newsGrid) return;
        
        // Clear existing articles
        this.newsGrid.innerHTML = '';
        this.displayedCount = 0;
        
        if (this.filteredArticles.length === 0) {
            this.showNoArticlesMessage();
            return;
        }
        
        // Load initial batch
        this.loadMoreArticles();
    }

    /**
     * Load more articles (pagination)
     */
    loadMoreArticles() {
        if (!this.newsGrid || !this.loadMoreBtn) return;
        
        const startIndex = this.displayedCount;
        const endIndex = Math.min(
            startIndex + (startIndex === 0 ? APP_CONFIG.PAGINATION.INITIAL_LOAD : APP_CONFIG.PAGINATION.LOAD_MORE_COUNT),
            this.filteredArticles.length
        );
        
        const articlesToShow = this.filteredArticles.slice(startIndex, endIndex);
        
        // Create and append news cards
        articlesToShow.forEach((article, index) => {
            const newsCard = new NewsCard(article);
            const cardElement = newsCard.createElement();
            
            this.newsGrid.appendChild(cardElement);
            
            // Animate in with stagger
            setTimeout(() => {
                newsCard.animateIn();
            }, index * 100);
        });
        
        this.displayedCount = endIndex;
        
        // Update load more button
        if (this.displayedCount >= this.filteredArticles.length) {
            this.loadMoreBtn.style.display = 'none';
        } else {
            this.loadMoreBtn.style.display = 'block';
            this.loadMoreBtn.textContent = `Load More (${this.filteredArticles.length - this.displayedCount} remaining)`;
        }
    }

    /**
     * Show no articles message
     */
    showNoArticlesMessage() {
        if (!this.newsGrid) return;
        
        this.newsGrid.innerHTML = `
            <div class="no-articles-message">
                <h3>No articles found</h3>
                <p>No articles available for the selected category. Try selecting a different category or check back later.</p>
                <button class="btn btn-primary" onclick="newsApp.filterByCategory('${APP_CONFIG.CATEGORIES.ALL}')">
                    Show All Articles
                </button>
            </div>
        `;
        
        if (this.loadMoreBtn) {
            this.loadMoreBtn.style.display = 'none';
        }
    }

    /**
     * Update active filter button
     * @param {string} category - Active category
     */
    updateActiveFilterButton(category) {
        this.filterButtons.forEach(btn => {
            if (btn.dataset.category === category) {
                btn.classList.add(CSS_CLASSES.ACTIVE);
            } else {
                btn.classList.remove(CSS_CLASSES.ACTIVE);
            }
        });
    }

    /**
     * Update active navigation link
     * @param {HTMLElement} activeLink - Active navigation link
     */
    updateActiveNavLink(activeLink) {
        this.navLinks.forEach(link => {
            link.classList.remove(CSS_CLASSES.ACTIVE);
        });
        activeLink.classList.add(CSS_CLASSES.ACTIVE);
    }

    /**
     * Handle scroll events
     */
    handleScroll() {
        // Header scroll effect
        if (this.header) {
            if (window.scrollY > 100) {
                this.header.classList.add(CSS_CLASSES.SCROLLED);
            } else {
                this.header.classList.remove(CSS_CLASSES.SCROLLED);
            }
        }
        
        // Infinite scroll (optional)
        if (this.isNearBottom() && this.displayedCount < this.filteredArticles.length) {
            this.loadMoreArticles();
        }
    }

    /**
     * Check if user is near bottom of page
     * @returns {boolean} True if near bottom
     */
    isNearBottom() {
        return window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000;
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Close mobile menu on resize to desktop
        if (!isMobile() && this.nav) {
            this.closeMobileMenu();
        }
    }

    /**
     * Handle network status change
     * @param {boolean} isOnline - Network status
     */
    handleNetworkChange(isOnline) {
        const statusElement = document.querySelector(SELECTORS.CONNECTION_STATUS);
        if (statusElement) {
            if (isOnline) {
                statusElement.classList.add(CSS_CLASSES.HIDDEN);
                // Refresh data when back online
                setTimeout(() => this.loadNews(), 1000);
            } else {
                statusElement.classList.remove(CSS_CLASSES.HIDDEN);
            }
        }
    }

    /**
     * Toggle mobile menu
     */
    toggleMobileMenu() {
        if (this.nav && this.mobileMenuToggle) {
            this.nav.classList.toggle(CSS_CLASSES.ACTIVE);
            this.mobileMenuToggle.classList.toggle(CSS_CLASSES.ACTIVE);
        }
    }

    /**
     * Close mobile menu
     */
    closeMobileMenu() {
        if (this.nav && this.mobileMenuToggle) {
            this.nav.classList.remove(CSS_CLASSES.ACTIVE);
            this.mobileMenuToggle.classList.remove(CSS_CLASSES.ACTIVE);
        }
    }

    /**
     * Handle newsletter form submission
     * @param {Event} e - Form submit event
     */
    async handleNewsletterSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const emailInput = form.querySelector('input[type="email"]');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (!emailInput || !isValidEmail(emailInput.value)) {
            showError('Please enter a valid email address');
            return;
        }
        
        // Show loading state
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Subscribing...';
        submitBtn.disabled = true;
        
        try {
            // Simulate API call (replace with actual endpoint)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            showSuccess('Successfully subscribed to newsletter!');
            form.reset();
            
            // Track subscription
            this.trackEvent('newsletter_subscribe', {
                email: emailInput.value
            });
            
        } catch (error) {
            showError('Failed to subscribe. Please try again.');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Retry loading news
     */
    async retryLoad() {
        hideError();
        await this.loadNews();
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        showError(message);
    }

    /**
     * Set up periodic refresh of news data
     */
    setupPeriodicRefresh() {
        // Refresh every 5 minutes
        setInterval(() => {
            if (NetworkStatus.isOnline() && !this.isLoading) {
                this.loadNews();
            }
        }, 5 * 60 * 1000);
    }

    /**
     * Load articles from cache
     * @returns {Array|null} Cached articles or null
     */
    loadFromCache() {
        const cached = Storage.get(APP_CONFIG.CACHE.NEWS_KEY);
        if (cached && cached.timestamp) {
            const age = Date.now() - cached.timestamp;
            if (age < APP_CONFIG.CACHE.CACHE_DURATION) {
                return cached.data;
            }
        }
        return null;
    }

    /**
     * Save articles to cache
     * @param {Array} articles - Articles to cache
     */
    saveToCache(articles) {
        Storage.set(APP_CONFIG.CACHE.NEWS_KEY, {
            data: articles,
            timestamp: Date.now()
        });
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
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.newsApp = new NewsApp();
    newsApp.init();
});

// Handle page visibility change (refresh when tab becomes visible)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.newsApp && NetworkStatus.isOnline()) {
        // Refresh if data is older than 2 minutes
        const cached = Storage.get(APP_CONFIG.CACHE.NEWS_KEY);
        if (!cached || Date.now() - cached.timestamp > 2 * 60 * 1000) {
            window.newsApp.loadNews();
        }
    }
});