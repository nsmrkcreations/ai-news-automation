class SearchHandler {
    constructor() {
        this.searchInput = document.getElementById('search-input');
        this.newsContainer = document.getElementById('news-grid');
        this.originalNews = [];
        
        if (this.searchInput) {
            this.initialize();
        }
    }

    async initialize() {
        try {
            // Load news data
            const response = await fetch('/data/news.json');
            this.originalNews = await response.json();
            
            // Add event listener for search input
            this.searchInput.addEventListener('input', (e) => this.handleSearch(e));
            
            // Add event listener for Enter key
            this.searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSearch(e);
                }
            });
        } catch (error) {
            console.error('Error initializing search:', error);
        }
    }

    handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            // If search is empty, show all news
            this.displayNews(this.originalNews);
            return;
        }
        
        // Filter news based on search term
        const filteredNews = this.originalNews.filter(news => 
            news.title.toLowerCase().includes(searchTerm) || 
            news.description.toLowerCase().includes(searchTerm) ||
            (news.content && news.content.toLowerCase().includes(searchTerm))
        );
        
        this.displayNews(filteredNews);
    }

    displayNews(newsItems) {
        if (!this.newsContainer) return;
        
        if (newsItems.length === 0) {
            this.newsContainer.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <i class="material-icons text-5xl text-gray-400 mb-4">search_off</i>
                    <h3 class="text-xl font-medium text-gray-600 dark:text-gray-300">No results found</h3>
                    <p class="text-gray-500 mt-2">Try different keywords or check back later for updates.</p>
                </div>
            `;
            return;
        }
        
        // Clear existing news
        this.newsContainer.innerHTML = '';
        
        // Add filtered news items
        newsItems.forEach(item => {
            const newsElement = this.createNewsElement(item);
            this.newsContainer.appendChild(newsElement);
        });
    }

    createNewsElement(news) {
        const article = document.createElement('article');
        article.className = 'bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300';
        
        const image = news.imageUrl ? 
            `<img src="${news.imageUrl}" alt="${news.title}" class="w-full h-48 object-cover">` :
            `<div class="w-full h-48 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <i class="material-icons text-4xl text-gray-400">image_not_supported</i>
            </div>`;
        
        article.innerHTML = `
            ${image}
            <div class="p-4">
                <div class="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2">
                    <span class="capitalize">${news.category || 'General'}</span>
                    <span class="mx-2">•</span>
                    <span>${new Date(news.publishedAt).toLocaleDateString()}</span>
                </div>
                <h3 class="text-lg font-semibold mb-2 line-clamp-2">${news.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-3">${news.description || ''}</p>
                <a href="${news.url || '#'}" class="mt-4 inline-flex items-center text-[var(--primary-color)] hover:underline" target="_blank" rel="noopener noreferrer">
                    Read more
                    <i class="material-icons ml-1 text-sm">arrow_forward</i>
                </a>
            </div>
        `;
        
        return article;
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SearchHandler();
});
