// Category page functionality
import { createNewsCard, showError, showLoadingState } from './utils/ui.js';
import linkHandler from './utils/link-handler.js';

document.addEventListener('DOMContentLoaded', () => {
    const categoryHeader = document.getElementById('categoryHeader');
    const newsList = document.getElementById('newsList');
    const sortBy = document.getElementById('sortBy');
    const timeRange = document.getElementById('timeRange');
    const pagination = document.getElementById('pagination');

    let currentPage = 1;
    const itemsPerPage = 12;
    let currentCategory = '';
    let newsData = [];

    // Get category from URL
    const urlParams = new URLSearchParams(window.location.search);
    currentCategory = urlParams.get('cat') || 'all';

    // Initialize the page
    initializePage();

    // Event listeners for filters
    sortBy?.addEventListener('change', handleFiltersChange);
    timeRange?.addEventListener('change', handleFiltersChange);

    async function initializePage() {
        try {
            // Update header
            updateCategoryHeader();
            
            // Show loading state
            showLoadingState(newsList);

            // Fetch news data
            await fetchCategoryNews();

            // Update URL with category
            linkHandler.navigate(`/category.html?cat=${currentCategory}`, 
                `${capitalizeFirst(currentCategory)} News - NewsSurgeAI`);

        } catch (error) {
            console.error('Error initializing category page:', error);
            showError('Unable to load category news. Please try again later.');
        }
    }

    function updateCategoryHeader() {
        if (!categoryHeader) return;

        const categoryInfo = getCategoryInfo(currentCategory);
        categoryHeader.innerHTML = `
            <div class="category-header ${currentCategory}">
                <i class="fas fa-${categoryInfo.icon}"></i>
                <h1>${categoryInfo.title}</h1>
                <p>${categoryInfo.description}</p>
            </div>
        `;
    }

    async function fetchCategoryNews() {
        try {
            const response = await fetch('/data/news.json');
            if (!response.ok) throw new Error('Failed to fetch news data');

            const allNews = await response.json();
            
            // Filter by category
            newsData = currentCategory === 'all' 
                ? allNews 
                : allNews.filter(article => article.category.toLowerCase() === currentCategory.toLowerCase());

            // Apply current filters
            const filtered = filterNews(newsData);
            
            // Update display
            displayNews(filtered);
            
        } catch (error) {
            console.error('Error fetching category news:', error);
            showError('Unable to load news. Please try again later.');
        }
    }

    function filterNews(articles) {
        let filtered = [...articles];

        // Apply time range filter
        const timeRangeValue = timeRange?.value || 'all';
        if (timeRangeValue !== 'all') {
            const now = new Date();
            const timeRanges = {
                today: 1,
                week: 7,
                month: 30
            };
            
            const daysAgo = timeRanges[timeRangeValue];
            if (daysAgo) {
                const cutoff = new Date(now.setDate(now.getDate() - daysAgo));
                filtered = filtered.filter(article => new Date(article.date) >= cutoff);
            }
        }

        // Apply sort
        const sortByValue = sortBy?.value || 'date';
        if (sortByValue === 'date') {
            filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
        } else if (sortByValue === 'relevance') {
            filtered.sort((a, b) => b.relevanceScore - a.relevanceScore);
        }

        return filtered;
    }

    function displayNews(articles) {
        if (!newsList) return;

        if (articles.length === 0) {
            newsList.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <p>No articles found in this category.</p>
                    <a href="/categories.html" class="back-link">Browse All Categories</a>
                </div>
            `;
            return;
        }

        // Calculate pagination
        const totalPages = Math.ceil(articles.length / itemsPerPage);
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const pageArticles = articles.slice(start, end);

        // Display articles
        newsList.innerHTML = pageArticles.map(article => createNewsCard(article)).join('');

        // Update pagination
        updatePagination(totalPages);
    }

    function updatePagination(totalPages) {
        if (!pagination) return;

        const pages = [];
        
        // Previous button
        if (currentPage > 1) {
            pages.push(`
                <button 
                    class="pagination-button" 
                    onclick="changePage(${currentPage - 1})"
                    aria-label="Previous page">
                    <i class="fas fa-chevron-left"></i>
                </button>
            `);
        }

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (
                i === 1 || 
                i === totalPages || 
                (i >= currentPage - 2 && i <= currentPage + 2)
            ) {
                pages.push(`
                    <button 
                        class="pagination-button ${i === currentPage ? 'active' : ''}"
                        onclick="changePage(${i})"
                        aria-label="Page ${i}"
                        ${i === currentPage ? 'aria-current="page"' : ''}>
                        ${i}
                    </button>
                `);
            } else if (
                i === currentPage - 3 || 
                i === currentPage + 3
            ) {
                pages.push('<span class="pagination-ellipsis">...</span>');
            }
        }

        // Next button
        if (currentPage < totalPages) {
            pages.push(`
                <button 
                    class="pagination-button" 
                    onclick="changePage(${currentPage + 1})"
                    aria-label="Next page">
                    <i class="fas fa-chevron-right"></i>
                </button>
            `);
        }

        pagination.innerHTML = pages.join('');
    }

    function handleFiltersChange() {
        const filtered = filterNews(newsData);
        currentPage = 1; // Reset to first page
        displayNews(filtered);
    }

    // Make changePage function globally available
    window.changePage = (page) => {
        currentPage = page;
        const filtered = filterNews(newsData);
        displayNews(filtered);
        // Scroll to top of news list
        newsList?.scrollIntoView({ behavior: 'smooth' });
    };
});

// Utility functions
function getCategoryInfo(category) {
    const categories = {
        world: {
            title: 'World News',
            description: 'Global headlines and international coverage',
            icon: 'globe'
        },
        politics: {
            title: 'Politics',
            description: 'Political news and policy updates',
            icon: 'landmark'
        },
        business: {
            title: 'Business',
            description: 'Business and economic news',
            icon: 'chart-line'
        },
        technology: {
            title: 'Technology',
            description: 'Tech news and innovations',
            icon: 'microchip'
        },
        science: {
            title: 'Science',
            description: 'Scientific discoveries and research',
            icon: 'flask'
        },
        health: {
            title: 'Health',
            description: 'Health and medical news',
            icon: 'heartbeat'
        },
        entertainment: {
            title: 'Entertainment',
            description: 'Entertainment and culture news',
            icon: 'film'
        },
        sports: {
            title: 'Sports',
            description: 'Sports news and updates',
            icon: 'basketball-ball'
        },
        all: {
            title: 'All Categories',
            description: 'Browse all news categories',
            icon: 'newspaper'
        }
    };

    return categories[category] || categories.all;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
