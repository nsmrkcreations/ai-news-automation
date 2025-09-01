class NewsUI {
    constructor(newsService) {
        this.newsService = newsService;
        this.currentPage = 0;
        this.itemsPerPage = 6;
        this.isLoading = false;
        
        // DOM Elements
        this.featuredSection = document.querySelector('.featured-section');
        this.secondaryStories = document.querySelector('.secondary-stories');
        this.newsGrid = document.querySelector('.news-grid');
        
        // Initialize infinite scroll
        this.setupInfiniteScroll();
    }

    async initialize() {
        try {
            await this.newsService.fetchNews();
            await this.renderAllSections();
        } catch (error) {
            console.error('Failed to initialize news UI:', error);
            this.showError('Failed to load news. Please try again later.');
        }
    }

    async renderAllSections() {
        this.renderFeaturedStory();
        this.renderSecondaryStories();
        await this.renderNewsGrid();
    }

    renderFeaturedStory() {
        const featured = this.newsService.getFeaturedNews();
        if (!featured) return;

        const mainStory = document.createElement('article');
        mainStory.className = 'main-story';
        mainStory.innerHTML = `
            <img src="${featured.urlToImage || '/images/placeholder.jpg'}" 
                 alt="${featured.title}" 
                 class="main-story-image"
                 loading="lazy">
            <div class="main-story-content">
                <span class="category-tag ${featured.category || 'general'}">${featured.source.name}</span>
                <h2 class="news-title">${featured.title}</h2>
                <p class="news-excerpt">${featured.description}</p>
                <div class="news-meta">
                    <span class="publish-time">${this.newsService.formatPublishDate(featured.publishedAt)}</span>
                    <span class="read-time">${this.estimateReadTime(featured.content)} min read</span>
                </div>
            </div>
        `;

        this.featuredSection.innerHTML = '';
        this.featuredSection.appendChild(mainStory);
    }

    renderSecondaryStories() {
        const secondaryNews = this.newsService.getSecondaryNews();
        
        this.secondaryStories.innerHTML = secondaryNews.map(story => `
            <article class="secondary-story">
                <img src="${story.urlToImage || '/images/placeholder.jpg'}" 
                     alt="${story.title}" 
                     class="secondary-story-image"
                     loading="lazy">
                <div class="secondary-story-content">
                    <span class="category-tag ${story.category || 'general'}">${story.source.name}</span>
                    <h3 class="news-title">${story.title}</h3>
                    <div class="news-meta">
                        <span class="publish-time">${this.newsService.formatPublishDate(story.publishedAt)}</span>
                    </div>
                </div>
            </article>
        `).join('');
    }

    async renderNewsGrid(append = false) {
        if (this.isLoading) return;
        this.isLoading = true;

        try {
            const news = this.newsService.getLatestNews(
                this.currentPage * this.itemsPerPage,
                this.itemsPerPage
            );

            const newsHTML = news.map(article => `
                <article class="news-card">
                    <img src="${article.urlToImage || '/images/placeholder.jpg'}" 
                         alt="${article.title}" 
                         class="news-card-image"
                         loading="lazy">
                    <div class="news-card-content">
                        <span class="category-tag ${article.category || 'general'}">${article.source.name}</span>
                        <h3 class="news-title">${article.title}</h3>
                        <p class="news-excerpt">${article.description}</p>
                        <div class="article-footer">
                            <span class="publish-time">${this.newsService.formatPublishDate(article.publishedAt)}</span>
                            <div class="social-share">
                                <button class="share-button" aria-label="Share on Twitter">
                                    <i class="fab fa-twitter"></i>
                                </button>
                                <button class="share-button" aria-label="Share on Facebook">
                                    <i class="fab fa-facebook"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </article>
            `).join('');

            if (append) {
                this.newsGrid.insertAdjacentHTML('beforeend', newsHTML);
            } else {
                this.newsGrid.innerHTML = newsHTML;
            }

            this.currentPage++;
        } catch (error) {
            console.error('Error rendering news grid:', error);
        } finally {
            this.isLoading = false;
        }
    }

    setupInfiniteScroll() {
        const options = {
            root: null,
            rootMargin: '100px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isLoading) {
                    this.renderNewsGrid(true);
                }
            });
        }, options);

        // Create and observe sentinel element
        const sentinel = document.createElement('div');
        sentinel.className = 'infinite-scroll-sentinel';
        this.newsGrid.parentNode.appendChild(sentinel);
        observer.observe(sentinel);
    }

    estimateReadTime(content) {
        const wordsPerMinute = 200;
        const words = content ? content.trim().split(/\s+/).length : 0;
        return Math.max(1, Math.ceil(words / wordsPerMinute));
    }

    showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        this.newsGrid.parentNode.insertBefore(errorElement, this.newsGrid);
    }
}
