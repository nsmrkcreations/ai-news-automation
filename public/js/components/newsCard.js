// News Card Component
class NewsCard {
    constructor(article) {
        this.article = article;
        this.element = null;
    }

    /**
     * Create news card HTML element
     * @returns {HTMLElement} News card element
     */
    createElement() {
        const card = document.createElement('article');
        card.className = 'news-card';
        card.setAttribute('data-category', this.article.category);
        card.setAttribute('data-id', generateId());
        
        // Handle image loading with fallback
        const imageUrl = this.article.urlToImage || FALLBACK_IMAGES.NEWS_PLACEHOLDER;
        
        card.innerHTML = `
            <div class="news-card-image">
                <img src="${imageUrl}" 
                     alt="${sanitizeHTML(this.article.title)}" 
                     loading="lazy"
                     onerror="this.src='${FALLBACK_IMAGES.NEWS_PLACEHOLDER}'">
                ${this.article.isBreaking ? '<span class="breaking-badge">Breaking</span>' : ''}
                <span class="category-tag">${CATEGORY_NAMES[this.article.category] || this.article.category}</span>
            </div>
            <div class="news-card-content">
                <h3 class="news-card-title">${sanitizeHTML(this.article.title)}</h3>
                <p class="news-card-description">${sanitizeHTML(this.article.description || '')}</p>
                <div class="news-card-meta">
                    <span class="news-card-source">${sanitizeHTML(this.article.source || 'Unknown Source')}</span>
                    <span class="news-card-date">${formatRelativeTime(this.article.publishedAt)}</span>
                </div>
            </div>
        `;

        // Add click handler
        card.addEventListener('click', () => this.handleClick());
        
        // Add hover effects
        card.addEventListener('mouseenter', () => this.handleHover(true));
        card.addEventListener('mouseleave', () => this.handleHover(false));

        this.element = card;
        return card;
    }

    /**
     * Handle card click
     */
    handleClick() {
        if (this.article.url) {
            // Track click event
            this.trackEvent('card_click', {
                title: this.article.title,
                category: this.article.category,
                source: this.article.source
            });
            
            // Open article in new tab
            window.open(this.article.url, '_blank', 'noopener,noreferrer');
        }
    }

    /**
     * Handle card hover
     * @param {boolean} isHovering - Whether card is being hovered
     */
    handleHover(isHovering) {
        if (this.element) {
            if (isHovering) {
                this.element.style.transform = 'translateY(-4px)';
            } else {
                this.element.style.transform = 'translateY(0)';
            }
        }
    }

    /**
     * Track analytics event
     * @param {string} eventName - Event name
     * @param {Object} eventData - Event data
     */
    trackEvent(eventName, eventData) {
        // Analytics tracking (can be extended with Google Analytics, etc.)
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, eventData);
        }
        
        console.log('Event tracked:', eventName, eventData);
    }

    /**
     * Update card content
     * @param {Object} newArticle - Updated article data
     */
    update(newArticle) {
        this.article = { ...this.article, ...newArticle };
        
        if (this.element) {
            // Update title
            const titleElement = this.element.querySelector('.news-card-title');
            if (titleElement) {
                titleElement.textContent = this.article.title;
            }
            
            // Update description
            const descElement = this.element.querySelector('.news-card-description');
            if (descElement) {
                descElement.textContent = this.article.description || '';
            }
            
            // Update meta information
            const sourceElement = this.element.querySelector('.news-card-source');
            if (sourceElement) {
                sourceElement.textContent = this.article.source || 'Unknown Source';
            }
            
            const dateElement = this.element.querySelector('.news-card-date');
            if (dateElement) {
                dateElement.textContent = formatRelativeTime(this.article.publishedAt);
            }
        }
    }

    /**
     * Animate card entrance
     */
    animateIn() {
        if (this.element) {
            animateIn(this.element, CSS_CLASSES.FADE_IN_UP);
        }
    }

    /**
     * Remove card from DOM
     */
    remove() {
        if (this.element && this.element.parentNode) {
            this.element.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                if (this.element && this.element.parentNode) {
                    this.element.parentNode.removeChild(this.element);
                }
            }, 300);
        }
    }
}

// Hero Article Component (larger version of news card)
class HeroArticle {
    constructor(article) {
        this.article = article;
        this.element = null;
    }

    /**
     * Create hero article HTML element
     * @returns {HTMLElement} Hero article element
     */
    createElement() {
        const heroContainer = document.createElement('article');
        heroContainer.className = 'hero-article-container';
        
        const imageUrl = this.article.urlToImage || FALLBACK_IMAGES.HERO_PLACEHOLDER;
        
        heroContainer.innerHTML = `
            <div class="hero-article">
                <div class="hero-article-image">
                    <img src="${imageUrl}" 
                         alt="${sanitizeHTML(this.article.title)}" 
                         loading="eager"
                         onerror="this.src='${FALLBACK_IMAGES.HERO_PLACEHOLDER}'">
                    ${this.article.isBreaking ? '<span class="breaking-badge">Breaking News</span>' : ''}
                </div>
                <div class="hero-article-content">
                    <div class="hero-article-meta">
                        <span class="category-tag">${CATEGORY_NAMES[this.article.category] || this.article.category}</span>
                        <span class="hero-article-date">${formatRelativeTime(this.article.publishedAt)}</span>
                    </div>
                    <h1 class="hero-article-title">${sanitizeHTML(this.article.title)}</h1>
                    <p class="hero-article-description">${sanitizeHTML(this.article.description || '')}</p>
                    <div class="hero-article-footer">
                        <span class="hero-article-source">Source: ${sanitizeHTML(this.article.source || 'Unknown')}</span>
                        <button class="btn btn-primary hero-read-more">Read Full Article</button>
                    </div>
                </div>
            </div>
        `;

        // Add click handlers
        const readMoreBtn = heroContainer.querySelector('.hero-read-more');
        const heroArticle = heroContainer.querySelector('.hero-article');
        
        const clickHandler = () => this.handleClick();
        
        if (readMoreBtn) {
            readMoreBtn.addEventListener('click', clickHandler);
        }
        
        if (heroArticle) {
            heroArticle.addEventListener('click', clickHandler);
            heroArticle.style.cursor = 'pointer';
        }

        this.element = heroContainer;
        return heroContainer;
    }

    /**
     * Handle hero article click
     */
    handleClick() {
        if (this.article.url) {
            this.trackEvent('hero_click', {
                title: this.article.title,
                category: this.article.category,
                source: this.article.source
            });
            
            window.open(this.article.url, '_blank', 'noopener,noreferrer');
        }
    }

    /**
     * Track analytics event
     * @param {string} eventName - Event name
     * @param {Object} eventData - Event data
     */
    trackEvent(eventName, eventData) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, eventData);
        }
        
        console.log('Event tracked:', eventName, eventData);
    }

    /**
     * Animate hero article entrance
     */
    animateIn() {
        if (this.element) {
            animateIn(this.element, CSS_CLASSES.SLIDE_IN_RIGHT);
        }
    }
}

// Trending Article Component (sidebar version)
class TrendingArticle {
    constructor(article, index) {
        this.article = article;
        this.index = index;
        this.element = null;
    }

    /**
     * Create trending article HTML element
     * @returns {HTMLElement} Trending article element
     */
    createElement() {
        const trendingItem = document.createElement('div');
        trendingItem.className = 'trending-article';
        
        const imageUrl = this.article.urlToImage || FALLBACK_IMAGES.NEWS_PLACEHOLDER;
        
        trendingItem.innerHTML = `
            <div class="trending-article-image">
                <img src="${imageUrl}" 
                     alt="${sanitizeHTML(this.article.title)}" 
                     loading="lazy"
                     onerror="this.src='${FALLBACK_IMAGES.NEWS_PLACEHOLDER}'">
            </div>
            <div class="trending-article-content">
                <h4 class="trending-article-title">${sanitizeHTML(truncateText(this.article.title, 80))}</h4>
                <div class="trending-article-meta">
                    <span class="trending-source">${sanitizeHTML(this.article.source || 'Unknown')}</span>
                    <span class="trending-date">${formatRelativeTime(this.article.publishedAt)}</span>
                </div>
            </div>
        `;

        // Add click handler
        trendingItem.addEventListener('click', () => this.handleClick());
        trendingItem.style.cursor = 'pointer';

        this.element = trendingItem;
        return trendingItem;
    }

    /**
     * Handle trending article click
     */
    handleClick() {
        if (this.article.url) {
            this.trackEvent('trending_click', {
                title: this.article.title,
                position: this.index,
                category: this.article.category,
                source: this.article.source
            });
            
            window.open(this.article.url, '_blank', 'noopener,noreferrer');
        }
    }

    /**
     * Track analytics event
     * @param {string} eventName - Event name
     * @param {Object} eventData - Event data
     */
    trackEvent(eventName, eventData) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, eventData);
        }
        
        console.log('Event tracked:', eventName, eventData);
    }

    /**
     * Animate trending article entrance
     */
    animateIn() {
        if (this.element) {
            setTimeout(() => {
                animateIn(this.element, CSS_CLASSES.FADE_IN_UP);
            }, this.index * 100); // Stagger animation
        }
    }
}
