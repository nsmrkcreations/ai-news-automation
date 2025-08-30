// Utility functions
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Lazy loading images
const lazyLoadImages = () => {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
};

// Infinite scroll
class InfiniteScroll {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            threshold: 100,
            loadMoreCallback: null,
            ...options
        };
        this.isLoading = false;
        this.hasMore = true;
        this.setupObserver();
    }

    setupObserver() {
        const options = {
            root: null,
            rootMargin: `${this.options.threshold}px`,
            threshold: 0
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isLoading && this.hasMore) {
                    this.loadMore();
                }
            });
        }, options);

        // Create and observe trigger element
        const trigger = document.createElement('div');
        trigger.className = 'infinite-scroll-trigger';
        this.container.appendChild(trigger);
        this.observer.observe(trigger);
    }

    async loadMore() {
        if (this.isLoading || !this.hasMore) return;

        this.isLoading = true;
        this.showLoading();

        try {
            if (this.options.loadMoreCallback) {
                const hasMore = await this.options.loadMoreCallback();
                this.hasMore = hasMore;
            }
        } catch (error) {
            console.error('Error loading more content:', error);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    showLoading() {
        const loader = document.createElement('div');
        loader.className = 'loading-skeleton';
        loader.style.height = '200px';
        loader.style.marginBottom = '20px';
        this.container.appendChild(loader);
    }

    hideLoading() {
        const loader = this.container.querySelector('.loading-skeleton');
        if (loader) {
            loader.remove();
        }
    }
}

// Breaking news ticker
class BreakingNewsTicker {
    constructor(container) {
        this.container = container;
        this.items = [];
        this.currentIndex = 0;
    }

    setItems(items) {
        this.items = items;
        this.render();
    }

    render() {
        if (!this.items.length) return;

        const ticker = document.createElement('div');
        ticker.className = 'breaking-news-ticker';
        
        const content = document.createElement('span');
        content.textContent = this.items[this.currentIndex];
        ticker.appendChild(content);
        
        this.container.innerHTML = '';
        this.container.appendChild(ticker);

        this.startAnimation();
    }

    startAnimation() {
        setInterval(() => {
            this.currentIndex = (this.currentIndex + 1) % this.items.length;
            const content = this.container.querySelector('span');
            content.textContent = this.items[this.currentIndex];
        }, 5000);
    }
}

// Initialize components
document.addEventListener('DOMContentLoaded', () => {
    // Initialize lazy loading
    lazyLoadImages();

    // Initialize infinite scroll
    const newsGrid = document.querySelector('.news-grid');
    if (newsGrid) {
        new InfiniteScroll(newsGrid, {
            loadMoreCallback: async () => {
                // Implement your load more logic here
                return true; // return false when no more items
            }
        });
    }

    // Initialize breaking news ticker
    const breakingNewsContainer = document.querySelector('.breaking-news-content');
    if (breakingNewsContainer) {
        const ticker = new BreakingNewsTicker(breakingNewsContainer);
        // Add your breaking news items here
        ticker.setItems([
            'Breaking: Major tech announcement expected today',
            'Weather Alert: Storm warning issued for coastal areas',
            'Sports: National team advances to finals'
        ]);
    }

    // Mobile menu toggle
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', () => {
            mainNav.classList.toggle('active');
        });
    }
});
