class CategoriesHandler {
    constructor() {
        this.newsContainer = document.getElementById('news-container');
        this.categories = new Set();
        this.newsData = [];
        this.currentFilter = null;
        this.placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwIDAgODAwIDQwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YzZjRmNiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9Ii85Y2E3YmMiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBpbWFnZSBhdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPg==';
        
        if (this.newsContainer) {
            this.initialize();
        }
    }

    async initialize() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.newsData = await response.json();
            
            // Sort articles by date (latest first)
            this.newsData.sort((a, b) => {
                const dateA = new Date(a.publishedAt || 0);
                const dateB = new Date(b.publishedAt || 0);
                return dateB - dateA;
            });
            
            this.setupCategoryFilters();
            this.checkUrlParams();
            this.displayNewsByCategory();
            
            console.log(`Categories initialized with ${this.newsData.length} articles`);
        } catch (error) {
            console.error('Error loading news:', error);
            this.showError('Failed to load news articles. Please try again later.');
        }
    }

    setupCategoryFilters() {
        // Get unique categories
        const categories = [...new Set(this.newsData.map(article => article.category || 'General'))];
        categories.sort();
        
        // Create category filter buttons
        const filterContainer = document.createElement('div');
        filterContainer.className = 'mb-8 flex flex-wrap gap-2 justify-center';
        filterContainer.innerHTML = `
            <button class="category-filter active px-4 py-2 rounded-full bg-[var(--primary-color)] text-white text-sm font-medium transition-colors" 
                    data-category="all">
                All Categories (${this.newsData.length})
            </button>
            ${categories.map(category => {
                const count = this.newsData.filter(article => (article.category || 'General') === category).length;
                return `
                    <button class="category-filter px-4 py-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-[var(--primary-color)] hover:text-white transition-colors" 
                            data-category="${category}">
                        ${category} (${count})
                    </button>
                `;
            }).join('')}
        `;
        
        // Insert filter container before news container
        this.newsContainer.parentNode.insertBefore(filterContainer, this.newsContainer);
        
        // Add event listeners to filter buttons
        filterContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('category-filter')) {
                this.handleCategoryFilter(e.target);
            }
        });
    }

    checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const category = urlParams.get('category');
        if (category && category !== 'all') {
            this.currentFilter = category;
            // Update active filter button
            setTimeout(() => {
                const filterButton = document.querySelector(`[data-category="${category}"]`);
                if (filterButton) {
                    this.handleCategoryFilter(filterButton);
                }
            }, 100);
        }
    }

    handleCategoryFilter(button) {
        // Update active state
        document.querySelectorAll('.category-filter').forEach(btn => {
            btn.classList.remove('active', 'bg-[var(--primary-color)]', 'text-white');
            btn.classList.add('bg-gray-200', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
        });
        
        button.classList.add('active', 'bg-[var(--primary-color)]', 'text-white');
        button.classList.remove('bg-gray-200', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
        
        // Update current filter
        this.currentFilter = button.dataset.category === 'all' ? null : button.dataset.category;
        
        // Update URL
        const url = new URL(window.location);
        if (this.currentFilter) {
            url.searchParams.set('category', this.currentFilter);
        } else {
            url.searchParams.delete('category');
        }
        window.history.replaceState({}, '', url);
        
        // Display filtered news
        this.displayNewsByCategory();
    }

    showError(message) {
        this.newsContainer.innerHTML = `
            <div class="text-center py-12">
                <i class="material-icons text-5xl text-red-400 mb-4">error_outline</i>
                <h3 class="text-xl font-medium text-gray-600 dark:text-gray-300 mb-2">Error Loading News</h3>
                <p class="text-gray-500">${message}</p>
                <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-[var(--primary-color)] text-white rounded-md hover:opacity-90">
                    Try Again
                </button>
            </div>
        `;
    }

    displayNewsByCategory() {
        let articlesToShow = this.newsData;
        
        // Filter by category if selected
        if (this.currentFilter) {
            articlesToShow = this.newsData.filter(article => 
                (article.category || 'General') === this.currentFilter
            );
        }
        
        if (articlesToShow.length === 0) {
            this.newsContainer.innerHTML = `
                <div class="text-center py-12">
                    <i class="material-icons text-5xl text-gray-400 mb-4">article</i>
                    <h3 class="text-xl font-medium text-gray-600 dark:text-gray-300">No articles found</h3>
                    <p class="text-gray-500 mt-2">
                        ${this.currentFilter ? `No articles in "${this.currentFilter}" category.` : 'No articles available.'}
                    </p>
                </div>
            `;
            return;
        }
        
        if (this.currentFilter) {
            // Show all articles in the selected category
            this.displaySingleCategory(this.currentFilter, articlesToShow);
        } else {
            // Group and show by all categories
            this.displayAllCategories(articlesToShow);
        }
    }

    displayAllCategories(articles) {
        const newsByCategory = {};
        
        // Group news by category
        articles.forEach(article => {
            const category = article.category || 'General';
            if (!newsByCategory[category]) newsByCategory[category] = [];
            newsByCategory[category].push(article);
        });

        // Sort categories by article count (descending)
        const sortedCategories = Object.entries(newsByCategory)
            .sort(([,a], [,b]) => b.length - a.length);

        // Generate HTML
        let html = '';
        for (const [category, categoryArticles] of sortedCategories) {
            html += `
                <div class="mb-12">
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-2xl font-bold pb-2 border-b border-gray-200 dark:border-gray-700 flex-grow">
                            ${category} <span class="text-lg text-gray-500">(${categoryArticles.length})</span>
                        </h2>
                        <button class="ml-4 text-[var(--primary-color)] hover:underline text-sm font-medium" 
                                onclick="window.categoriesHandler.showCategory('${category}')">
                            View All →
                        </button>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        ${categoryArticles.slice(0, 8).map(article => this.createArticleCard(article)).join('')}
                    </div>
                    ${categoryArticles.length > 8 ? `
                        <div class="text-center mt-6">
                            <button class="px-6 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-[var(--primary-color)] hover:text-white transition-colors"
                                    onclick="window.categoriesHandler.showCategory('${category}')">
                                View ${categoryArticles.length - 8} More Articles
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        this.newsContainer.innerHTML = html;
    }

    displaySingleCategory(category, articles) {
        const html = `
            <div class="mb-8">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
                        ${category} <span class="text-xl text-gray-500">(${articles.length} articles)</span>
                    </h2>
                    <button class="text-[var(--primary-color)] hover:underline text-sm font-medium" 
                            onclick="window.categoriesHandler.showAllCategories()">
                        ← Back to All Categories
                    </button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    ${articles.map(article => this.createArticleCard(article)).join('')}
                </div>
            </div>
        `;
        this.newsContainer.innerHTML = html;
    }

    showCategory(category) {
        const filterButton = document.querySelector(`[data-category="${category}"]`);
        if (filterButton) {
            this.handleCategoryFilter(filterButton);
        }
    }

    showAllCategories() {
        const allButton = document.querySelector('[data-category="all"]');
        if (allButton) {
            this.handleCategoryFilter(allButton);
        }
    }

    createArticleCard(article) {
        // Extract image URL
        const imageUrl = this.extractImageUrl(article) || this.placeholderImage;
        
        // Format date and time
        const date = this.formatDate(article.publishedAt);
        const timeAgo = this.formatTimeAgo(article.publishedAt);
        
        // Clean description
        const description = this.stripHtml(article.description || '').substring(0, 180);
        const truncatedDescription = description.length === 180 ? description + '...' : description;
        
        // Check if article is AI enhanced
        const isAIEnhanced = article.aiEnhanced || article.aiBadge;
        
        return `
            <article class="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105 flex flex-col h-full">
                <!-- Smaller image section - 25% height -->
                <a href="article.html?id=${encodeURIComponent(article.url)}" class="block">
                    <div class="h-32 bg-cover bg-center relative" style="background-image: url('${imageUrl}')"
                         onerror="this.style.backgroundImage='url(${this.placeholderImage})';">
                        <div class="absolute top-2 left-2">
                            <span class="px-2 py-1 bg-[var(--primary-color)] text-white text-xs font-medium rounded-full">
                                ${article.category || 'General'}
                            </span>
                        </div>
                        ${isAIEnhanced ? `
                            <div class="absolute top-2 right-2">
                                <div class="flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white text-xs font-medium">
                                    <i class="material-icons text-xs mr-1">smart_toy</i>
                                    AI
                                </div>
                            </div>
                        ` : article.source?.name ? `
                            <div class="absolute bottom-2 right-2">
                                <span class="px-2 py-1 bg-black bg-opacity-70 text-white text-xs rounded">
                                    ${article.source.name}
                                </span>
                            </div>
                        ` : ''}
                    </div>
                </a>
                
                <!-- Larger content section - 75% height -->
                <div class="p-4 flex flex-col flex-grow">
                    ${isAIEnhanced ? `
                        <div class="flex items-center mb-2">
                            <div class="inline-flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 text-purple-700 dark:text-purple-300 text-xs font-medium">
                                <i class="material-icons text-xs mr-1">smart_toy</i>
                                AI Enhanced
                            </div>
                        </div>
                    ` : ''}
                    <div class="flex items-center text-xs text-gray-500 dark:text-gray-400 mb-2">
                        <span>${date}</span>
                        <span class="mx-2">•</span>
                        <span>${timeAgo}</span>
                        ${article.source?.name && !isAIEnhanced ? `
                            <span class="mx-2">•</span>
                            <span>${article.source.name}</span>
                        ` : ''}
                    </div>
                    <a href="article.html?id=${encodeURIComponent(article.url)}" class="hover:text-[var(--primary-color)] transition-colors">
                        <h3 class="text-base md:text-lg font-bold mb-3 line-clamp-2 leading-tight">${article.title}</h3>
                    </a>
                    <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-4 flex-grow mb-4">
                        ${truncatedDescription}
                    </p>
                    <div class="mt-auto">
                        <a href="article.html?id=${encodeURIComponent(article.url)}" 
                           class="inline-flex items-center text-[var(--primary-color)] hover:underline text-sm font-medium group w-full justify-center py-2 border border-[var(--primary-color)] rounded-md hover:bg-[var(--primary-color)] hover:text-white transition-colors">
                            Read Full Article
                            <i class="material-icons text-sm ml-1 transform group-hover:translate-x-1 transition-transform">arrow_forward</i>
                        </a>
                    </div>
                </div>
            </article>
        `;
    }

    // Helper function to extract image URL from article
    extractImageUrl(article) {
        try {
            // First try to get from imageUrl if it exists and is a valid URL
            if (article.imageUrl && this.isValidUrl(article.imageUrl)) {
                return article.imageUrl;
            }
            
            // Fall back to urlToImage if it exists and is a valid URL
            if (article.urlToImage && this.isValidUrl(article.urlToImage)) {
                return article.urlToImage;
            }
            
            // Check for image in content
            if (article.content) {
                const imgMatch = article.content.match(/<img[^>]+src=["'](https?:\/\/[^"']+?\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (imgMatch && imgMatch[1]) {
                    const imgUrl = imgMatch[1].replace(/&amp;/g, '&');
                    if (this.isValidUrl(imgUrl)) {
                        return imgUrl;
                    }
                }
            }
            
            return null;
        } catch (error) {
            console.error('Error extracting image URL:', error);
            return null;
        }
    }
    
    // Helper function to validate URLs
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    stripHtml(html) {
        if (!html) return '';
        try {
            const tmp = document.createElement('div');
            tmp.innerHTML = html;
            return tmp.textContent || tmp.innerText || '';
        } catch (error) {
            return String(html).replace(/<[^>]*>?/gm, '');
        }
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown date';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return 'Unknown date';
        }
    }

    formatTimeAgo(dateString) {
        if (!dateString) return 'recently';
        try {
            const date = new Date(dateString);
            const now = new Date();
            const seconds = Math.floor((now - date) / 1000);
            
            let interval = Math.floor(seconds / 31536000);
            if (interval > 1) return `${interval} years ago`;
            if (interval === 1) return '1 year ago';
            
            interval = Math.floor(seconds / 2592000);
            if (interval > 1) return `${interval} months ago`;
            if (interval === 1) return '1 month ago';
            
            interval = Math.floor(seconds / 86400);
            if (interval > 1) return `${interval} days ago`;
            if (interval === 1) return 'yesterday';
            
            interval = Math.floor(seconds / 3600);
            if (interval > 1) return `${interval} hours ago`;
            if (interval === 1) return '1 hour ago';
            
            interval = Math.floor(seconds / 60);
            if (interval > 1) return `${interval} minutes ago`;
            if (interval === 1) return '1 minute ago';
            
            return 'just now';
        } catch (e) {
            return 'recently';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.categoriesHandler = new CategoriesHandler();
});
