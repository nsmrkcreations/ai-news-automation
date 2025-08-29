export class NewsCardRenderer {
    static defaultImage = '/images/fallback.jpg';

    static getCategoryImage(category) {
        const images = {
            technology: '/images/news/technology.jpg',
            business: '/images/news/business.jpg',
            science: '/images/news/science.jpg',
            health: '/images/news/health.jpg',
            sports: '/images/news/sports.jpg',
            entertainment: '/images/news/entertainment.jpg',
            general: '/images/news/general.jpg'
        };
        return images[category] || this.defaultImage;
    }

    static async preloadImage(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Image not found');
            return url;
        } catch (error) {
            console.warn(`Failed to load image: ${url}, using fallback`);
            return this.defaultImage;
        }
    }

    static async createNewsCard(article) {
        const imageUrl = await this.preloadImage(this.getCategoryImage(article.category));
        
        return `
            <article class="news-card">
                <div class="news-image-container">
                    <img src="${imageUrl}" 
                         alt="${article.title}" 
                         class="news-image"
                         loading="lazy"
                         onerror="this.src='${this.defaultImage}'">
                </div>
                <div class="news-content">
                    <span class="news-category">${article.category}</span>
                    <h2 class="news-title">${article.title}</h2>
                    <p class="news-excerpt">${article.description}</p>
                    <div class="news-meta">
                        <span class="news-source">${article.source}</span>
                        <span class="news-time">${article.readingTime}</span>
                    </div>
                    <div class="news-actions">
                        <a href="${article.url}" class="btn btn-primary" target="_blank" rel="noopener">
                            Read More
                            <i class="fas fa-arrow-right"></i>
                        </a>
                        <button class="btn btn-secondary share-btn" data-url="${article.url}" data-title="${article.title}">
                            <i class="fas fa-share-alt"></i>
                            Share
                        </button>
                    </div>
                </div>
            </article>
        `;
    }
}
