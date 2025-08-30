/**
 * Modern Layout JavaScript - Populates sections with news data
 */

class ModernLayoutManager {
    constructor() {
        this.newsData = [];
        this.currentCategory = 'all';
        this.init();
    }

    async init() {
        await this.loadNewsData();
        this.setupEventListeners();
        this.populateNewsGrid();
        this.updateActiveDate();
    }
    
    setupEventListeners() {
        // Category filter
        document.querySelectorAll('.category-tag').forEach(tag => {
            tag.addEventListener('click', (e) => {
                e.preventDefault();
                this.currentCategory = tag.textContent.toLowerCase();
                document.querySelectorAll('.category-tag').forEach(t => t.classList.remove('active'));
                tag.classList.add('active');
                this.populateNewsGrid();
            });
        });
        
        // Search functionality
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearch.bind(this));
        }
    }
    
    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        if (searchTerm.length < 2) {
            this.populateNewsGrid();
            return;
        }
        
        const filteredNews = this.newsData.filter(article => 
            article.title.toLowerCase().includes(searchTerm) || 
            (article.description && article.description.toLowerCase().includes(searchTerm))
        );
        
        this.renderNewsGrid(filteredNews);
    }

    async loadNewsData() {
        try {
            const response = await fetch('data/news.json');
            let newsData = await response.json();
            
            // Sort by publication date - newest first
            this.newsData = newsData.map(article => ({
                ...article,
                // Ensure all required fields have default values
                urlToImage: article.urlToImage || 'https://via.placeholder.com/600x400/1a1a2e/e94560?text=News',
                source: article.source?.name || 'NewsAPI',
                publishedAt: article.publishedAt || new Date().toISOString(),
                category: article.category || 'general'
            })).sort((a, b) => {
                const dateA = new Date(a.publishedAt);
                const dateB = new Date(b.publishedAt);
                return dateB - dateA; // Newest first
            });
            
        } catch (error) {
            console.error('Failed to load news data:', error);
            this.newsData = this.getFallbackData();
        }
    }
    
    populateNewsGrid() {
        let filteredNews = [...this.newsData];
        
        // Filter by category if not 'all'
        if (this.currentCategory !== 'all') {
            filteredNews = filteredNews.filter(article => 
                article.category.toLowerCase() === this.currentCategory
            );
        }
        
        this.renderNewsGrid(filteredNews);
    }
    
    renderNewsGrid(articles) {
        const grid = document.getElementById('news-grid');
        if (!grid) return;
        
        if (!articles || articles.length === 0) {
            grid.innerHTML = '<p class="no-results">No articles found. Try a different search term or category.</p>';
            return;
        }
        
        grid.innerHTML = articles.map(article => this.createNewsCard(article)).join('');
    }
    
    createNewsCard(article) {
        const publishedDate = new Date(article.publishedAt);
        const formattedDate = publishedDate.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        return `
            <article class="news-card">
                <div class="news-image-container">
                    <img src="${article.urlToImage}" alt="${article.title}" class="news-image" loading="lazy">
                    <span class="news-category">${article.category || 'General'}</span>
                </div>
                <div class="news-content">
                    <h3 class="news-title">${article.title}</h3>
                    <p class="news-excerpt">${article.description || ''}</p>
                    <div class="news-meta">
                        <span class="news-source">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/>
                            </svg>
                            ${article.source}
                        </span>
                        <span class="news-date">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
                            </svg>
                            ${formattedDate}
                        </span>
                    </div>
                </div>
            </article>
        `;
    }
    
    updateActiveDate() {
        const dateElement = document.getElementById('current-date');
        if (dateElement) {
            const options = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            };
            dateElement.textContent = new Date().toLocaleDateString('en-US', options);
        }
    }

    // Fallback data in case of API failure
    getFallbackData() {
        return [
            {
                title: 'AI Breakthrough: New Model Achieves Human-Level Performance',
                description: 'Researchers have developed an AI model that demonstrates human-level performance on a range of complex tasks.',
                urlToImage: 'https://images.unsplash.com/photo-1677442135136-760c81388f98?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80',
                source: 'Tech News',
                publishedAt: new Date().toISOString(),
                category: 'technology'
            },
            {
                title: 'Global Markets React to New Economic Policies',
                description: 'Stock markets around the world show mixed reactions to recently announced economic policies.',
                urlToImage: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80',
                source: 'Financial Times',
                publishedAt: new Date(Date.now() - 86400000).toISOString(),
                category: 'business'
            },
            {
                title: 'New Study Reveals Benefits of Mediterranean Diet',
                description: 'Research confirms significant health benefits associated with the Mediterranean diet.',
                urlToImage: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1200&q=80',
                source: 'Health Journal',
                publishedAt: new Date(Date.now() - 172800000).toISOString(),
                category: 'health'
            }
        ];
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
