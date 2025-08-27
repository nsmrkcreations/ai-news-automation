// NewsUpdater.js
import { buildWSUrl, checkWSSupport } from '../config.js';

export class NewsUpdater {
    constructor() {
        // Initialize properties
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectDelay = 30000; // 30 seconds
        this.connectionPromise = null;
        this.connectionStatus = 'disconnected';
        this.eventHandlers = {};

        // Start connection
        this.initialize();
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
            await this.connect();
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
