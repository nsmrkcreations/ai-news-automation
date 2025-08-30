// Hero Section Component
class HeroSection {
    constructor() {
        this.heroArticleContainer = document.querySelector(SELECTORS.HERO_ARTICLE);
        this.trendingContainer = document.querySelector(SELECTORS.TRENDING_ARTICLES);
        this.currentHeroArticle = null;
        this.trendingArticles = [];
    }

    /**
     * Initialize hero section
     */
    init() {
        if (!this.heroArticleContainer || !this.trendingContainer) {
            console.warn('Hero section elements not found');
            return;
        }
    }

    /**
     * Update hero section with new articles
     * @param {Array} articles - Array of articles
     */
    updateContent(articles) {
        if (!articles || articles.length === 0) return;

        // Select hero article (first breaking news or first article)
        const breakingNews = articles.filter(article => article.isBreaking);
        const heroArticle = breakingNews.length > 0 ? breakingNews[0] : articles[0];

        // Select trending articles (next 4-5 articles, excluding hero)
        const remainingArticles = articles.filter(article => article !== heroArticle);
        const trendingArticles = remainingArticles.slice(0, 5);

        this.setHeroArticle(heroArticle);
        this.setTrendingArticles(trendingArticles);
    }

    /**
     * Set the main hero article
     * @param {Object} article - Hero article data
     */
    setHeroArticle(article) {
        if (!article || !this.heroArticleContainer) return;

        // Clear existing content
        this.heroArticleContainer.innerHTML = '';

        // Create hero article component
        this.currentHeroArticle = new HeroArticle(article);
        const heroElement = this.currentHeroArticle.createElement();

        // Add to container
        this.heroArticleContainer.appendChild(heroElement);

        // Animate in
        setTimeout(() => {
            this.currentHeroArticle.animateIn();
        }, 100);
    }

    /**
     * Set trending articles in sidebar
     * @param {Array} articles - Array of trending articles
     */
    setTrendingArticles(articles) {
        if (!articles || articles.length === 0 || !this.trendingContainer) return;

        // Clear existing content
        this.trendingContainer.innerHTML = '';
        this.trendingArticles = [];

        // Create trending article components
        articles.forEach((article, index) => {
            const trendingArticle = new TrendingArticle(article, index);
            const trendingElement = trendingArticle.createElement();
            
            this.trendingContainer.appendChild(trendingElement);
            this.trendingArticles.push(trendingArticle);

            // Animate in with stagger
            setTimeout(() => {
                trendingArticle.animateIn();
            }, (index + 1) * 150);
        });
    }

    /**
     * Refresh hero section content
     * @param {Array} articles - Updated articles array
     */
    refresh(articles) {
        this.updateContent(articles);
    }

    /**
     * Show loading state
     */
    showLoading() {
        if (this.heroArticleContainer) {
            this.heroArticleContainer.innerHTML = `
                <div class="hero-loading">
                    <div class="loading-spinner"></div>
                    <p>Loading featured story...</p>
                </div>
            `;
        }

        if (this.trendingContainer) {
            this.trendingContainer.innerHTML = `
                <div class="trending-loading">
                    <div class="loading-spinner"></div>
                    <p>Loading trending stories...</p>
                </div>
            `;
        }
    }

    /**
     * Show error state
     * @param {string} message - Error message
     */
    showError(message = 'Failed to load stories') {
        if (this.heroArticleContainer) {
            this.heroArticleContainer.innerHTML = `
                <div class="hero-error">
                    <h3>Unable to load featured story</h3>
                    <p>${message}</p>
                    <button class="btn btn-secondary retry-hero">Try Again</button>
                </div>
            `;

            // Add retry handler
            const retryBtn = this.heroArticleContainer.querySelector('.retry-hero');
            if (retryBtn) {
                retryBtn.addEventListener('click', () => {
                    this.dispatchEvent(new CustomEvent('hero-retry'));
                });
            }
        }

        if (this.trendingContainer) {
            this.trendingContainer.innerHTML = `
                <div class="trending-error">
                    <p>Unable to load trending stories</p>
                </div>
            `;
        }
    }

    /**
     * Dispatch custom events
     * @param {CustomEvent} event - Event to dispatch
     */
    dispatchEvent(event) {
        if (this.heroArticleContainer) {
            this.heroArticleContainer.dispatchEvent(event);
        }
    }
}

// Enhanced Hero Article with additional features
class EnhancedHeroArticle extends HeroArticle {
    constructor(article) {
        super(article);
        this.shareButtons = null;
    }

    /**
     * Create enhanced hero article with sharing options
     * @returns {HTMLElement} Enhanced hero article element
     */
    createElement() {
        const heroContainer = super.createElement();
        
        // Add sharing functionality
        this.addSharingButtons(heroContainer);
        
        // Add reading time estimate
        this.addReadingTime(heroContainer);
        
        return heroContainer;
    }

    /**
     * Add social sharing buttons
     * @param {HTMLElement} container - Hero container element
     */
    addSharingButtons(container) {
        const contentDiv = container.querySelector('.hero-article-content');
        if (!contentDiv) return;

        const shareContainer = document.createElement('div');
        shareContainer.className = 'hero-share-buttons';
        shareContainer.innerHTML = `
            <span class="share-label">Share:</span>
            <button class="share-btn twitter" data-platform="twitter" aria-label="Share on Twitter">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
            </button>
            <button class="share-btn facebook" data-platform="facebook" aria-label="Share on Facebook">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
            </button>
            <button class="share-btn copy-link" data-platform="copy" aria-label="Copy link">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                </svg>
            </button>
        `;

        contentDiv.appendChild(shareContainer);

        // Add share button handlers
        shareContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.share-btn');
            if (btn) {
                this.handleShare(btn.dataset.platform);
            }
        });

        this.shareButtons = shareContainer;
    }

    /**
     * Handle social sharing
     * @param {string} platform - Social platform
     */
    handleShare(platform) {
        const url = this.article.url;
        const title = this.article.title;
        const text = `${title} - via NewSurgeAI`;

        switch (platform) {
            case 'twitter':
                window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`, '_blank');
                break;
            case 'facebook':
                window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
                break;
            case 'copy':
                copyToClipboard(url).then(success => {
                    if (success) {
                        showSuccess('Link copied to clipboard!');
                    }
                });
                break;
        }

        // Track sharing event
        this.trackEvent('article_share', {
            platform: platform,
            title: title,
            url: url
        });
    }

    /**
     * Add estimated reading time
     * @param {HTMLElement} container - Hero container element
     */
    addReadingTime(container) {
        const metaDiv = container.querySelector('.hero-article-meta');
        if (!metaDiv) return;

        // Estimate reading time (average 200 words per minute)
        const wordCount = (this.article.description || '').split(' ').length;
        const readingTime = Math.max(1, Math.ceil(wordCount / 200));

        const readingTimeSpan = document.createElement('span');
        readingTimeSpan.className = 'reading-time';
        readingTimeSpan.textContent = `${readingTime} min read`;

        metaDiv.appendChild(readingTimeSpan);
    }
}
