// NewsUpdater.js - Simple polling mechanism for news updates
export class NewsUpdater {
    constructor() {
        this.eventHandlers = {};
        this.lastUpdateTime = 0;
        this.lastArticles = [];
        this.pollingInterval = null;
        this.checkInterval = 5 * 60 * 1000; // Check every 5 minutes
        
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
                this.startPolling();
            }
        } catch (error) {
            console.error('Failed to initialize news updates:', error);
            // Retry after 1 minute
            setTimeout(() => this.initialize(), 60000);
        }
    }

    startPolling() {
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
                }
            } catch (error) {
                console.error('Failed to fetch news updates:', error);
            }
        }, this.checkInterval);
    }

    async fetchLatestNews() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching news:', error);
            throw error;
        }
    }
}
        }

        // Poll every 5 minutes
        this.pollingInterval = setInterval(() => {
            this.fetchLatestNews();
        }, 5 * 60 * 1000);
    }

    async fetchLatestNews() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) {
                throw new Error('Failed to fetch news');
            }

            const data = await response.json();
            
            // Check if we have new articles
            if (data.length > 0) {
                const latestTimestamp = new Date(data[0].publishedAt).getTime();
                
                if (latestTimestamp > this.lastUpdateTime) {
                    this.lastUpdateTime = latestTimestamp;
                    // Emit all articles on first load
                    if (this.lastUpdateTime === 0) {
                        this.emit('initial', data);
                    } else {
                        // Emit only new articles on subsequent loads
                        const newArticles = data.filter(article => 
                            new Date(article.publishedAt).getTime() > this.lastUpdateTime
                        );
                        if (newArticles.length > 0) {
                            this.emit('update', newArticles);
                        }
                    }
                }
            }

            this.updateConnectionStatus('connected');
        } catch (error) {
            console.error('Failed to fetch news:', error);
            this.updateConnectionStatus('error');
        }
    }

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        this.emit('connectionChange', status);
        
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            switch (status) {
                case 'connecting':
                    statusElement.textContent = 'Connecting to news service...';
                    break;
                case 'connected':
                    statusElement.textContent = 'Connected to news service';
                    // Hide after 3 seconds if connected
                    setTimeout(() => {
                        statusElement.style.display = 'none';
                    }, 3000);
                    break;
                case 'error':
                    statusElement.textContent = 'Error connecting to news service';
                    statusElement.style.display = 'block';
                    break;
            }
        }
    }

    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }

    async initialize() {
        try {
            // First try WebSocket connection
            await this.connect();
        } catch (error) {
            console.warn('WebSocket connection failed, falling back to HTTP polling:', error);
            // Fall back to HTTP polling
            this.startHttpPolling();
        }
    }

    async startHttpPolling() {
        // Initial load
        await this.fetchLatestNews();
        
        // Poll every 5 minutes
        setInterval(() => this.fetchLatestNews(), 5 * 60 * 1000);
    }

    async fetchLatestNews() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) {
                throw new Error('Failed to fetch news');
            }
            const data = await response.json();
            this.emit('initial', data);
            // Update connection status
            this.updateConnectionStatus('connected');
        } catch (error) {
            console.error('HTTP polling failed:', error);
            this.updateConnectionStatus('error');
        }
    }

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        this.emit('connectionChange', status);
        
        // Update UI
        const statusElement = document.querySelector('.connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            statusElement.textContent = status === 'connected' 
                ? 'Connected to news service' 
                : 'Error connecting to news service';
        }

    async connect() {
        try {
            if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
                console.log('Connection already in progress');
                return;
            }

            // Check WebSocket support and security
            if (!checkWSSupport()) {
                throw new Error('WebSocket not supported or secure context required');
            }

            // Build WebSocket URL
            const wsUrl = buildWSUrl('/news-updates');
            
            // Create new WebSocket connection
            this.ws = new WebSocket(wsUrl);
            
            // Set up connection timeout
            const connectionTimeout = setTimeout(() => {
                if (this.ws.readyState === WebSocket.CONNECTING) {
                    this.ws.close();
                    throw new Error('WebSocket connection timeout');
                }
            }, 5000);

            // Wait for connection to establish
            await new Promise((resolve, reject) => {
                this.ws.onopen = () => {
                    clearTimeout(connectionTimeout);
                    this.reconnectAttempts = 0;
                    this.connectionStatus = 'connected';
                    this.emit('connectionChange', { status: 'connected' });
                    resolve();
                };
                
                this.ws.onerror = (error) => {
                    clearTimeout(connectionTimeout);
                    this.connectionStatus = 'error';
                    this.emit('connectionChange', { status: 'error', error });
                    reject(error);
                };
            });

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.emit(data.type, data.articles);
            };

            this.ws.onclose = () => {
                this.connectionStatus = 'disconnected';
                this.emit('connectionChange', { status: 'disconnected' });
                this.scheduleReconnect();
            };

        } catch (error) {
            console.error('WebSocket connection error:', error);
            throw error;
        }
    }

    scheduleReconnect() {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxReconnectDelay);
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), delay);
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}
