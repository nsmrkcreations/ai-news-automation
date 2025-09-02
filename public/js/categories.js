class CategoriesHandler {
    // Helper function to extract image URL from article (matching the one in news-data-integration.js)
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
                // Try to find an image URL in the content
                const imgMatch = article.content.match(/<img[^>]+src=["'](https?:\/\/[^"']+?\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (imgMatch && imgMatch[1]) {
                    const imgUrl = imgMatch[1].replace(/&amp;/g, '&');
                    if (this.isValidUrl(imgUrl)) {
                        return imgUrl;
                    }
                }
                
                // Try to find a figure with image in the content
                const figureMatch = article.content.match(/<figure[^>]*>\s*<img[^>]+src=["'](https?:\/\/[^"']+\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (figureMatch && figureMatch[1]) {
                    const imgUrl = figureMatch[1].replace(/&amp;/g, '&');
                    if (this.isValidUrl(imgUrl)) {
                        return imgUrl;
                    }
                }
            }
            
            // Check for image in description
            if (article.description) {
                const descImgMatch = article.description.match(/<img[^>]+src=["'](https?:\/\/[^"']+\.(?:jpg|jpeg|png|webp|gif)[^"']*)["']/i);
                if (descImgMatch && descImgMatch[1]) {
                    const imgUrl = descImgMatch[1].replace(/&amp;/g, '&');
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
    constructor() {
        this.newsContainer = document.getElementById('news-container');
        this.categories = new Set();
        this.newsData = [];
        if (this.newsContainer) this.initialize();
    }

    async initialize() {
        try {
            const response = await fetch('/data/news.json');
            this.newsData = await response.json();
            this.displayNewsByCategory();
        } catch (error) {
            console.error('Error loading news:', error);
        }
    }

    displayNewsByCategory() {
        const newsByCategory = {};
        
        // Group news by category
        this.newsData.forEach(article => {
            const category = article.category || 'General';
            if (!newsByCategory[category]) newsByCategory[category] = [];
            newsByCategory[category].push(article);
        });

        // Generate HTML
        let html = '';
        for (const [category, articles] of Object.entries(newsByCategory)) {
            html += `
                <div class="mb-12">
                    <h2 class="text-2xl font-bold mb-6 pb-2 border-b border-gray-200 dark:border-gray-700">
                        ${category}
                    </h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${articles.slice(0, 3).map(article => this.createArticleCard(article)).join('')}
                    </div>
                </div>
            `;
        }
        this.newsContainer.innerHTML = html;
    }

    createArticleCard(article) {
        // Default placeholder image (matching the one in news-data-integration.js)
        const placeholderImage = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwIDAgODAwIDQwMCI+CiAgPHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iI2YzZjRmNiIvPgogIDx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGZpbGw9Ii85Y2E3YmMiIGZvbnQtd2VpZ2h0PSJib2xkIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIj5ObyBpbWFnZSBhdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPg==';
        
        // Extract image URL using the same logic as the main page
        let imageUrl = this.extractImageUrl(article) || placeholderImage;
        
        // Format date
        const date = article.publishedAt ? new Date(article.publishedAt).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }) : '';
        
        return `
            <div class="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow">
                <a href="${article.url}" target="_blank" rel="noopener">
                    <div class="h-48 bg-cover bg-center" style="background-image: url('${imageUrl}')"></div>
                </a>
                <div class="p-4">
                    <a href="${article.url}" target="_blank" rel="noopener" class="hover:text-[var(--primary-color)]">
                        <h3 class="text-lg font-bold mb-2 line-clamp-2">${article.title}</h3>
                    </a>
                    ${date ? `<p class="text-sm text-gray-500 dark:text-gray-400 mb-2">${date}</p>` : ''}
                    <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-3">
                        ${article.description || ''}
                    </p>
                </div>
            </div>
        `;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CategoriesHandler();
});
