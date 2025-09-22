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
            // Try new enhanced format first
            let response = await fetch('/data/news_latest.json');
            if (!response.ok) {
                // Fallback to old format
                response = await fetch('/data/news.json');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
            }

            const data = await response.json();

            // Handle both old and new formats
            if (data.articles) {
                // New enhanced format
                this.newsData = data.articles.map(article => this.normalizeEnhancedArticle(article));
                console.log(`Loaded enhanced format with ${this.newsData.length} articles`);
                console.log('Enhanced data metadata:', {
                    generated_at: data.generated_at,
                    total_articles: data.total_articles,
                    categories: data.categories,
                    sources: data.sources
                });
            } else if (Array.isArray(data)) {
                // Old format
                this.newsData = data;
                console.log(`Loaded legacy format with ${this.newsData.length} articles`);
            } else {
                throw new Error('Invalid data format');
            }

            // Ensure articles are sorted by date (latest first)
            this.newsData.sort((a, b) => {
                const dateA = new Date(a.publishedAt || a.published_at || 0);
                const dateB = new Date(b.publishedAt || b.published_at || 0);
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

    normalizeEnhancedArticle(article) {
        // Convert enhanced format to legacy format for compatibility
        return {
            id: article.id,
            title: article.title,
            description: article.summary || article.excerpt || '',
            content: article.content_snippet || article.excerpt || '',
            publishedAt: article.published_at || article.publishedAt,
            source: {
                name: article.source || 'Unknown Source'
            },
            author: article.author || null,
            url: article.source_url || article.url,
            imageUrl: article.media && article.media[0] ? article.media[0].url : null,
            urlToImage: article.media && article.media[0] ? article.media[0].url : null,
            category: article.category || 'general',
            aiEnhanced: article.ai_enhanced || false,
            aiBadge: article.ai_enhanced || false,
            keywords: article.keywords || [],
            readingTime: article.reading_time_minutes || 1,
            fetchedAt: article.fetched_at || new Date().toISOString(),
            // Enhanced fields
            summary: article.summary || '',
            aiInsights: article.ai_insights || '',
            language: article.language || 'en'
        };
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
        // Search functionality - handle both desktop and mobile search inputs
        const searchInputs = document.querySelectorAll('input[placeholder="Search news..."]');
        searchInputs.forEach(searchInput => {
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.searchQuery = e.target.value;
                    this.renderNews();
                });
            }
        });

        // Category links
        document.querySelectorAll('a[data-category]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.currentCategory = e.target.dataset.category;
                this.renderNews();
            });
        });
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
            <div class="inline-flex items-center px-3 py-1 rounded bg-purple-600 text-white text-sm font-medium mb-2">
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
                            <span class="px-2 py-1 bg-purple-600 text-white text-xs rounded flex items-center">
                                <i class="material-icons text-xs mr-1">smart_toy</i>
                                AI
                            </span>
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
                        <a href="#article" data-section="article" data-article-url="${encodeURIComponent(featuredArticle.url)}" class="article-link hover:text-[var(--primary-color)] transition-colors">
                            ${featuredArticle.title}
                        </a>
                    </h2>
                    <p class="text-gray-600 dark:text-gray-300 text-sm md:text-lg mb-6 line-clamp-3 md:line-clamp-4">${cleanDescription}</p>
                    <a href="#article" data-section="article" data-article-url="${encodeURIComponent(featuredArticle.url)}" class="article-link inline-flex items-center px-6 py-3 bg-[var(--primary-color)] text-white rounded-md font-medium hover:bg-[var(--primary-color)]/90 transition-colors">
                        Read Article
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
                            <a href="#article" data-section="article" data-article-url="${encodeURIComponent(article.url)}" class="article-link hover:text-[var(--primary-color)] hover:underline">
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
                <article class="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden h-full flex flex-col">
                    <!-- Clean image section with fade -->
                    <div class="relative h-40 overflow-hidden">
                        <img src="${imageUrl || this.placeholderImage}" 
                             alt="${cleanTitle}"
                             class="w-full h-full object-cover"
                             onerror="this.src='${this.placeholderImage}';">
                        
                        <!-- Subtle bottom fade -->
                        <div class="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
                        
                        <!-- Simple badges -->
                        <div class="absolute top-2 left-2">
                            <span class="px-2 py-1 bg-[var(--primary-color)] text-white text-xs rounded">
                                ${article.category || 'General'}
                            </span>
                        </div>
                        
                        ${isAIEnhanced ? `
                            <div class="absolute top-2 right-2">
                                <span class="px-2 py-1 bg-purple-600 text-white text-xs rounded flex items-center">
                                    <i class="material-icons text-xs mr-1">smart_toy</i>
                                    AI
                                </span>
                            </div>
                        ` : ''}
                    </div>
                    
                    <!-- Clean content section -->
                    <div class="p-4 flex flex-col flex-grow">
                        <!-- Title -->
                        <h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base leading-tight mb-2 line-clamp-2">
                            <a href="#article" data-section="article" data-article-url="${encodeURIComponent(article.url)}" class="article-link hover:text-[var(--primary-color)] transition-colors">
                                ${cleanTitle}
                            </a>
                        </h3>
                        
                        <!-- Description -->
                        <p class="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-3 flex-grow">
                            ${cleanDescription}
                        </p>
                        
                        <!-- Source and time -->
                        <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-3">
                            <span>${sourceName}</span>
                            <span>${timeAgo}</span>
                        </div>
                        
                        <!-- Simple read link -->
                        <a href="#article" data-section="article" data-article-url="${encodeURIComponent(article.url)}" class="article-link text-[var(--primary-color)] text-sm font-medium hover:underline">
                            Read more →
                        </a>
                    </div>
                </article>
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
        const newsContainer = document.querySelector('#news-container');
        if (!newsContainer) return;

        // Initialize category filtering
        this.initCategoryFiltering();
        
        // Render all articles by default
        this.renderCategoryArticles('all');
    }
    
    initCategoryFiltering() {
        const categoryFilters = document.querySelectorAll('.category-filter');
        
        categoryFilters.forEach(filter => {
            filter.addEventListener('click', (e) => {
                const category = e.target.getAttribute('data-category');
                
                // Update active filter
                categoryFilters.forEach(f => {
                    f.classList.remove('active');
                    f.classList.add('bg-white', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
                    f.classList.remove('bg-[var(--primary-color)]', 'text-white');
                });
                
                e.target.classList.add('active');
                e.target.classList.remove('bg-white', 'dark:bg-gray-700', 'text-gray-700', 'dark:text-gray-300');
                e.target.classList.add('bg-[var(--primary-color)]', 'text-white');
                
                // Render articles for selected category
                this.renderCategoryArticles(category);
            });
        });
    }
    
    renderCategoryArticles(selectedCategory) {
        const newsContainer = document.querySelector('#news-container');
        if (!newsContainer) return;
        
        // Filter articles by category
        let filteredArticles = this.newsData;
        if (selectedCategory !== 'all') {
            filteredArticles = this.newsData.filter(article => 
                article.category === selectedCategory
            );
        }
        
        // Group articles by category for display
        const categories = [...new Set(filteredArticles.map(article => article.category))];
        
        const categoryHTML = categories.map(category => {
            const categoryArticles = filteredArticles.filter(article => article.category === category);
            
            return `
                <div class="category-section">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-xl md:text-2xl font-bold text-gray-900 dark:text-gray-100 capitalize">
                            ${category} News
                        </h2>
                        <span class="text-sm text-gray-500 dark:text-gray-400">
                            ${categoryArticles.length} articles
                        </span>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${categoryArticles.slice(0, 6).map(article => this.renderCategoryArticle(article)).join('')}
                    </div>
                </div>
            `;
        }).join('');
        
        newsContainer.innerHTML = categoryHTML;
    }
    
    renderCategoryArticle(article) {
        const imageUrl = this.extractImageUrl(article) || this.placeholderImage;
        const publishedDate = new Date(article.publishedAt);
        const timeAgo = this.formatTimeAgo(publishedDate);
        const sourceName = article.source?.name || 'Unknown Source';
        const cleanTitle = this.stripHtml(article.title || '');
        const cleanDescription = this.stripHtml(article.description || '').substring(0, 120) + '...';
        const isAIEnhanced = article.aiEnhanced || article.aiBadge;
        
        return `
            <article class="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden h-full flex flex-col">
                <div class="relative h-40 overflow-hidden">
                    <img src="${imageUrl}" 
                         alt="${cleanTitle}"
                         class="w-full h-full object-cover"
                         onerror="this.src='${this.placeholderImage}';">
                    
                    <div class="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent"></div>
                    
                    <div class="absolute top-2 left-2">
                        <span class="px-2 py-1 bg-[var(--primary-color)] text-white text-xs rounded">
                            ${article.category || 'General'}
                        </span>
                    </div>
                    
                    ${isAIEnhanced ? `
                        <div class="absolute top-2 right-2">
                            <span class="px-2 py-1 bg-purple-600 text-white text-xs rounded flex items-center">
                                <i class="material-icons text-xs mr-1">smart_toy</i>
                                AI
                            </span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="p-4 flex flex-col flex-grow">
                    <h3 class="font-semibold text-gray-900 dark:text-gray-100 text-base leading-tight mb-2 line-clamp-2">
                        <a href="#article" data-section="article" data-article-url="${encodeURIComponent(article.url)}" class="article-link hover:text-[var(--primary-color)] transition-colors">
                            ${cleanTitle}
                        </a>
                    </h3>
                    
                    <p class="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-3 flex-grow">
                        ${cleanDescription}
                    </p>
                    
                    <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-3">
                        <span>${sourceName}</span>
                        <span>${timeAgo}</span>
                    </div>
                    
                    <a href="#article" data-section="article" data-article-url="${encodeURIComponent(article.url)}" class="article-link text-[var(--primary-color)] text-sm font-medium hover:underline">
                        Read more →
                    </a>
                </div>
            </article>
        `;
    }

    renderArticle(articleId) {
        const article = this.newsData.find(a => a.url === decodeURIComponent(articleId));
        if (!article) {
            this.showArticleError();
            return;
        }

        const articleContainer = document.querySelector('#article-content');
        if (!articleContainer) return;

        // Extract image URL
        const imageUrl = this.extractImageUrl(article);
        const publishedDate = new Date(article.publishedAt);
        const sourceName = article.source?.name || 'Unknown Source';

        // AI-Enhanced Content Processing
        const aiProcessedContent = this.generateAIContent(article);
        const readingTime = this.calculateReadingTime(aiProcessedContent.fullContent);

        document.title = `${article.title} - NewSurgeAI`;

        articleContainer.innerHTML = `
            <article class="max-w-4xl mx-auto">
                <!-- Breadcrumb -->
                <nav class="mb-6">
                    <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <a href="#home" data-section="home" class="nav-link hover:text-[var(--primary-color)]">Home</a>
                        <i class="material-icons mx-2 text-sm">chevron_right</i>
                        <a href="#categories" data-section="categories" class="nav-link hover:text-[var(--primary-color)] capitalize">${article.category || 'General'}</a>
                        <i class="material-icons mx-2 text-sm">chevron_right</i>
                        <span>Article</span>
                    </div>
                </nav>

                <!-- AI Enhancement Badge -->
                <div class="mb-6">
                    <div class="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium shadow-lg">
                        <i class="material-icons mr-2">smart_toy</i>
                        AI Enhanced & Optimized for Reading
                    </div>
                </div>

                <!-- Article Header -->
                <header class="mb-8">
                    <div class="flex flex-wrap items-center gap-3 mb-4">
                        <span class="px-3 py-1 bg-[var(--primary-color)] text-white text-sm rounded-full capitalize">${article.category || 'General'}</span>
                        <span class="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-full">
                            ${readingTime} min read
                        </span>
                        <span class="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-sm rounded-full">
                            ${aiProcessedContent.wordCount} words
                        </span>
                    </div>
                    
                    <h1 class="text-2xl md:text-4xl lg:text-5xl font-bold leading-tight mb-6 text-gray-900 dark:text-gray-100">
                        ${article.title}
                    </h1>
                    
                    <div class="flex flex-wrap items-center text-gray-600 dark:text-gray-400 text-sm mb-6">
                        <span class="font-medium">${sourceName}</span>
                        <span class="mx-3">•</span>
                        <span>${publishedDate.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        })}</span>
                        ${article.author ? `
                            <span class="mx-3">•</span>
                            <span>By ${article.author}</span>
                        ` : ''}
                    </div>
                </header>

                <!-- AI Summary Section -->
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 rounded-xl mb-8 border border-blue-200 dark:border-blue-800">
                    <h2 class="flex items-center text-xl font-bold mb-4 text-blue-700 dark:text-blue-300">
                        <i class="material-icons mr-2">auto_awesome</i>
                        AI Summary
                    </h2>
                    <p class="text-gray-700 dark:text-gray-300 text-lg leading-relaxed">${aiProcessedContent.summary}</p>
                </div>

                <!-- Key Points Section -->
                ${aiProcessedContent.keyPoints.length > 0 ? `
                    <div class="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl mb-8">
                        <h2 class="flex items-center text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
                            <i class="material-icons mr-2">key</i>
                            Key Points
                        </h2>
                        <ul class="space-y-3">
                            ${aiProcessedContent.keyPoints.map(point => `
                                <li class="flex items-start">
                                    <i class="material-icons text-[var(--primary-color)] mr-3 mt-1 text-sm">arrow_right</i>
                                    <span class="text-gray-700 dark:text-gray-300">${point}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                <!-- Article Image -->
                ${imageUrl ? `
                    <div class="mb-8">
                        <img src="${imageUrl}" alt="${article.title}" 
                             class="w-full h-48 md:h-64 object-cover rounded-xl shadow-lg"
                             onerror="this.style.display='none';">
                    </div>
                ` : ''}

                <!-- Main Article Content -->
                <div class="prose prose-lg dark:prose-invert max-w-none">
                    <div class="text-gray-700 dark:text-gray-300 leading-relaxed space-y-6">
                        ${aiProcessedContent.formattedContent}
                    </div>
                </div>

                <!-- AI Analysis Section -->
                ${aiProcessedContent.analysis ? `
                    <div class="mt-8 bg-purple-50 dark:bg-purple-900/20 p-6 rounded-xl border border-purple-200 dark:border-purple-800">
                        <h2 class="flex items-center text-xl font-bold mb-4 text-purple-700 dark:text-purple-300">
                            <i class="material-icons mr-2">psychology</i>
                            AI Analysis
                        </h2>
                        <p class="text-gray-700 dark:text-gray-300 leading-relaxed">${aiProcessedContent.analysis}</p>
                    </div>
                ` : ''}

                <!-- Original Source Section -->
                <div class="mt-8 p-6 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-xl border">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Read the Original Article</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Get the full story from the original source</p>
                        </div>
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer" 
                           class="inline-flex items-center px-6 py-3 bg-[var(--primary-color)] text-white rounded-lg hover:opacity-90 transition-opacity font-medium shadow-lg">
                            <i class="material-icons mr-2">open_in_new</i>
                            Original Source
                        </a>
                    </div>
                </div>

                <!-- Share Section -->
                <div class="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
                    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Share this AI-enhanced article:</span>
                        <div class="flex gap-3">
                            <button onclick="shareArticle('twitter')" class="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                <i class="material-icons mr-2 text-sm">share</i>
                                Twitter
                            </button>
                            <button onclick="shareArticle('facebook')" class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                <i class="material-icons mr-2 text-sm">share</i>
                                Facebook
                            </button>
                            <button onclick="copyArticleLink()" class="flex items-center px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors">
                                <i class="material-icons mr-2 text-sm">link</i>
                                Copy Link
                            </button>
                        </div>
                    </div>
                </div>
            </article>
        `;dingTime(aiProcessedContent.fullContent);

        document.title = `${article.title} - NewSurgeAI`;

        articleContainer.innerHTML = `
            <article class="max-w-4xl mx-auto">
                <!-- Breadcrumb -->
                <nav class="mb-6">
                    <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <a href="#home" data-section="home" class="nav-link hover:text-[var(--primary-color)]">Home</a>
                        <i class="material-icons mx-2 text-sm">chevron_right</i>
                        <a href="#categories" data-section="categories" class="nav-link hover:text-[var(--primary-color)] capitalize">${article.category || 'General'}</a>
                        <i class="material-icons mx-2 text-sm">chevron_right</i>
                        <span>Article</span>
                    </div>
                </nav>

                <!-- AI Enhancement Badge -->
                <div class="mb-6">
                    <div class="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium shadow-lg">
                        <i class="material-icons mr-2">smart_toy</i>
                        AI Enhanced & Optimized for Reading
                    </div>
                </div>

                <!-- Article Header -->
                <header class="mb-8">
                    <div class="flex flex-wrap items-center gap-3 mb-4">
                        <span class="px-3 py-1 bg-[var(--primary-color)] text-white text-sm rounded-full capitalize">${article.category || 'General'}</span>
                        <span class="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm rounded-full">
                            ${readingTime} min read
                        </span>
                        <span class="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 text-sm rounded-full">
                            ${aiProcessedContent.wordCount} words
                        </span>
                    </div>
                    
                    <h1 class="text-2xl md:text-4xl lg:text-5xl font-bold leading-tight mb-6 text-gray-900 dark:text-gray-100">
                        ${article.title}
                    </h1>
                    
                    <div class="flex flex-wrap items-center text-gray-600 dark:text-gray-400 text-sm mb-6">
                        <span class="font-medium">${sourceName}</span>
                        <span class="mx-3">•</span>
                        <span>${publishedDate.toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric'
                        })}</span>
                        ${article.author ? `
                            <span class="mx-3">•</span>
                            <span>By ${article.author}</span>
                        ` : ''}
                    </div>
                </header>

                <!-- AI Summary Section -->
                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 rounded-xl mb-8 border border-blue-200 dark:border-blue-800">
                    <h2 class="flex items-center text-xl font-bold mb-4 text-blue-700 dark:text-blue-300">
                        <i class="material-icons mr-2">auto_awesome</i>
                        AI Summary
                    </h2>
                    <p class="text-gray-700 dark:text-gray-300 text-lg leading-relaxed">${aiProcessedContent.summary}</p>
                </div>

                <!-- Key Points Section -->
                ${aiProcessedContent.keyPoints.length > 0 ? `
                    <div class="bg-gray-50 dark:bg-gray-800 p-6 rounded-xl mb-8">
                        <h2 class="flex items-center text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
                            <i class="material-icons mr-2">key</i>
                            Key Points
                        </h2>
                        <ul class="space-y-3">
                            ${aiProcessedContent.keyPoints.map(point => `
                                <li class="flex items-start">
                                    <i class="material-icons text-[var(--primary-color)] mr-3 mt-1 text-sm">arrow_right</i>
                                    <span class="text-gray-700 dark:text-gray-300">${point}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}

                <!-- Article Image -->
                ${imageUrl ? `
                    <div class="mb-8">
                        <img src="${imageUrl}" alt="${article.title}" 
                             class="w-full h-48 md:h-64 object-cover rounded-xl shadow-lg"
                             onerror="this.style.display='none';">
                    </div>
                ` : ''}

                <!-- Main Article Content -->
                <div class="prose prose-lg dark:prose-invert max-w-none">
                    <div class="text-gray-700 dark:text-gray-300 leading-relaxed space-y-6">
                        ${aiProcessedContent.formattedContent}
                    </div>
                </div>

                <!-- AI Analysis Section -->
                ${aiProcessedContent.analysis ? `
                    <div class="mt-8 bg-purple-50 dark:bg-purple-900/20 p-6 rounded-xl border border-purple-200 dark:border-purple-800">
                        <h2 class="flex items-center text-xl font-bold mb-4 text-purple-700 dark:text-purple-300">
                            <i class="material-icons mr-2">psychology</i>
                            AI Analysis
                        </h2>
                        <p class="text-gray-700 dark:text-gray-300 leading-relaxed">${aiProcessedContent.analysis}</p>
                    </div>
                ` : ''}

                <!-- Original Source Section -->
                <div class="mt-8 p-6 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-xl border">
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-2">Read the Original Article</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400">Get the full story from the original source</p>
                        </div>
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer" 
                           class="inline-flex items-center px-6 py-3 bg-[var(--primary-color)] text-white rounded-lg hover:opacity-90 transition-opacity font-medium shadow-lg">
                            <i class="material-icons mr-2">open_in_new</i>
                            Original Source
                        </a>
                    </div>
                </div>

                <!-- Share Section -->
                <div class="mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
                    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Share this AI-enhanced article:</span>
                        <div class="flex gap-3">
                            <button onclick="shareArticle('twitter')" class="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                <i class="material-icons mr-2 text-sm">share</i>
                                Twitter
                            </button>
                            <button onclick="shareArticle('facebook')" class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                <i class="material-icons mr-2 text-sm">share</i>
                                Facebook
                            </button>
                            <button onclick="copyArticleLink()" class="flex items-center px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors">
                                <i class="material-icons mr-2 text-sm">link</i>
                                Copy Link
                            </button>
                        </div>
                    </div>
                </div>
            </article>
        `;
    }

    showArticleError() {
        const articleContainer = document.querySelector('#article-content');
        if (!articleContainer) return;

        articleContainer.innerHTML = `
            <div class="text-center py-12">
                <i class="material-icons text-5xl text-red-400 mb-4">error_outline</i>
                <h3 class="text-xl font-medium text-gray-600 dark:text-gray-300 mb-2">Article Not Found</h3>
                <p class="text-gray-500 mb-4">The article you're looking for could not be found.</p>
                <a href="#home" data-section="home" class="nav-link inline-flex items-center px-4 py-2 bg-[var(--primary-color)] text-white rounded-md hover:opacity-90 transition-opacity">
                    <i class="material-icons mr-2">arrow_back</i>
                    Back to Home
                </a>
            </div>
        `;
    }

    generateAIContent(article) {
        const cleanDescription = this.stripHtml(article.description || '');
        const cleanContent = this.stripHtml(article.content || '');
        const fullText = `${cleanDescription} ${cleanContent}`.trim();

        // AI-Enhanced Summary (limit to 200 words)
        const summary = this.generateAISummary(cleanDescription, article.title);

        // Extract key points
        const keyPoints = this.extractKeyPoints(fullText);

        // Format content for better readability (100-400 words max)
        const formattedContent = this.formatContentForReading(fullText, 400);

        // Generate AI analysis
        const analysis = this.generateAIAnalysis(article);

        return {
            summary,
            keyPoints,
            formattedContent,
            analysis,
            fullContent: formattedContent,
            wordCount: this.countWords(formattedContent)
        };
    }

    generateAISummary(description, title) {
        // AI-style summary generation (simulated)
        const sentences = description.split(/[.!?]+/).filter(s => s.trim().length > 10);

        if (sentences.length === 0) {
            return `This article discusses ${title.toLowerCase()}, providing insights and analysis on the topic.`;
        }

        // Take first 2-3 most relevant sentences and enhance them
        const keySentences = sentences.slice(0, Math.min(3, sentences.length));
        let summary = keySentences.join('. ').trim();

        // Ensure it ends with a period
        if (!summary.endsWith('.')) {
            summary += '.';
        }

        // Add AI enhancement context
        if (summary.length < 100) {
            summary += ` This AI-enhanced article provides comprehensive coverage and analysis of the key developments and implications.`;
        }

        return summary;
    }

    extractKeyPoints(content) {
        const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 20);
        const keyPoints = [];

        // Look for sentences with key indicators
        const keyIndicators = [
            'important', 'significant', 'major', 'key', 'critical', 'essential',
            'announced', 'revealed', 'discovered', 'found', 'shows', 'indicates',
            'according to', 'research', 'study', 'report', 'data', 'statistics'
        ];

        sentences.forEach(sentence => {
            const lowerSentence = sentence.toLowerCase();
            const hasKeyIndicator = keyIndicators.some(indicator => lowerSentence.includes(indicator));

            if (hasKeyIndicator && sentence.trim().length > 30 && sentence.trim().length < 200) {
                keyPoints.push(sentence.trim());
            }
        });

        // Limit to 5 key points
        return keyPoints.slice(0, 5);
    }

    formatContentForReading(content, maxWords = 400) {
        if (!content) return '<p>Content is being processed by our AI system for optimal readability.</p>';

        // Split into sentences
        const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);

        // Group sentences into paragraphs (3-4 sentences each)
        const paragraphs = [];
        let currentParagraph = [];
        let wordCount = 0;

        for (let sentence of sentences) {
            const sentenceWords = this.countWords(sentence);

            if (wordCount + sentenceWords > maxWords) {
                break;
            }

            currentParagraph.push(sentence.trim());
            wordCount += sentenceWords;

            // Create paragraph every 3-4 sentences
            if (currentParagraph.length >= 3 + Math.floor(Math.random() * 2)) {
                paragraphs.push(currentParagraph.join('. ') + '.');
                currentParagraph = [];
            }
        }

        // Add remaining sentences as final paragraph
        if (currentParagraph.length > 0) {
            paragraphs.push(currentParagraph.join('. ') + '.');
        }

        // Format as HTML paragraphs
        return paragraphs.map(p => `<p class="text-lg leading-relaxed mb-6">${p}</p>`).join('');
    }

    generateAIAnalysis(article) {
        const category = article.category || 'general';
        const title = article.title.toLowerCase();

        // Generate contextual analysis based on category and content
        const analysisTemplates = {
            technology: "This development represents a significant advancement in the technology sector, with potential implications for industry standards and future innovation.",
            business: "From a business perspective, this news could impact market dynamics and present new opportunities for stakeholders in the industry.",
            science: "The scientific implications of this research contribute to our understanding of the field and may influence future studies and applications.",
            politics: "This political development may have broader implications for policy-making and could influence future governmental decisions.",
            health: "This health-related news provides important insights that could affect public health policies and individual healthcare decisions.",
            sports: "This sports news highlights important developments in the athletic world and may influence future competitions and athlete performance.",
            entertainment: "This entertainment news reflects current trends in the industry and may influence future content creation and audience preferences.",
            markets: "This market development could significantly impact investor sentiment and trading patterns, with potential ripple effects across global financial markets including the US and Indian exchanges."
        };

        let baseAnalysis = analysisTemplates[category] || analysisTemplates.technology;

        // Add specific context based on title keywords
        if (title.includes('ai') || title.includes('artificial intelligence')) {
            baseAnalysis += " The AI implications of this development could reshape how we approach automation and machine learning in various sectors.";
        } else if (title.includes('climate') || title.includes('environment')) {
            baseAnalysis += " The environmental impact and sustainability aspects of this news are particularly relevant in today's climate-conscious world.";
        } else if (title.includes('economic') || title.includes('financial')) {
            baseAnalysis += " The economic ramifications could influence market trends and investment strategies in the coming months.";
        }

        return baseAnalysis;
    }

    calculateReadingTime(content) {
        const wordsPerMinute = 200; // Average reading speed
        const wordCount = this.countWords(content);
        return Math.max(1, Math.ceil(wordCount / wordsPerMinute));
    }

    countWords(text) {
        if (!text) return 0;
        return this.stripHtml(text).split(/\s+/).filter(word => word.length > 0).length;
    }


}