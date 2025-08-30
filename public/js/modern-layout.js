/**
 * Modern Layout JavaScript - Populates sections with news data
 */

class ModernLayoutManager {
    constructor() {
        this.newsData = [];
        this.init();
    }

    async init() {
        await this.loadNewsData();
        this.populateHeroSection();
        this.populateLatestNews();
        this.populateBulletinStory();
        this.populateMostRead();
        this.populateEditorspick();
        this.populateBusinessSports();
        this.populateTopCreator();
    }

    async loadNewsData() {
        try {
            const response = await fetch('data/news.json');
            let newsData = await response.json();
            
            // Sort by publication date - newest first
            this.newsData = newsData.sort((a, b) => {
                const dateA = new Date(a.publishedAt || 0);
                const dateB = new Date(b.publishedAt || 0);
                return dateB - dateA; // Newest first
            });
            
        } catch (error) {
            console.error('Failed to load news data:', error);
            this.newsData = this.getFallbackData();
        }
    }

    populateHeroSection() {
        const heroData = this.newsData[0] || this.getFallbackData()[0];
        
        document.getElementById('hero-image').src = heroData.urlToImage || 'https://via.placeholder.com/600x400/1a1a2e/e94560?text=Featured+News';
        document.getElementById('hero-title').textContent = heroData.title || 'Latest Breaking News';
        document.getElementById('hero-description').textContent = heroData.description || 'Stay updated with the latest news and developments.';
        document.getElementById('hero-date').textContent = this.formatDate(heroData.publishedAt);
    }

    populateLatestNews() {
        const container = document.getElementById('latest-news-grid');
        const latestNews = this.newsData.slice(1, 5);

        container.innerHTML = latestNews.map(article => `
            <div class="news-card-small">
                <img src="${article.urlToImage || 'https://via.placeholder.com/300x160/667eea/ffffff?text=News'}" 
                     alt="${article.title}" 
                     onerror="this.src='https://via.placeholder.com/300x160/667eea/ffffff?text=News'">
                <div class="content">
                    <h3 class="title">${this.truncateText(article.title, 60)}</h3>
                    <div class="meta">
                        <span class="source">${article.source || 'NewsAPI'}</span>
                        <span class="date">${this.formatDate(article.publishedAt)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    populateBulletinStory() {
        const container = document.querySelector('.bulletin-avatars');
        const avatars = [
            { name: 'Tech Reporter', image: 'https://via.placeholder.com/60x60/667eea/ffffff?text=TR' },
            { name: 'Business Analyst', image: 'https://via.placeholder.com/60x60/764ba2/ffffff?text=BA' },
            { name: 'Science Writer', image: 'https://via.placeholder.com/60x60/e94560/ffffff?text=SW' },
            { name: 'Sports Editor', image: 'https://via.placeholder.com/60x60/4CAF50/ffffff?text=SE' },
            { name: 'World News', image: 'https://via.placeholder.com/60x60/ff9800/ffffff?text=WN' },
            { name: 'Health Reporter', image: 'https://via.placeholder.com/60x60/9c27b0/ffffff?text=HR' },
            { name: 'Finance Expert', image: 'https://via.placeholder.com/60x60/f44336/ffffff?text=FE' },
            { name: 'Tech Analyst', image: 'https://via.placeholder.com/60x60/2196f3/ffffff?text=TA' },
            { name: 'Climate Reporter', image: 'https://via.placeholder.com/60x60/795548/ffffff?text=CR' }
        ];

        container.innerHTML = avatars.map(avatar => `
            <div class="avatar" title="${avatar.name}">
                <img src="${avatar.image}" alt="${avatar.name}">
            </div>
        `).join('');
    }

    populateMostRead() {
        const container = document.querySelector('.most-read-grid');
        const mainArticle = this.newsData[0] || this.getFallbackData()[0];
        const sideArticles = this.newsData.slice(1, 4);

        container.innerHTML = `
            <div class="most-read-main">
                <img src="${mainArticle.urlToImage || 'https://via.placeholder.com/600x300/1a1a2e/e94560?text=Most+Read'}" 
                     alt="${mainArticle.title}">
                <div class="most-read-overlay">
                    <h3>${this.truncateText(mainArticle.title, 80)}</h3>
                    <p>${this.truncateText(mainArticle.description, 120)}</p>
                </div>
            </div>
            <div class="most-read-sidebar">
                ${sideArticles.map(article => `
                    <div class="news-card-small">
                        <img src="${article.urlToImage || 'https://via.placeholder.com/200x120/667eea/ffffff?text=News'}" 
                             alt="${article.title}">
                        <div class="content">
                            <h4 class="title">${this.truncateText(article.title, 50)}</h4>
                            <div class="meta">
                                <span class="date">${this.formatDate(article.publishedAt)}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    populateEditorspick() {
        const container = document.querySelector('.editors-grid');
        const mainArticle = this.newsData[1] || this.getFallbackData()[1];
        const sideArticles = this.newsData.slice(2, 6);

        container.innerHTML = `
            <div class="editors-main">
                <img src="${mainArticle.urlToImage || 'https://via.placeholder.com/500x400/ff9800/ffffff?text=Editors+Pick'}" 
                     alt="${mainArticle.title}">
                <div class="editors-overlay">
                    <h3>${this.truncateText(mainArticle.title, 60)}</h3>
                    <p>${this.truncateText(mainArticle.description, 100)}</p>
                </div>
            </div>
            ${sideArticles.map(article => `
                <div class="news-card-small">
                    <img src="${article.urlToImage || 'https://via.placeholder.com/250x150/764ba2/ffffff?text=News'}" 
                         alt="${article.title}">
                    <div class="content">
                        <h4 class="title">${this.truncateText(article.title, 40)}</h4>
                    </div>
                </div>
            `).join('')}
        `;
    }

    populateBusinessSports() {
        const businessContainer = document.querySelector('.business-grid');
        const sportContainer = document.querySelector('.sport-grid');
        
        const businessNews = this.newsData.filter(article => 
            article.category === 'business' || article.title.toLowerCase().includes('business')
        ).slice(0, 4);
        
        const sportsNews = this.newsData.filter(article => 
            article.category === 'sports' || article.title.toLowerCase().includes('sport')
        ).slice(0, 4);

        // Fallback if no specific category news
        const fallbackBusiness = businessNews.length ? businessNews : this.newsData.slice(0, 4);
        const fallbackSports = sportsNews.length ? sportsNews : this.newsData.slice(4, 8);

        businessContainer.innerHTML = fallbackBusiness.map(article => `
            <div class="news-card-small">
                <img src="${article.urlToImage || 'https://via.placeholder.com/200x120/4CAF50/ffffff?text=Business'}" 
                     alt="${article.title}">
                <div class="content">
                    <h4 class="title">${this.truncateText(article.title, 45)}</h4>
                    <div class="meta">
                        <span class="date">${this.formatDate(article.publishedAt)}</span>
                    </div>
                </div>
            </div>
        `).join('');

        sportContainer.innerHTML = fallbackSports.map(article => `
            <div class="news-card-small">
                <img src="${article.urlToImage || 'https://via.placeholder.com/200x120/f44336/ffffff?text=Sports'}" 
                     alt="${article.title}">
                <div class="content">
                    <h4 class="title">${this.truncateText(article.title, 45)}</h4>
                    <div class="meta">
                        <span class="date">${this.formatDate(article.publishedAt)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    populateTopCreator() {
        const container = document.querySelector('.creator-grid');
        const creators = [
            { name: 'Alex Smith', role: 'Tech Editor', image: 'https://via.placeholder.com/60x60/667eea/ffffff?text=AS' },
            { name: 'Sarah Johnson', role: 'Business Reporter', image: 'https://via.placeholder.com/60x60/764ba2/ffffff?text=SJ' },
            { name: 'Mike Chen', role: 'Science Writer', image: 'https://via.placeholder.com/60x60/e94560/ffffff?text=MC' },
            { name: 'Emma Davis', role: 'Sports Analyst', image: 'https://via.placeholder.com/60x60/4CAF50/ffffff?text=ED' }
        ];

        container.innerHTML = creators.map(creator => `
            <div class="creator-card">
                <div class="creator-avatar">
                    <img src="${creator.image}" alt="${creator.name}">
                </div>
                <div class="creator-name">${creator.name}</div>
                <div class="creator-role">${creator.role}</div>
            </div>
        `).join('');
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    formatDate(dateString) {
        if (!dateString) return 'Today';
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Today';
        if (diffDays === 2) return 'Yesterday';
        if (diffDays <= 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }

    getFallbackData() {
        return [
            {
                title: "AI Revolution Transforms Healthcare Industry",
                description: "Artificial intelligence is revolutionizing healthcare with breakthrough diagnostic tools and treatment methods.",
                urlToImage: "https://via.placeholder.com/600x400/667eea/ffffff?text=AI+Healthcare",
                publishedAt: new Date().toISOString(),
                source: "TechNews",
                category: "technology"
            },
            {
                title: "Global Markets Show Strong Recovery",
                description: "International markets demonstrate resilience with significant gains across major indices.",
                urlToImage: "https://via.placeholder.com/600x400/4CAF50/ffffff?text=Markets",
                publishedAt: new Date(Date.now() - 86400000).toISOString(),
                source: "BusinessDaily",
                category: "business"
            }
        ];
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ModernLayoutManager();
    });
} else {
    new ModernLayoutManager();
}
