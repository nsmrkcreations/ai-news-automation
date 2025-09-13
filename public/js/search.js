class SearchHandler {
    constructor() {
        this.searchInputs = document.querySelectorAll('input[placeholder*="Search"]');
        this.newsContainer = document.getElementById('news-grid') || document.getElementById('news-container');
        this.originalNews = [];
        this.isSearching = false;
        
        if (this.searchInputs.length > 0) {
            this.initialize();
        }
    }

    async initialize() {
        try {
            // Load news data
            const response = await fetch('/data/news.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.originalNews = await response.json();
            
            // Add event listeners to all search inputs
            this.searchInputs.forEach(input => {
                // Debounced search on input
                let searchTimeout;
                input.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => this.handleSearch(e), 300);
                });
                
                // Immediate search on Enter key
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        clearTimeout(searchTimeout);
                        this.handleSearch(e);
                    }
                });
            });
            
            console.log(`Search initialized with ${this.originalNews.length} articles`);
        } catch (error) {
            console.error('Error initializing search:', error);
        }
    }

    handleSearch(event) {
        if (this.isSearching) return;
        
        const searchTerm = event.target.value.toLowerCase().trim();
        
        // Update all search inputs with the same value
        this.searchInputs.forEach(input => {
            if (input !== event.target) {
                input.value = event.target.value;
            }
        });
        
        if (searchTerm === '') {
            // If search is empty, trigger a refresh of the original display
            this.resetDisplay();
            return;
        }
        
        this.isSearching = true;
        
        // Enhanced search with multiple criteria and scoring
        const filteredNews = this.originalNews.filter(news => {
            const title = (news.title || '').toLowerCase();
            const description = (news.description || '').toLowerCase();
            const content = (news.content || '').toLowerCase();
            const category = (news.category || '').toLowerCase();
            const source = (news.source?.name || '').toLowerCase();
            
            return title.includes(searchTerm) || 
                   description.includes(searchTerm) ||
                   content.includes(searchTerm) ||
                   category.includes(searchTerm) ||
                   source.includes(searchTerm);
        }).sort((a, b) => {
            // Score articles by relevance (title matches score higher)
            const aTitle = (a.title || '').toLowerCase();
            const bTitle = (b.title || '').toLowerCase();
            const aTitleMatch = aTitle.includes(searchTerm);
            const bTitleMatch = bTitle.includes(searchTerm);
            
            if (aTitleMatch && !bTitleMatch) return -1;
            if (!aTitleMatch && bTitleMatch) return 1;
            
            // If both or neither match title, sort by date (newest first)
            const aDate = new Date(a.publishedAt || 0);
            const bDate = new Date(b.publishedAt || 0);
            return bDate - aDate;
        });
        
        this.displayNews(filteredNews, searchTerm);
        this.isSearching = false;
    }

    resetDisplay() {
        // Trigger a refresh of the original display
        if (window.newsDataIntegration) {
            window.newsDataIntegration.renderNews();
        } else if (window.categoriesHandler) {
            window.categoriesHandler.displayNewsByCategory();
        } else {
            this.displayNews(this.originalNews);
        }
    }

    displayNews(newsItems, searchTerm = '') {
        if (!this.newsContainer) return;
        
        if (newsItems.length === 0) {
            const noResultsHTML = `
                <div class="col-span-full text-center py-12">
                    <i class="material-icons text-5xl text-gray-400 mb-4">search_off</i>
                    <h3 class="text-xl font-medium text-gray-600 dark:text-gray-300">No results found</h3>
                    <p class="text-gray-500 mt-2">
                        ${searchTerm ? `No articles found for "${searchTerm}". ` : ''}
                        Try different keywords or check back later for updates.
                    </p>
                </div>
            `;
            
            // Handle different container types
            if (this.newsContainer.id === 'news-container') {
                this.newsContainer.innerHTML = noResultsHTML;
            } else {
                this.newsContainer.innerHTML = noResultsHTML;
            }
            return;
        }
        
        // Clear existing news
        this.newsContainer.innerHTML = '';
        
        // Add search results header if searching
        if (searchTerm) {
            const headerHTML = `
                <div class="col-span-full mb-6">
                    <div class="flex items-center justify-between">
                        <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">
                            Search Results for "${searchTerm}" (${newsItems.length} articles)
                        </h2>
                        <button onclick="window.searchHandler.clearSearch()" 
                                class="text-sm text-[var(--primary-color)] hover:underline">
                            Clear Search
                        </button>
                    </div>
                </div>
            `;
            
            if (this.newsContainer.id === 'news-container') {
                this.newsContainer.innerHTML = headerHTML;
                // For categories page, group by category
                this.displaySearchResultsByCategory(newsItems, searchTerm);
            } else {
                this.newsContainer.innerHTML = headerHTML;
                // For main page, display as grid
                newsItems.forEach(item => {
                    const newsElement = this.createNewsElement(item, searchTerm);
                    this.newsContainer.appendChild(newsElement);
                });
            }
        } else {
            // Regular display without search
            if (this.newsContainer.id === 'news-container') {
                // Categories page
                this.displayNewsByCategory(newsItems);
            } else {
                // Main page grid
                newsItems.forEach(item => {
                    const newsElement = this.createNewsElement(item);
                    this.newsContainer.appendChild(newsElement);
                });
            }
        }
    }

    displaySearchResultsByCategory(newsItems, searchTerm) {
        const newsByCategory = {};
        
        // Group search results by category
        newsItems.forEach(article => {
            const category = article.category || 'General';
            if (!newsByCategory[category]) newsByCategory[category] = [];
            newsByCategory[category].push(article);
        });

        // Generate HTML for each category
        for (const [category, articles] of Object.entries(newsByCategory)) {
            const categorySection = document.createElement('div');
            categorySection.className = 'mb-8';
            categorySection.innerHTML = `
                <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">
                    ${category} (${articles.length})
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${articles.map(article => this.createCategoryArticleCard(article, searchTerm)).join('')}
                </div>
            `;
            this.newsContainer.appendChild(categorySection);
        }
    }

    displayNewsByCategory(newsItems) {
        const newsByCategory = {};
        
        // Group news by category
        newsItems.forEach(article => {
            const category = article.category || 'General';
            if (!newsByCategory[category]) newsByCategory[category] = [];
            newsByCategory[category].push(article);
        });

        // Generate HTML for each category
        for (const [category, articles] of Object.entries(newsByCategory)) {
            const categorySection = document.createElement('div');
            categorySection.className = 'mb-12';
            categorySection.innerHTML = `
                <h2 class="text-2xl font-bold mb-6 pb-2 border-b border-gray-200 dark:border-gray-700">
                    ${category}
                </h2>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    ${articles.slice(0, 6).map(article => this.createCategoryArticleCard(article)).join('')}
                </div>
            `;
            this.newsContainer.appendChild(categorySection);
        }
    }

    clearSearch() {
        this.searchInputs.forEach(input => {
            input.value = '';
        });
        this.resetDisplay();
    }

    createNewsElement(news, searchTerm = '') {
        const article = document.createElement('article');
        article.className = 'bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300';
        
        // Extract image URL
        const imageUrl = this.extractImageUrl(news);
        const image = imageUrl ? 
            `<img src="${imageUrl}" alt="${news.title}" class="w-full h-48 object-cover" onerror="this.onerror=null; this.src='${this.getPlaceholderImage()}';">` :
            `<div class="w-full h-48 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <i class="material-icons text-4xl text-gray-400">image_not_supported</i>
            </div>`;
        
        // Highlight search terms in title and description
        const highlightedTitle = searchTerm ? this.highlightText(news.title, searchTerm) : news.title;
        const highlightedDescription = searchTerm ? this.highlightText(news.description || '', searchTerm) : (news.description || '');
        
        article.innerHTML = `
            ${image}
            <div class="p-4">
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <span class="capitalize">${news.category || 'General'}</span>
                    <span class="mx-2">•</span>
                    <span>${this.formatDate(news.publishedAt)}</span>
                    ${news.source?.name ? `<span class="mx-2">•</span><span>${news.source.name}</span>` : ''}
                </div>
                <h3 class="text-lg font-semibold mb-2 line-clamp-2">${highlightedTitle}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-3">${highlightedDescription}</p>
                <a href="${news.url || '#'}" class="mt-4 inline-flex items-center text-[var(--primary-color)] hover:underline" target="_blank" rel="noopener noreferrer">
                    Read more
                    <i class="material-icons ml-1 text-sm">arrow_forward</i>
                </a>
            </div>
        `;
        
        return article;
    }

    createCategoryArticleCard(article, searchTerm = '') {
        const imageUrl = this.extractImageUrl(article);
        const date = this.formatDate(article.publishedAt);
        
        // Highlight search terms
        const highlightedTitle = searchTerm ? this.highlightText(article.title, searchTerm) : article.title;
        const highlightedDescription = searchTerm ? this.highlightText(article.description || '', searchTerm) : (article.description || '');
        
        return `
            <div class="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                <a href="${article.url}" target="_blank" rel="noopener">
                    <div class="h-48 bg-cover bg-center" style="background-image: url('${imageUrl || this.getPlaceholderImage()}')"></div>
                </a>
                <div class="p-4">
                    <a href="${article.url}" target="_blank" rel="noopener" class="hover:text-[var(--primary-color)]">
                        <h3 class="text-lg font-bold mb-2 line-clamp-2">${highlightedTitle}</h3>
                    </a>
                    ${date ? `<p class="text-sm text-gray-500 dark:text-gray-400 mb-2">${date}</p>` : ''}
                    <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-3">
                        ${highlightedDescription}
                    </p>
                </div>
            </div>
        `;
    }

    extractImageUrl(article) {
        if (article.imageUrl && this.isValidUrl(article.imageUrl)) {
            return article.imageUrl;
        }
        if (article.urlToImage && this.isValidUrl(article.urlToImage)) {
            return article.urlToImage;
        }
        return null;
    }

    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    getPlaceholderImage() {
        return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwIDAgODAwIDQwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YzZjRmNiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9Ii85Y2E3YmMiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBpbWFnZSBhdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPg==';
    }

    highlightText(text, searchTerm) {
        if (!text || !searchTerm) return text;
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-600">$1</mark>');
    }

    formatDate(dateString) {
        if (!dateString) return '';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return '';
        }
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.searchHandler = new SearchHandler();
});
