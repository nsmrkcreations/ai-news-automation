// Import modules
import { NewsUpdater } from './utils/NewsUpdater.js';
import shareHandler from './utils/share-handler.js';
import { NewsCardRenderer } from './utils/NewsCardRenderer.js';
import './components/navigation.js';

// Service Worker Registration and Update Management
async function registerAndUpdateSW() {
    try {
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.register('/sw.js');

            // Check for updates every minute
            setInterval(async () => {
                try {
                    await registration.update();
                    
                    if (registration.waiting) {
                        // New version available
                        if (confirm('A new version is available. Would you like to update?')) {
                            registration.waiting.postMessage({ type: 'SKIP_WAITING' });
                            window.location.reload();
                        }
                    }
                } catch (error) {
                    console.error('SW update check failed:', error);
                }
            }, 60000);

            // Handle updates that happen in the background
            let refreshing = false;
            navigator.serviceWorker.addEventListener('controllerchange', () => {
                if (!refreshing) {
                    refreshing = true;
                    window.location.reload();
                }
            });
        }
    } catch (error) {
        console.error('SW registration failed:', error);
    }
}

// Global state
var state = {
    allArticles: [],
    currentCategory: 'all',
    isLoading: false
};

// DOM Elements
var elements = {
    newsGrid: document.getElementById('newsGrid'),
    shareOverlay: document.getElementById('shareOverlay'),
    menuToggle: document.querySelector('.menu-toggle'),
    mainNav: document.querySelector('.main-nav'),
    mobileMenu: document.querySelector('.mobile-menu')
};

// Initialize news updater and service worker
var newsUpdater = new NewsUpdater();

// Register and initialize service worker
registerAndUpdateSW().then(() => {
    console.log('Service Worker registered successfully');
}).catch(error => {
    console.error('Service Worker registration failed:', error);
});

// Add test function for cache invalidation
async function testCacheInvalidation() {
    if ('serviceWorker' in navigator) {
        try {
            // Get all caches
            const cacheKeys = await caches.keys();
            console.log('Current caches:', cacheKeys);

            // Check version.json
            const versionResponse = await fetch('/version.json');
            const versionData = await versionResponse.json();
            console.log('Current version:', versionData);

            // Test news data freshness
            const newsResponse = await fetch('/data/news.json');
            const newsData = await newsResponse.json();
            console.log('Latest news timestamp:', newsData[0]?.publishedAt);

            return true;
        } catch (error) {
            console.error('Cache test failed:', error);
            return false;
        }
    }
    return false;
}

// Run cache test after 2 seconds to ensure service worker is active
setTimeout(() => {
    testCacheInvalidation().then(result => {
        console.log('Cache invalidation test result:', result);
    });
}, 2000);

// Set up event handlers
newsUpdater.on('initial', articles => {
    state.allArticles = articles;
    filterAndDisplayNews(state.currentCategory);
    elements.newsGrid?.removeAttribute('aria-busy');
});

newsUpdater.on('update', articles => {
    state.allArticles = [...articles, ...state.allArticles];
    filterAndDisplayNews(state.currentCategory);
    showUpdateNotification(articles.length, false);
});

newsUpdater.on('breaking', articles => {
    state.allArticles = [...articles, ...state.allArticles];
    filterAndDisplayNews(state.currentCategory);
    showUpdateNotification(articles.length, true);
});

newsUpdater.on('connectionChange', status => {
    handleConnectionStatus(status);
});

function showUpdateNotification(count, isBreaking) {
    const notification = document.createElement('div');
    notification.className = `update-notification ${isBreaking ? 'breaking' : ''}`;
    
    if (isBreaking) {
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <strong>Breaking News:</strong> ${count} new urgent ${count === 1 ? 'story' : 'stories'}
        `;
    } else {
        notification.textContent = `${count} new ${count === 1 ? 'article' : 'articles'} available`;
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, isBreaking ? 6000 : 3000);
}

function handleConnectionStatus(status) {
    // Status is now handled by NewsUpdater class
    if (status === 'error') {
        showError('Connection lost. Retrying...');
    }
    
    switch (status.status) {
        case 'connected':
            statusEl.textContent = 'Connected to news service';
            statusEl.classList.remove('error', 'warning');
            break;
        case 'disconnected':
            statusEl.textContent = 'Disconnected from news service. Reconnecting...';
            statusEl.classList.add('warning');
            break;
        case 'error':
            statusEl.textContent = 'Error connecting to news service';
            statusEl.classList.add('error');
            break;
    }

    if (!statusEl.parentNode) {
        document.body.appendChild(statusEl);
    }

    if (status.status === 'connected') {
        setTimeout(() => statusEl.remove(), 3000);
    }
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

function filterAndDisplayNews(category) {
    const filteredArticles = category === 'all' 
        ? state.allArticles 
        : state.allArticles.filter(article => article.category.toLowerCase() === category.toLowerCase());
    
    if (!elements.newsGrid) return;
    
    if (filteredArticles.length === 0) {
        elements.newsGrid.innerHTML = `
            <div class="no-content">
                <i class="fas fa-newspaper"></i>
                <p>No articles found in this category</p>
            </div>
        `;
        return;
    }
    
    elements.newsGrid.innerHTML = filteredArticles.map(article => `
        <article class="news-card">
            <img src="${article.image || 'images/fallback.jpg'}" 
                alt="${escapeHtml(article.title)}" 
                class="news-image"
                onerror="this.src='images/fallback.jpg'">
            <div class="news-content">
                <span class="news-category" style="--category-color: ${getCategoryColor(article.category)}">
                    ${escapeHtml(article.category)}
                </span>
                <h3 class="news-title">${escapeHtml(article.title)}</h3>
                <p class="news-excerpt">${escapeHtml(article.description || '')}</p>
                <div class="news-meta">
                    <time>${formatDate(article.date)}</time>
                    <button class="share-trigger" 
                        onclick="showShareOverlay('${escapeHtml(article.url)}', '${escapeHtml(article.title)}')"
                        aria-label="Share this article">
                        <i class="fas fa-share-alt"></i>
                    </button>
                </div>
            </div>
        </article>
    `).join('');
}

function escapeHtml(unsafe) {
    if (!unsafe || typeof unsafe !== 'string') return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getCategoryColor(category) {
    const colors = {
        business: '#059669',
        technology: '#7c3aed',
        politics: '#dc2626',
        sports: '#ea580c',
        entertainment: '#db2777',
        default: '#2563eb'
    };
    return colors[category.toLowerCase()] || colors.default;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    setupMobileMenu();
    handleNetworkStatus();
});

// Network handling
window.addEventListener('online', () => {
    // NewsUpdater will initialize automatically
    handleNetworkStatus();
});

window.addEventListener('offline', handleNetworkStatus);

function handleNetworkStatus() {
    const existingStatus = document.querySelector('.network-status');
    if (existingStatus) {
        existingStatus.remove();
    }

    if (!navigator.onLine) {
        const networkStatus = document.createElement('div');
        networkStatus.className = 'network-status';
        networkStatus.innerHTML = `
            <div class="offline-message">
                <i class="fas fa-wifi-slash"></i>
                You are offline. Some content may not be available.
                <button class="retry-button" onclick="retryConnection()">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
        document.body.prepend(networkStatus);
    }
}

function retryConnection() {
    if (!navigator.onLine) {
        showError('Still offline. Please check your internet connection.');
    }
    // NewsUpdater will handle reconnection automatically
}

function setupMobileMenu() {
    if (!elements.menuToggle || !elements.mobileMenu) return;

    elements.menuToggle.addEventListener('click', () => {
        elements.mobileMenu.classList.toggle('active');
        document.body.style.overflow = elements.mobileMenu.classList.contains('active') ? 'hidden' : '';
    });

    document.addEventListener('click', (e) => {
        if (elements.mobileMenu.classList.contains('active') && 
            !elements.mobileMenu.contains(e.target) && 
            !elements.menuToggle.contains(e.target)) {
            elements.mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}
