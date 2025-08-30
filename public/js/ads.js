/**
 * AdSense Auto Ads Integration Module
 * Handles AdSense Auto Ads without requiring specific ad slots
 */

class AdManager {
    constructor() {
        this.autoAdsEnabled = false;
    }

    /**
     * Initialize AdSense Auto Ads
     */
    init() {
        if (!window.APP_CONFIG || !window.APP_CONFIG.ADSENSE_PUBLISHER_ID) {
            console.warn('AdSense: No publisher ID configured');
            return;
        }

        if (window.APP_CONFIG.ADSENSE_AUTO_ADS) {
            this.enableAutoAds();
        }
    }

    /**
     * Enable AdSense Auto Ads
     */
    enableAutoAds() {
        if (this.autoAdsEnabled) {
            return;
        }

        try {
            // Auto ads are enabled in the main HTML script
            // This just tracks the status
            this.autoAdsEnabled = true;
            console.log('AdSense: Auto Ads enabled for publisher', window.APP_CONFIG.ADSENSE_PUBLISHER_ID);
            
            // Track auto ads initialization
            this.trackAdPerformance('auto_ads', 'initialized');
            
        } catch (error) {
            console.error('AdSense: Failed to enable auto ads', error);
        }
    }

    /**
     * Track ad performance
     */
    trackAdPerformance(adType, action) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'ad_interaction', {
                ad_type: adType,
                action: action,
                publisher_id: window.APP_CONFIG?.ADSENSE_PUBLISHER_ID || 'unknown',
                timestamp: Date.now()
            });
        }
        
        console.log('AdSense Event:', adType, action);
    }

    /**
     * Check if auto ads are working
     */
    checkAutoAdsStatus() {
        return {
            enabled: this.autoAdsEnabled,
            publisherId: window.APP_CONFIG?.ADSENSE_PUBLISHER_ID,
            scriptLoaded: typeof adsbygoogle !== 'undefined'
        };
    }
}

// Initialize ad manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adManager = new AdManager();
    
    // Wait for AdSense script and config to load
    const checkAdSense = setInterval(() => {
        if (typeof adsbygoogle !== 'undefined' && window.APP_CONFIG) {
            clearInterval(checkAdSense);
            window.adManager.init();
        }
    }, 100);
    
    // Timeout after 10 seconds
    setTimeout(() => {
        clearInterval(checkAdSense);
        const status = window.adManager?.checkAutoAdsStatus();
        if (!status?.enabled) {
            console.warn('AdSense: Auto Ads failed to initialize within timeout');
        }
    }, 10000);
});

// Export for global access
window.AdManager = AdManager;
