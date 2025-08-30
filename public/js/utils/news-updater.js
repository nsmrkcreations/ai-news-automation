// News updater utility class
export class NewsUpdater {
    constructor() {
        this.newsDataUrl = 'data/news.json';
    }
    
    async getNews() {
        try {
            const response = await fetch(this.newsDataUrl);
            if (!response.ok) {
                throw new Error('Failed to fetch news data');
            }
            
            const news = await response.json();
            return this.sortNewsByDate(news);
        } catch (error) {
            console.error('Error fetching news:', error);
            return [];
        }
    }
    
    sortNewsByDate(news) {
        return news.sort((a, b) => {
            return new Date(b.publishedAt) - new Date(a.publishedAt);
        });
    }
}
