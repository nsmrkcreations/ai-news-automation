// NewsUpdater.js - Simple polling mechanism for news updates
export class NewsUpdater {
    constructor(options = {}) {
        // Event handling
        this.eventHandlers = {};
        
        // State management
        this.lastArticles = [];
        this.connected = false;
        this.connectionStatus = 'disconnected';
        
        // Polling configuration
        this.pollingInterval = null;
        this.baseInterval = options.interval || 5 * 60 * 1000; // Default: 5 minutes
        this.checkInterval = this.baseInterval;
        this.maxInterval = options.maxInterval || 30 * 60 * 1000; // Max: 30 minutes
        
        // Error handling
        this.retryCount = 0;
        this.maxRetries = options.maxRetries || 3;
        this.requestTimeout = options.requestTimeout || 10000; // 10 second timeout
        
        // Start fetching news
        this.initialize();
    }

    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    emit(event, data) {
        const handlers = this.eventHandlers[event];
        if (handlers) {
            handlers.forEach(handler => handler(data));
        }
    }

    async initialize() {
        try {
            // Get initial news data
            const news = await this.fetchLatestNews();
            if (news && news.length > 0) {
                this.lastArticles = news;
                this.emit('initial', news);
                this.updateConnectionStatus(true);
                this.startPolling();
            }
        } catch (error) {
            console.error('Failed to initialize news updates:', error);
            this.updateConnectionStatus(false);
            this.retryInitialization();
        }
    }

    retryInitialization() {
        const backoffTime = Math.min(
            this.baseInterval * Math.pow(2, this.retryCount),
            this.maxInterval
        );
        this.retryCount++;
        
        if (this.retryCount <= this.maxRetries) {
            console.log(`Retrying initialization in ${backoffTime/1000} seconds...`);
            setTimeout(() => this.initialize(), backoffTime);
        } else {
            console.error('Max retries exceeded. Please check your connection.');
            this.emit('error', { 
                type: 'connection',
                message: 'Failed to connect after multiple attempts'
            });
        }
    }

    startPolling() {
        // Reset retry count on successful connection
        this.retryCount = 0;
        
        // Clear any existing polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        // Start new polling interval
        this.pollingInterval = setInterval(async () => {
            try {
                const news = await this.fetchLatestNews();
                if (news && news.length > 0) {
                    // Check for new articles
                    const newArticles = news.filter(article => 
                        !this.lastArticles.some(existing => existing.url === article.url)
                    );

                    if (newArticles.length > 0) {
                        // Check for breaking news
                        const breakingNews = newArticles.filter(article => 
                            article.isBreaking || 
                            article.title.toLowerCase().includes('breaking') ||
                            article.title.toLowerCase().includes('urgent')
                        );

                        if (breakingNews.length > 0) {
                            this.emit('breaking', breakingNews);
                        } else {
                            this.emit('update', newArticles);
                        }

                        this.lastArticles = news;
                    }
                    
                    // Reset check interval on successful fetch
                    this.checkInterval = this.baseInterval;
                    this.updateConnectionStatus(true);
                }
            } catch (error) {
                console.error('Failed to fetch news updates:', error);
                this.updateConnectionStatus(false);
                this.emit('error', {
                    type: 'fetch',
                    message: 'Failed to fetch news updates'
                });
                
                // Increase check interval with exponential backoff
                this.checkInterval = Math.min(
                    this.checkInterval * 2,
                    this.maxInterval
                );
            }
        }, this.checkInterval);
    }

    async fetchLatestNews() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

            const response = await fetch('/data/news.json', {
                signal: controller.signal,
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            console.error('Error fetching news:', error);
            throw error;
        }
    }

    updateConnectionStatus(status) {
        const prevStatus = this.connected;
        this.connected = status;

        // Emit connection status change events
        if (prevStatus !== status) {
            // Update UI if status element exists
            const statusElement = document.querySelector('.connection-status');
            if (statusElement) {
                statusElement.className = `connection-status ${this.connectionStatus}`;
                statusElement.textContent = status ? 'Connected to news service' : 'Error connecting to news service';
                
                if (status) {
                    // Hide after 3 seconds if connected
                    setTimeout(() => {
                        statusElement.style.display = 'none';
                    }, 3000);
                } else {
                    statusElement.style.display = 'block';
                }
            }
        }
    }

    // Cleanup method
    destroy() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.eventHandlers = {};
    }
}
