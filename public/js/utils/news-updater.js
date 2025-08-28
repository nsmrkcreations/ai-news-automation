export class NewsUpdater {
    constructor(options = {}) {
        this.lastFetchTime = Date.now();
        this.pollInterval = options.pollInterval || 5 * 60 * 1000; // 5 minutes default
        this.handlers = new Map();
        this.isPolling = false;
    }

    start() {
        if (this.isPolling) return;
        this.isPolling = true;
        this.startPolling();
    }

    stop() {
        this.isPolling = false;
    }

    on(event, handler) {
        if (!this.handlers.has(event)) {
            this.handlers.set(event, new Set());
        }
        this.handlers.get(event).add(handler);
    }

    off(event, handler) {
        const handlers = this.handlers.get(event);
        if (handlers) {
            handlers.delete(handler);
        }
    }

    emit(event, data) {
        const handlers = this.handlers.get(event);
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

    async startPolling() {
        if (!this.isPolling) return;

        try {
            await this.fetchLatestNews();
        } catch (error) {
            console.error('Error fetching news:', error);
            this.emit('error', error);
        }

        // Schedule next poll
        setTimeout(() => this.startPolling(), this.pollInterval);
    }

    async fetchLatestNews() {
        try {
            const response = await fetch(`/api/news?since=${this.lastFetchTime}`);
            if (!response.ok) throw new Error('Failed to fetch news');
            
            const news = await response.json();
            if (news.length > 0) {
                this.lastFetchTime = Date.now();
                this.emit('update', news);

                // Check for breaking news
                const breakingNews = news.filter(article => article.isBreaking);
                if (breakingNews.length > 0) {
                    this.emit('breaking', breakingNews);
                }
            }
        } catch (error) {
            console.error('Error fetching news:', error);
            throw error;
        }
    }

    // Cleanup
    destroy() {
        this.stop();
        this.handlers.clear();
    }
}
