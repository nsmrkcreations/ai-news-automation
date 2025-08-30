/**
 * Configuration file for sensitive IDs and API keys
 * This file should be generated server-side and not committed to version control
 */

// Configuration object that will be populated by server-side rendering or build process
window.APP_CONFIG = {
    // Google Analytics ID - populated from environment variable
    GA_MEASUREMENT_ID: '{{GA_MEASUREMENT_ID}}',
    
    // Google AdSense Publisher ID - populated from environment variable
    ADSENSE_PUBLISHER_ID: '{{ADSENSE_PUBLISHER_ID}}',
    
    // AdSense Configuration - using auto ads without specific slots
    ADSENSE_AUTO_ADS: true,
    
    // Other configuration
    SITE_NAME: 'NewSurgeAI',
    VERSION: '1.0.0'
};

// Fallback values for development (these should be replaced in production)
if (window.APP_CONFIG.GA_MEASUREMENT_ID === '{{GA_MEASUREMENT_ID}}') {
    console.warn('Using development configuration - replace with environment variables in production');
    window.APP_CONFIG = {
        ...window.APP_CONFIG,
        GA_MEASUREMENT_ID: 'G-DX7CWQ62HW',
        ADSENSE_PUBLISHER_ID: 'ca-pub-1318338562171737',
        ADSENSE_AUTO_ADS: true
    };
}
