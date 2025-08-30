// Application Constants
const APP_CONFIG = {
    API_ENDPOINTS: {
        NEWS_DATA: '/data/news.json',
        NEWSLETTER_SUBSCRIBE: '/api/newsletter/subscribe'
    },
    
    CATEGORIES: {
        ALL: 'all',
        TECHNOLOGY: 'technology',
        BUSINESS: 'business',
        SCIENCE: 'science',
        WORLD: 'world',
        GENERAL: 'general'
    },
    
    PAGINATION: {
        INITIAL_LOAD: 12,
        LOAD_MORE_COUNT: 6
    },
    
    CACHE: {
        NEWS_KEY: 'newsurgeai_news_cache',
        CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
        BREAKING_NEWS_DURATION: 2 * 60 * 1000 // 2 minutes
    },
    
    ANIMATIONS: {
        FADE_DURATION: 300,
        SLIDE_DURATION: 400,
        TICKER_SPEED: 30000 // 30 seconds
    },
    
    BREAKPOINTS: {
        MOBILE: 768,
        TABLET: 1024,
        DESKTOP: 1200
    }
};

// DOM Element Selectors
const SELECTORS = {
    // Header
    HEADER: '.header',
    MOBILE_MENU_TOGGLE: '.mobile-menu-toggle',
    NAV: '.nav',
    NAV_LINKS: '.nav-link',
    CURRENT_DATE: '#current-date',
    
    // Breaking News
    BREAKING_TICKER: '#breaking-ticker',
    TICKER_TEXT: '#ticker-text',
    
    // Hero Section
    HERO_ARTICLE: '#hero-article',
    TRENDING_ARTICLES: '#trending-articles',
    
    // Filters
    FILTER_BUTTONS: '.filter-btn',
    
    // News Grid
    NEWS_GRID: '#news-grid',
    LOAD_MORE_BTN: '#load-more-btn',
    
    // UI States
    LOADING_OVERLAY: '#loading-overlay',
    ERROR_MESSAGE: '#error-message',
    ERROR_TEXT: '#error-text',
    RETRY_BTN: '#retry-btn',
    CONNECTION_STATUS: '#connection-status',
    
    // Forms
    NEWSLETTER_FORM: '#newsletter-form'
};

// CSS Classes
const CSS_CLASSES = {
    ACTIVE: 'active',
    HIDDEN: 'hidden',
    LOADING: 'loading',
    ERROR: 'error',
    SCROLLED: 'scrolled',
    FADE_IN_UP: 'fade-in-up',
    SLIDE_IN_RIGHT: 'slide-in-right',
    BREAKING_BADGE: 'breaking-badge',
    CATEGORY_TAG: 'category-tag'
};

// Event Types
const EVENTS = {
    CLICK: 'click',
    SCROLL: 'scroll',
    RESIZE: 'resize',
    LOAD: 'load',
    ERROR: 'error',
    ONLINE: 'online',
    OFFLINE: 'offline',
    SUBMIT: 'submit'
};

// Error Messages
const ERROR_MESSAGES = {
    NETWORK_ERROR: 'Unable to connect to the server. Please check your internet connection.',
    DATA_LOAD_ERROR: 'Failed to load news articles. Please try again later.',
    GENERIC_ERROR: 'Something went wrong. Please refresh the page and try again.',
    NO_ARTICLES: 'No articles found for the selected category.',
    NEWSLETTER_ERROR: 'Failed to subscribe to newsletter. Please try again.'
};

// Success Messages
const SUCCESS_MESSAGES = {
    NEWSLETTER_SUCCESS: 'Successfully subscribed to newsletter!',
    DATA_LOADED: 'News articles loaded successfully.',
    CACHE_UPDATED: 'News cache updated.'
};

// Category Display Names
const CATEGORY_NAMES = {
    [APP_CONFIG.CATEGORIES.ALL]: 'All News',
    [APP_CONFIG.CATEGORIES.TECHNOLOGY]: 'Technology',
    [APP_CONFIG.CATEGORIES.BUSINESS]: 'Business',
    [APP_CONFIG.CATEGORIES.SCIENCE]: 'Science',
    [APP_CONFIG.CATEGORIES.WORLD]: 'World',
    [APP_CONFIG.CATEGORIES.GENERAL]: 'General'
};

// Fallback Images
const FALLBACK_IMAGES = {
    NEWS_PLACEHOLDER: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDQwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjMUExQTJFIi8+CjxwYXRoIGQ9Ik0xNzUgNzVIMjI1VjEyNUgxNzVWNzVaIiBmaWxsPSIjRTk0NTYwIi8+CjxwYXRoIGQ9Ik0xOTAgOTBIMjEwVjExMEgxOTBWOTBaIiBmaWxsPSIjRkZGRkZGIi8+CjwvZXZnPg==',
    HERO_PLACEHOLDER: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjQwMCIgdmlld0JveD0iMCAwIDgwMCA0MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI4MDAiIGhlaWdodD0iNDAwIiBmaWxsPSIjMUExQTJFIi8+CjxwYXRoIGQ9Ik0zNTAgMTUwSDQ1MFYyNTBIMzUwVjE1MFoiIGZpbGw9IiNFOTQ1NjAiLz4KPHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4PSIzODAiIHk9IjE4MCI+CjxwYXRoIGQ9Ik0yMCAzNUMxMi4yNjggMzUgNiAyOC43MzIgNiAyMUM2IDEzLjI2OCAxMi4yNjggNyAyMCA3QzI3LjczMiA3IDM0IDEzLjI2OCAzNCAyMUMzNCAyOC43MzIgMjcuNzMyIDM1IDIwIDM1WiIgZmlsbD0iI0ZGRkZGRiIvPgo8L3N2Zz4KPC9zdmc+'
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        APP_CONFIG,
        SELECTORS,
        CSS_CLASSES,
        EVENTS,
        ERROR_MESSAGES,
        SUCCESS_MESSAGES,
        CATEGORY_NAMES,
        FALLBACK_IMAGES
    };
}
