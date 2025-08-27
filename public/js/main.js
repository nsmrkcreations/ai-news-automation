// Global variables
let allArticles = [];
let currentCategory = 'all';
let isLoading = false;

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const shareOverlay = document.getElementById('shareOverlay');
const menuToggle = document.querySelector('.menu-toggle');
const mainNav = document.querySelector('.main-nav');

// Fetch and display news
async function fetchNews() {
    if (isLoading) return;
    
    isLoading = true;
    showLoading();
    
    try {
        const response = await fetch('data/news.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allArticles = await response.json();
        filterAndDisplayNews(currentCategory);
    } catch (error) {
        console.error('Error fetching news:', error);
        showError('Unable to load news articles. Please try again later.');
    } finally {
        isLoading = false;
    }
}

function showLoading() {
    newsGrid.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading news...</p>
        </div>
    `;
}

function showError(message) {
    newsGrid.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <p>${message}</p>
            <button onclick="fetchNews()" class="retry-button">
                <i class="fas fa-redo"></i> Try Again
            </button>
        </div>
    `;
}

function filterAndDisplayNews(category) {
    const filteredArticles = category === 'all' 
        ? allArticles 
        : allArticles.filter(article => article.category.toLowerCase() === category.toLowerCase());
    
    const newsGrid = document.getElementById('newsGrid');
    
    if (filteredArticles.length === 0) {
        newsGrid.innerHTML = `
            <div class="no-articles">
                <i class="fas fa-newspaper"></i>
                <p>No articles found in this category</p>
            </div>
        `;
        return;
    }
    
    newsGrid.innerHTML = filteredArticles.map(article => `
        <div class="news-card">
            <div class="news-image-container">
                ${article.urlToImage 
                    ? `<img src="${article.urlToImage}" alt="${article.title}" class="news-image" onerror="this.onerror=null; this.src='images/fallback.jpg';">` 
                    : `<div class="news-image-placeholder">
                           <i class="fas fa-newspaper"></i>
                       </div>`
                }
            </div>
            <div class="news-content">
                <div class="news-category">${article.category}</div>
                <h2 class="news-title">
                    <a href="${article.url}" target="_blank" rel="noopener noreferrer">${article.title}</a>
                </h2>
                <p class="news-description">${article.description || 'No description available'}</p>
                <div class="news-meta">
                    <span class="news-date">${formatDate(article.publishedAt)}</span>
                    <div class="news-actions">
                        <a href="${article.url}" target="_blank" rel="noopener noreferrer" class="read-more">
                            <i class="fas fa-external-link-alt"></i>
                        </a>
                        <button class="share-button" onclick="showShareOverlay('${article.url}', '${article.title.replace(/'/g, "\\'")}')">
                            <i class="fas fa-share-alt"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Share functionality
function showShareOverlay(url, title) {
    const shareOverlay = document.getElementById('shareOverlay');
    const shareTitle = document.getElementById('shareTitle');
    shareOverlay.style.display = 'flex';
    shareTitle.textContent = title;
    
    // Update share buttons
    document.getElementById('twitterShare').href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;
    document.getElementById('facebookShare').href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    document.getElementById('linkedinShare').href = `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
    window.shareUrl = url;
}

function hideShareOverlay() {
    document.getElementById('shareOverlay').style.display = 'none';
}

function copyLink() {
    navigator.clipboard.writeText(window.shareUrl).then(() => {
        alert('Link copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy link:', err);
    });
}

// Utility functions
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchNews();
    setupNavigationHandlers();
});

function setupNavigationHandlers() {
    // Category navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            currentCategory = link.dataset.category;
            filterAndDisplayNews(currentCategory);
        });
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    menuToggle.addEventListener('click', () => {
        mainNav.classList.toggle('show');
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    fetchNews();
    setupNavigationHandlers();
});
