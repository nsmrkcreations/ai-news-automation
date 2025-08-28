// Environment-specific configuration
const config = {
    development: {
        wsHost: 'localhost',
        wsPort: '5000',
        apiBase: 'http://localhost:5000'
    },
    production: {
        wsHost: window.location.hostname,  // Use same domain as the website
        wsPort: '443',                     // Default HTTPS port
        apiBase: window.location.origin    // Use same origin as the website
    }
};

// Determine environment based on hostname
const ENV = window.location.hostname === 'localhost' ? 'development' : 'production';

// Export configuration based on environment
export const currentConfig = config[ENV];

// WebSocket URL builder with fallback and security
export function buildWSUrl(path) {
    const isSecure = window.location.protocol === 'https:';
    const protocol = isSecure ? 'wss:' : 'ws:';
    const host = currentConfig.wsHost;
    const port = currentConfig.wsPort;
    
    // Don't include standard ports in URL
    const portString = (isSecure && port === '443') || (!isSecure && port === '80') 
        ? '' 
        : `:${port}`;
    
    return `${protocol}//${host}${portString}${path}`;
}

// Utility to check WebSocket support and security
export function checkWSSupport() {
    if (!window.WebSocket) {
        throw new Error('WebSocket not supported in this browser');
    }
    
    if (window.location.protocol === 'https:' && !window.isSecureContext) {
        throw new Error('Secure WebSocket connection requires secure context');
    }
    
    return true;
}
