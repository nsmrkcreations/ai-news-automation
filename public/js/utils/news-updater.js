export class NewsUpdater {
    constructor() {
        // Initialize properties
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectDelay = 30000; // 30 seconds
        this.connectionPromise = null;
        this.preferences = this.getUserPreferences();
        this.connectionStatus = 'disconnected';
        this.eventHandlers = new Map();

        // Start connection
        this.initialize();
    }

    async initialize() {
        try {
            await this.connect();
            this.setupEventListeners();
        } catch (error) {
            console.error('Initial connection failed:', error);
            this.scheduleReconnect();
        }
    }

    async connect() {
        try {
            if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
                console.log('Connection already in progress');
                return;
            }

            // Get current preferences
            const prefs = this.preferences;
            
            // Build WebSocket URL with preferences
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsHost = process.env.NEWS_WS_HOST || window.location.hostname;
            const wsPort = process.env.NEWS_WS_PORT || '8080';
            const wsUrl = new URL(`${wsProtocol}//${wsHost}:${wsPort}/news-updates`);
            
            // Add user preferences as query parameters
            wsUrl.searchParams.set('categories', prefs.categories.join(','));
            wsUrl.searchParams.set('breaking', prefs.breakingNews);
            wsUrl.searchParams.set('minScore', prefs.minScore);
            wsUrl.searchParams.set('frequency', prefs.updateFrequency);

            // Create new WebSocket connection
            this.ws = new WebSocket(wsUrl.toString());
            
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
                    this.reconnectAttempts = 0; // Reset reconnect counter on successful connection
                    this.connectionStatus = 'connected';
                    this.emit('connectionChange', { status: 'connected' });
                    console.log('WebSocket connected successfully');
                    resolve();
                };
                
                this.ws.onerror = (error) => {
                    clearTimeout(connectionTimeout);
                    this.connectionStatus = 'error';
                    this.emit('connectionChange', { status: 'error', error });
                    console.error('WebSocket connection error:', error);
                    reject(error);
                };
            });
        } catch (error) {
            this.connectionStatus = 'error';
            this.emit('connectionChange', { status: 'error', error });
            throw error;
        }
    }

    setupEventListeners() {
        if (!this.ws) return;

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                switch (data.type) {
                    case 'initial':
                        this.emit('initialData', data.articles);
                        break;
                    case 'breaking':
                        this.handleBreakingNews(data.articles);
                        break;
                    case 'update':
                        this.handleNewsUpdate(data.articles);
                        break;
                    default:
                        console.warn('Unknown message type:', data.type);
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        };

        this.ws.onclose = () => {
            this.connectionStatus = 'disconnected';
            this.emit('connectionChange', { status: 'disconnected' });
            this.scheduleReconnect();
        };
    }

    scheduleReconnect() {
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxReconnectDelay);
        this.reconnectAttempts++;
        console.log(`Scheduling reconnect in ${delay}ms`);
        setTimeout(() => this.connect().catch(console.error), delay);
    }

    handleNewsUpdate(articles) {
        if (!articles || articles.length === 0) return;
        this.emit('update', articles);
    }

    handleBreakingNews(articles) {
        if (!articles || articles.length === 0) return;
        this.emit('breaking', articles);
        
        if (this.preferences.notificationSound) {
            this.playNotificationSound();
        }
    }

    // Event handling
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, new Set());
        }
        this.eventHandlers.get(event).add(handler);
    }

    off(event, handler) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.delete(handler);
        }
    }

    emit(event, data) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in ${event} handler:`, error);
                }
            });
        }
    }

    // Preferences management
    getUserPreferences() {
        const defaults = {
            categories: ['all'],
            breakingNews: true,
            minScore: 0,
            updateFrequency: 'standard',
            notificationSound: true
        };
        
        try {
            const stored = localStorage.getItem('newsPreferences');
            return stored ? { ...defaults, ...JSON.parse(stored) } : defaults;
        } catch (e) {
            return defaults;
        }
    }

    updatePreferences(newPrefs) {
        this.preferences = { ...this.preferences, ...newPrefs };
        localStorage.setItem('newsPreferences', JSON.stringify(this.preferences));
        
        // Reconnect with new preferences if connected
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close();
            this.connect().catch(console.error);
        }
    }

    playNotificationSound() {
        const audio = new Audio('/sounds/notification.mp3');
        audio.volume = 0.5;
        audio.play().catch(() => {}); // Ignore autoplay restrictions
    }

    // Cleanup
    destroy() {
        if (this.ws) {
            this.ws.close();
        }
        this.eventHandlers.clear();
    }
}
