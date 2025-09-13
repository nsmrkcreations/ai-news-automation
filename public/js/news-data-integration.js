// news-data-integration.js

class NewsDataIntegration {
    constructor() {
        this.newsData = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwIDAgODAwIDQwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YzZjRmNiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9Ii85Y2E3YmMiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBpbWFnZSBhdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPg==';

        // Make this instance globally available
        window.newsDataIntegration = this;
    }

    async initialize() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.newsData = await response.json();

            // Ensure articles are sorted by date (latest first)
            this.newsData.sort((a, b) => {
                const dateA = new Date(a.publishedAt || 0);
                const dateB = new Date(b.publishedAt || 0);
                return dateB - dateA;
            });

            this.setupEventListeners();
            this.renderNews();

            console.log(`News integration initialized with ${this.newsData.length} articles`);
        } catch (error) {
            console.error('Error loading news data:', error);
            this.showError('Failed to load news articles. Please try again later.');
        }
    }

    showError(message) {
        const containers = ['#featured-news', '#news-sidebar', '#news-grid'];
        containers.forEach(selector => {
            const container = document.querySelector(selector);
            if (container) {
                container.innerHTML = `
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
        });
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

        // Extract image URL from content if available, or use placeholder
        const imageUrl = this.extractImageUrl(featuredArticle) || this.placeholderImage;
        const publishedDate = new Date(featuredArticle.publishedAt);
        const timeAgo = this.formatTimeAgo(publishedDate);
        const sourceName = featuredArticle.source?.name || 'Unknown Source';

        // Clean up HTML from description
        const cleanDescription = this.stripHtml(featuredArticle.description || '').substring(0, 200) + '...';

        // Check if article is AI enhanced
        const isAIEnhanced = featuredArticle.aiEnhanced || featuredArticle.aiBadge;
        const aiIndicator = isAIEnhanced ? `
            <div class="inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white text-sm font-medium mb-2">
                <i class="material-icons text-sm mr-1">smart_toy</i>
                AI Enhanced
            </div>
        ` : '';

        featuredContainer.innerHTML = `
            <div class="flex flex-col md:flex-row bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-lg h-auto md:h-[400px]">
                <!-- Image Section - Smaller, 35% on desktop -->
                <div class="w-full md:w-2/5 h-48 md:h-full bg-center bg-cover relative" style="background-image: url('${imageUrl || this.placeholderImage}'); background-color: #f3f4f6;" onerror="this.style.backgroundImage='url(${this.placeholderImage})';">
                    <div class="absolute inset-0 bg-black/10"></div>
                    ${isAIEnhanced ? `
                        <div class="absolute top-3 left-3">
                            <div class="flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white text-xs font-medium">
                                <i class="material-icons text-xs mr-1">smart_toy</i>
                                AI
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <!-- Content Section - Larger, 65% on desktop -->
                <div class="w-full md:w-3/5 p-4 md:p-8 flex flex-col justify-center">
                    ${aiIndicator}
                    <div class="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-3">
                        <span class="capitalize px-2 py-1 bg-[var(--primary-color)] text-white rounded-full text-xs">${featuredArticle.category || 'General'}</span>
                        <span class="mx-3">•</span>
                        <span>${sourceName}</span>
                        <span class="mx-3">•</span>
                        <span>${timeAgo}</span>
                    </div>
                    <h2 class="text-lg md:text-3xl font-bold text-gray-900 dark:text-gray-100 leading-tight mb-4">
                        <a href="article.html?id=${encodeURIComponent(featuredArticle.url)}" class="hover:text-[var(--primary-color)] transition-colors">
                            ${featuredArticle.title}
                        </a>
                    </h2>
                    <p class="text-gray-600 dark:text-gray-300 text-sm md:text-lg mb-6 line-clamp-3 md:line-clamp-4">${cleanDescription}</p>
                    <a href="article.html?id=${encodeURIComponent(featuredArticle.url)}" class="inline-flex items-center px-4 md:px-6 py-2 md:py-3 bg-[var(--primary-color)] text-white rounded-md hover:opacity-90 transition-opacity font-medium text-sm md:text-base">
                        Read Full Article
                        <i class="material-icons ml-2 text-lg">arrow_forward</i>
                    </a>
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
            if (!article) return '';

            const imageUrl = this.extractImageUrl(article) || this.placeholderImage;
            const publishedDate = new Date(article.publishedAt);
            const timeAgo = this.formatTimeAgo(publishedDate);
            const sourceName = article.source?.name || 'Unknown Source';
            const cleanTitle = this.stripHtml(article.title || '').substring(0, 80) + (article.title?.length > 80 ? '...' : '');

            return `
                <div class="flex items-start gap-4 mb-4 hover:bg-gray-50 dark:hover:bg-gray-800 p-2 rounded-lg transition-colors">
                    <div class="w-24 h-24 bg-center bg-no-repeat bg-cover rounded-md flex-shrink-0" 
                         style="background-image: url('${imageUrl || this.placeholderImage}'); background-color: #f3f4f6;"
                         onerror="console.error('Error loading image:', this.style.backgroundImage); this.style.backgroundImage='url(${this.placeholderImage})';"></div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-bold leading-tight text-sm md:text-base">
                            <a href="article.html?id=${encodeURIComponent(article.url)}" class="hover:text-[var(--primary-color)] hover:underline">
                                ${cleanTitle}
                            </a>
                        </h3>
                        <p class="text-gray-500 dark:text-gray-400 text-xs mt-1">
                            ${sourceName} · ${timeAgo}
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
            if (!article) return '';

            const imageUrl = this.extractImageUrl(article) || this.placeholderImage;
            const publishedDate = new Date(article.publishedAt);
            const timeAgo = this.formatTimeAgo(publishedDate);
            const sourceName = article.source?.name || 'Unknown Source';
            const cleanTitle = this.stripHtml(article.title || '');
            const cleanDescription = this.stripHtml(article.description || '').substring(0, 120) + (article.description?.length > 120 ? '...' : '');

            // Check if article is AI enhanced
            const isAIEnhanced = article.aiEnhanced || article.aiBadge;

            return `
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden flex flex-col hover:shadow-lg transition-shadow duration-300 h-full">
                    <!-- Smaller image section - 30% height -->
                    <div class="w-full h-32 bg-center bg-cover relative" 
                         style="background-image: url('${imageUrl || this.placeholderImage}'); background-color: #f3f4f6;"
                         onerror="this.style.backgroundImage='url(${this.placeholderImage})';">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                        ${isAIEnhanced ? `
                            <div class="absolute top-2 left-2">
                                <div class="flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white text-xs font-medium">
                                    <i class="material-icons text-xs mr-1">smart_toy</i>
                                    AI
                                </div>
                            </div>
                        ` : ''}
                        <div class="absolute top-2 right-2">
                            <span class="px-2 py-1 bg-[var(--primary-color)] text-white text-xs rounded-full">
                                ${article.category || 'General'}
                            </span>
                        </div>
                    </div>
                    
                    <!-- Larger content section - 70% height -->
                    <div class="p-4 flex flex-col flex-grow">
                        ${isAIEnhanced ? `
                            <div class="flex items-center mb-2">
                                <div class="inline-flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900 text-purple-700 dark:text-purple-300 text-xs font-medium">
                                    <i class="material-icons text-xs mr-1">smart_toy</i>
                                    AI Enhanced Content
                                </div>
                            </div>
                        ` : ''}
                        <h3 class="font-bold leading-tight text-base md:text-lg mb-3 line-clamp-2">
                            <a href="article.html?id=${encodeURIComponent(article.url)}" class="hover:text-[var(--primary-color)] transition-colors">
                                ${cleanTitle}
                            </a>
                        </h3>
                        <p class="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-4 flex-grow">
                            ${cleanDescription}
                        </p>
                        <div class="mt-auto">
                            <div class="flex justify-between items-center mb-3">
                                <p class="text-gray-500 dark:text-gray-400 text-xs">
                                    ${sourceName} · ${timeAgo}
                                </p>
                            </div>
                            <a href="article.html?id=${encodeURIComponent(article.url)}" class="inline-flex items-center text-[var(--primary-color)] hover:underline text-sm font-medium group w-full justify-center py-2 border border-[var(--primary-color)] rounded-md hover:bg-[var(--primary-color)] hover:text-white transition-colors">
                                Read Full Article
                                <i class="material-icons text-sm ml-1 transform group-hover:translate-x-1 transition-transform">arrow_forward</i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        newsGrid.innerHTML = newsHTML;
    }

    // Helper function to extract image URL from article content
    extractImageUrl(article) {
        try {
            console.log('Extracting image for article:', article.title);

            // First try to get from imageUrl if it exists and is a valid URL
            if (article.imageUrl && this.isValidUrl(article.imageUrl)) {
                console.log('Using imageUrl:', article.imageUrl);
                return article.imageUrl;
            }

            // Fall back to urlToImage if it exists and is a valid URL
            if (article.urlToImage && this.isValidUrl(article.urlToImage)) {
                console.log('Using urlToImage:', article.urlToImage);
                return article.urlToImage;
            }

            // Check for image in content
            if (article.content) {
                // Try to find an image URL in the content
                const imgMatch = article.content.match(/<img[^>]+src=["'](https?:\/\/[^"']+?\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (imgMatch && imgMatch[1]) {
                    const imgUrl = imgMatch[1].replace(/&amp;/g, '&');
                    if (this.isValidUrl(imgUrl)) {
                        console.log('Found image in content:', imgUrl);
                        return imgUrl;
                    }
                }

                // Try to find a figure with image in the content
                const figureMatch = article.content.match(/<figure[^>]*>\s*<img[^>]+src=["'](https?:\/\/[^"']+?\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (figureMatch && figureMatch[1]) {
                    const imgUrl = figureMatch[1].replace(/&amp;/g, '&');
                    if (this.isValidUrl(imgUrl)) {
                        console.log('Found image in figure:', imgUrl);
                        return imgUrl;
                    }
                }
            }

            // Check for image in description
            if (article.description) {
                const descImgMatch = article.description.match(/<img[^>]+src=["'](https?:\/\/[^"']+?\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (descImgMatch && descImgMatch[1]) {
                    const imgUrl = descImgMatch[1].replace(/&amp;/g, '&');
                    if (this.isValidUrl(imgUrl)) {
                        console.log('Found image in description:', imgUrl);
                        return imgUrl;
                    }
                }
            }

            // Try to extract from the article's URL (some news sites have predictable image URLs)
            if (article.url) {
                try {
                    const url = new URL(article.url);
                    if (url.hostname.includes('theguardian.com')) {
                        // Example: Try to get the first image from the article's metadata
                        const articleId = article.url.split('/').pop().split('?')[0];
                        if (articleId) {
                            const guardianImgUrl = `https://media.guim.co.uk/${articleId}/0_0_3000_1800/1000.jpg`;
                            console.log('Trying Guardian image URL:', guardianImgUrl);
                            return guardianImgUrl;
                        }
                    }
                } catch (e) {
                    console.log('Error generating image URL from article URL:', e);
                }
            }

            console.log('No valid image URL found, using placeholder');
            return null;
        } catch (error) {
            console.error('Error extracting image URL:', error);
            return null;
        }
    }

    // Helper function to strip HTML tags
    // Helper to validate URLs
    isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
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
            console.error('Error stripping HTML:', error);
            return String(html).replace(/<[^>]*>?/gm, '');
        }
    }

    formatTimeAgo(date) {
        if (!date || isNaN(new Date(date).getTime())) return 'recently';

        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
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
                <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">${category.charAt(0).toUpperCase() + category.slice(1)
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
