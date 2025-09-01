// news-data-integration.js

class NewsDataIntegration {
    constructor() {
        this.newsData = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwIDAgODAwIDQwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YzZjRmNiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9Ii85Y2E3YmMiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBpbWFnZSBhdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPg==';
    }

    async initialize() {
        try {
            const response = await fetch('/data/news.json');
            this.newsData = await response.json();
            this.setupEventListeners();
            this.renderNews();
        } catch (error) {
            console.error('Error loading news data:', error);
        }
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.querySelector('input[placeholder="Search news..."]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                this.renderNews();
            });
        }

        // Category links
        document.querySelectorAll('a[data-category]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.currentCategory = e.target.dataset.category;
                this.renderNews();
            });
        });

        // Theme toggle
        const themeToggle = document.querySelector('button i.material-icons');
        if (themeToggle) {
            themeToggle.parentElement.addEventListener('click', () => {
                document.body.classList.toggle('dark');
            });
        }
    }

    filterNews() {
        return this.newsData.filter(article => {
            const matchesCategory = this.currentCategory === 'all' || article.category === this.currentCategory;
            const matchesSearch = !this.searchQuery || 
                article.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                article.description.toLowerCase().includes(this.searchQuery.toLowerCase());
            return matchesCategory && matchesSearch;
        });
    }

    renderNews() {
        if (this.newsData.length === 0) return;
        
        // Render featured news (first article)
        this.renderFeaturedNews();
        
        // Render sidebar news (next 3 articles)
        this.renderSidebarNews();
        
        // Render news grid (remaining articles)
        this.renderNewsGrid();
    }
    
    renderFeaturedNews() {
        const featuredContainer = document.querySelector('#featured-news');
        if (!featuredContainer) return;
        
        const featuredArticle = this.newsData[0];
        if (!featuredArticle) return;
        
        const publishedDate = new Date(featuredArticle.publishedAt);
        const timeAgo = this.formatTimeAgo(publishedDate);
        
        featuredContainer.innerHTML = `
            <div class="w-full h-[500px] bg-center bg-no-repeat bg-cover relative" style="background-image: url('${featuredArticle.urlToImage || this.placeholderImage}'); background-color: #f3f4f6;" onerror="this.style.backgroundImage='url(${this.placeholderImage})';">
                <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-8">
                    <div class="max-w-3xl mx-auto">
                        <h2 class="text-3xl md:text-4xl font-bold text-white leading-tight mb-4">
                            <a href="${featuredArticle.url}" target="_blank" class="hover:underline">
                                ${featuredArticle.title}
                            </a>
                        </h2>
                        <p class="text-gray-300 text-lg mb-4 line-clamp-2">${featuredArticle.description || ''}</p>
                        <div class="flex items-center text-gray-300">
                            <span>${featuredArticle.source.name}</span>
                            <span class="mx-2">·</span>
                            <span>${timeAgo}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderSidebarNews() {
        const sidebarContainer = document.querySelector('#news-sidebar');
        if (!sidebarContainer) return;
        
        // Get next 3 articles after the featured one
        const sidebarArticles = this.newsData.slice(1, 4);
        
        const sidebarHTML = sidebarArticles.map(article => {
            const publishedDate = new Date(article.publishedAt);
            const timeAgo = this.formatTimeAgo(publishedDate);
            
            return `
                <div class="flex items-start gap-4">
                    <div class="w-24 h-24 bg-center bg-no-repeat bg-cover rounded-md flex-shrink-0" 
                         style="background-image: url('${article.urlToImage || this.placeholderImage}'); background-color: #f3f4f6;"
                         onerror="this.style.backgroundImage='url(${this.placeholderImage})';"></div>
                    <div>
                        <h3 class="font-bold leading-tight">
                            <a href="${article.url}" target="_blank" class="hover:text-[var(--primary-color)] hover:underline">
                                ${article.title}
                            </a>
                        </h3>
                        <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
                            By ${article.source.name} · ${timeAgo}
                        </p>
                    </div>
                </div>
            `;
        }).join('');
        
        sidebarContainer.innerHTML = sidebarHTML;
    }
    
    renderNewsGrid() {
        const newsGrid = document.querySelector('#news-grid');
        if (!newsGrid) return;
        
        // Get all articles except the first 4 (featured + sidebar)
        const gridArticles = this.newsData.slice(4);
        
        const newsHTML = gridArticles.map(article => {
            const publishedDate = new Date(article.publishedAt);
            const timeAgo = this.formatTimeAgo(publishedDate);
            
            return `
                <div class="bg-white dark:bg-gray-800 rounded-md shadow-md overflow-hidden flex flex-col">
                    <div class="w-full h-40 bg-center bg-no-repeat bg-cover" 
                         style="background-image: url('${article.urlToImage || this.placeholderImage}'); background-color: #f3f4f6;"
                         onerror="this.style.backgroundImage='url(${this.placeholderImage})';"></div>
                    <div class="p-4 flex flex-col flex-grow">
                        <h3 class="font-bold leading-tight flex-grow line-clamp-2">
                            <a href="${article.url}" target="_blank" class="hover:text-[var(--primary-color)]">
                                ${article.title}
                            </a>
                        </h3>
                        <p class="text-gray-600 dark:text-gray-400 text-sm mt-2 line-clamp-2">
                            ${article.description || ''}
                        </p>
                        <div class="mt-4 flex justify-between items-center">
                            <p class="text-gray-500 dark:text-gray-400 text-xs">
                                By ${article.source.name} · ${timeAgo}
                            </p>
                            <a href="${article.url}" target="_blank" class="text-[var(--primary-color)] hover:underline text-sm font-medium flex items-center">
                                Read <i class="material-icons text-sm ml-1">open_in_new</i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        newsGrid.innerHTML = newsHTML;
    }
    
    formatTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);
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
    }

    renderCategories() {
        const categoriesContainer = document.querySelector('#categories-grid');
        if (!categoriesContainer) return;

        const categories = [...new Set(this.newsData.map(article => article.category))];
        const categoryCounts = categories.reduce((acc, category) => {
            acc[category] = this.newsData.filter(article => article.category === category).length;
            return acc;
        }, {});

        const categoriesHTML = categories.map(category => `
            <a href="#" data-category="${category}" 
               class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">${
                    category.charAt(0).toUpperCase() + category.slice(1)
                }</h3>
                <p class="mt-2 text-gray-600 dark:text-gray-300">${categoryCounts[category]} articles</p>
            </a>
        `).join('');

        categoriesContainer.innerHTML = categoriesHTML;
    }

    renderArticle(articleId) {
        const article = this.newsData.find(a => a.url === decodeURIComponent(articleId));
        if (!article) return;

        const articleContainer = document.querySelector('#article-content');
        if (!articleContainer) return;

        articleContainer.innerHTML = `
            <article class="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                ${article.urlToImage ? `
                    <img src="${article.urlToImage}" 
                         alt="${article.title}"
                         class="w-full h-96 object-cover"
                         onerror="this.onerror=null; this.src='/images/placeholder.jpg';"
                    />
                ` : ''}
                <div class="p-8">
                    <span class="text-[var(--primary-color)] text-sm font-medium">${article.category}</span>
                    <h1 class="mt-4 text-3xl font-bold">${article.title}</h1>
                    <div class="mt-4 flex items-center text-gray-500 dark:text-gray-400">
                        <span>${article.source.name}</span>
                        <span class="mx-2">·</span>
                        <span>${new Date(article.publishedAt).toLocaleDateString()}</span>
                        ${article.author ? `
                            <span class="mx-2">·</span>
                            <span>${article.author}</span>
                        ` : ''}
                    </div>
                    <div class="mt-8 prose dark:prose-invert max-w-none">
                        <p class="text-lg">${article.description || ''}</p>
                        <p class="mt-4">${article.content || ''}</p>
                    </div>
                    <div class="mt-8">
                        <a href="${article.url}" 
                           target="_blank"
                           class="inline-flex items-center px-6 py-3 bg-[var(--primary-color)] text-white rounded-md hover:bg-opacity-90">
                            Read Full Article
                            <svg class="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                            </svg>
                        </a>
                    </div>
                </div>
            </article>
        `;
    }
}
