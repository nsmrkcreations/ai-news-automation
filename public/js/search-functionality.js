/**
 * Search Functionality for News Articles
 */

class NewsSearch {
    constructor() {
        this.newsData = [];
        this.filteredData = [];
        this.currentCategory = 'all';
        this.init();
    }

    async init() {
        await this.loadNewsData();
        this.createSearchInterface();
        this.setupEventListeners();
    }

    async loadNewsData() {
        try {
            const response = await fetch('data/news.json');
            this.newsData = await response.json();
            this.filteredData = [...this.newsData];
        } catch (error) {
            console.error('Failed to load news data:', error);
        }
    }

    createSearchInterface() {
        // Add search bar to header
        const headerActions = document.querySelector('.header-actions') || this.createHeaderActions();
        
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        searchContainer.innerHTML = `
            <div class="search-box">
                <input type="text" id="news-search" placeholder="Search news..." class="search-input">
                <button class="search-btn" id="search-btn">🔍</button>
                <button class="clear-search" id="clear-search" style="display: none;">✕</button>
            </div>
            <div class="search-results" id="search-results" style="display: none;">
                <div class="results-header">
                    <span class="results-count">0 results found</span>
                </div>
                <div class="results-list"></div>
            </div>
        `;
        
        headerActions.insertBefore(searchContainer, headerActions.firstChild);
    }

    createHeaderActions() {
        const navContainer = document.querySelector('.nav-container');
        const headerActions = document.createElement('div');
        headerActions.className = 'header-actions';
        navContainer.appendChild(headerActions);
        return headerActions;
    }

    setupEventListeners() {
        const searchInput = document.getElementById('news-search');
        const searchBtn = document.getElementById('search-btn');
        const clearBtn = document.getElementById('clear-search');
        const searchResults = document.getElementById('search-results');

        // Real-time search
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (query.length > 2) {
                this.performSearch(query);
                clearBtn.style.display = 'block';
            } else if (query.length === 0) {
                this.clearSearch();
            }
        });

        // Search button
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                this.performSearch(query);
            }
        });

        // Clear search
        clearBtn.addEventListener('click', () => {
            this.clearSearch();
            searchInput.value = '';
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                searchResults.style.display = 'none';
            }
        });

        // Enter key search
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    this.performSearch(query);
                }
            }
        });
    }

    performSearch(query) {
        const results = this.newsData.filter(article => {
            const searchText = `${article.title} ${article.description} ${article.source}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });

        this.displaySearchResults(results, query);
    }

    displaySearchResults(results, query) {
        const searchResults = document.getElementById('search-results');
        const resultsCount = searchResults.querySelector('.results-count');
        const resultsList = searchResults.querySelector('.results-list');

        resultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''} found for "${query}"`;

        if (results.length === 0) {
            resultsList.innerHTML = `
                <div class="no-results">
                    <p>No articles found matching your search.</p>
                    <p>Try different keywords or check spelling.</p>
                </div>
            `;
        } else {
            resultsList.innerHTML = results.slice(0, 5).map(article => `
                <div class="search-result-item" onclick="window.open('${article.url}', '_blank')">
                    <div class="result-image">
                        <img src="${article.urlToImage || 'https://via.placeholder.com/80x60/667eea/ffffff?text=News'}" 
                             alt="${article.title}" 
                             onerror="this.src='https://via.placeholder.com/80x60/667eea/ffffff?text=News'">
                    </div>
                    <div class="result-content">
                        <h4 class="result-title">${this.highlightText(article.title, query)}</h4>
                        <p class="result-description">${this.highlightText(this.truncateText(article.description, 100), query)}</p>
                        <div class="result-meta">
                            <span class="result-source">${article.source}</span>
                            <span class="result-date">${this.formatDate(article.publishedAt)}</span>
                        </div>
                    </div>
                </div>
            `).join('');

            if (results.length > 5) {
                resultsList.innerHTML += `
                    <div class="show-all-results">
                        <button onclick="newsSearch.showAllResults('${query}')" class="show-all-btn">
                            Show all ${results.length} results
                        </button>
                    </div>
                `;
            }
        }

        searchResults.style.display = 'block';
    }

    highlightText(text, query) {
        if (!text || !query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    formatDate(dateString) {
        if (!dateString) return 'Today';
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Today';
        if (diffDays === 2) return 'Yesterday';
        if (diffDays <= 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }

    clearSearch() {
        const searchResults = document.getElementById('search-results');
        const clearBtn = document.getElementById('clear-search');
        
        searchResults.style.display = 'none';
        clearBtn.style.display = 'none';
    }

    showAllResults(query) {
        // Filter and display all results in main content area
        const results = this.newsData.filter(article => {
            const searchText = `${article.title} ${article.description} ${article.source}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });

        this.displayResultsInMainArea(results, query);
        this.clearSearch();
    }

    displayResultsInMainArea(results, query) {
        // Hide other sections and show search results
        const sections = ['latest-news', 'bulletin-story', 'most-read', 'editors-pick', 'dual-sections', 'top-creator'];
        sections.forEach(section => {
            const element = document.querySelector(`.${section}`);
            if (element) element.style.display = 'none';
        });

        // Create or update search results section
        let searchSection = document.querySelector('.search-results-section');
        if (!searchSection) {
            searchSection = document.createElement('section');
            searchSection.className = 'search-results-section';
            document.querySelector('.main-container').appendChild(searchSection);
        }

        searchSection.innerHTML = `
            <div class="section-header">
                <h2>Search Results for "${query}"</h2>
                <button class="back-to-home" onclick="newsSearch.backToHome()">← Back to Home</button>
            </div>
            <div class="search-results-grid">
                ${results.map(article => `
                    <div class="news-card-small" onclick="window.open('${article.url}', '_blank')">
                        <img src="${article.urlToImage || 'https://via.placeholder.com/300x180/667eea/ffffff?text=News'}" 
                             alt="${article.title}"
                             onerror="this.src='https://via.placeholder.com/300x180/667eea/ffffff?text=News'">
                        <div class="content">
                            <h3 class="title">${article.title}</h3>
                            <p class="description">${this.truncateText(article.description, 120)}</p>
                            <div class="meta">
                                <span class="source">${article.source}</span>
                                <span class="date">${this.formatDate(article.publishedAt)}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        searchSection.style.display = 'block';
    }

    backToHome() {
        // Show all sections again
        const sections = ['latest-news', 'bulletin-story', 'most-read', 'editors-pick', 'dual-sections', 'top-creator'];
        sections.forEach(section => {
            const element = document.querySelector(`.${section}`);
            if (element) element.style.display = 'block';
        });

        // Hide search results section
        const searchSection = document.querySelector('.search-results-section');
        if (searchSection) searchSection.style.display = 'none';

        // Clear search input
        const searchInput = document.getElementById('news-search');
        if (searchInput) searchInput.value = '';
        this.clearSearch();
    }
}

// Initialize search when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.newsSearch = new NewsSearch();
    });
} else {
    window.newsSearch = new NewsSearch();
}
