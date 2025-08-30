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
        // Create date object from the string
        const date = new Date(dateString);
        
        // Check if the date is valid
        if (isNaN(date.getTime())) {
            // If date is invalid, try to parse it as ISO string
            const isoDate = new Date(dateString + 'Z');
            if (!isNaN(isoDate.getTime())) {
                // If ISO date is valid, use it
                return isoDate.toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true,
                    timeZoneName: 'short'
                });
            }
            return 'Invalid date';
        }
        
        // Format the valid date
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: true,
            timeZoneName: 'short'
        });
    }
}
