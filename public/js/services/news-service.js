// News data fetching and management
class NewsService {
    constructor() {
        this.newsCache = null;
        this.categories = new Set();
    }

    async fetchNews() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) throw new Error('Failed to fetch news');
            this.newsCache = await response.json();
            this.extractCategories();
            return this.newsCache;
        } catch (error) {
            console.error('Error fetching news:', error);
            throw error;
        }
    }

    extractCategories() {
        this.newsCache.forEach(article => {
            if (article.category) {
                this.categories.add(article.category);
            }
        });
    }

    getNewsByCategory(category) {
        if (!this.newsCache) return [];
        if (category === 'all') return this.newsCache;
        return this.newsCache.filter(article => article.category === category);
    }

    getFeaturedNews() {
        if (!this.newsCache) return null;
        return this.newsCache.find(article => article.featured) || this.newsCache[0];
    }

    getSecondaryNews(count = 3) {
        if (!this.newsCache) return [];
        const featured = this.getFeaturedNews();
        return this.newsCache
            .filter(article => article !== featured)
            .slice(0, count);
    }

    getLatestNews(startIndex = 0, count = 6) {
        if (!this.newsCache) return [];
        const featured = this.getFeaturedNews();
        const secondary = new Set(this.getSecondaryNews());
        
        return this.newsCache
            .filter(article => article !== featured && !secondary.has(article))
            .slice(startIndex, startIndex + count);
    }

    formatPublishDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMinutes = Math.floor((now - date) / 1000 / 60);
        
        if (diffMinutes < 60) {
            return `${diffMinutes} minutes ago`;
        }
        
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) {
            return `${diffHours} hours ago`;
        }
        
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays < 7) {
            return `${diffDays} days ago`;
        }
        
        return date.toLocaleDateString('en-US', { 
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }
}
