/**
 * Configuration file for application settings and API endpoints
 */

// Main configuration object
window.APP_CONFIG = {
    // API Endpoints
    API_ENDPOINTS: {
        NEWS_DATA: '/data/news.json',
        NEWSLETTER_SUBSCRIBE: '/api/newsletter/subscribe'
    },
    
    // Google Analytics ID
    GA_MEASUREMENT_ID: 'G-DX7CWQ62HW',
    
    // Google AdSense Publisher ID
    ADSENSE_PUBLISHER_ID: 'ca-pub-1318338562171737',
    
    // AdSense Configuration
    ADSENSE_AUTO_ADS: true,
    
    // Application settings
    SITE_NAME: 'NewSurgeAI',
    VERSION: '1.0.0',
    
    // Error messages
    ERROR_MESSAGES: {
        DATA_LOAD_ERROR: 'Unable to load news articles. Please check your connection and try again.',
        NO_ARTICLES: 'No articles found. Please check back later.'
    }
};

// Log configuration status
console.log('Application configuration loaded:', window.APP_CONFIG);
