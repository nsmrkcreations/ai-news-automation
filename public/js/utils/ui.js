// UI utility functions
import linkHandler from './link-handler.js';
import shareHandler from './share-handler.js';

export function createNewsCard(article) {
    const safeArticle = {
        title: shareHandler.sanitizeShareData(article.title),
        description: shareHandler.sanitizeShareData(article.description),
        category: shareHandler.sanitizeShareData(article.category),
        image: linkHandler.validateUrl(article.image) || 'images/fallback.jpg',
        url: linkHandler.validateUrl(article.url),
        date: article.date ? new Date(article.date).toLocaleDateString() : 'No date'
    };

    return `
        <article class="news-card" role="article">
            <img src="${safeArticle.image}" 
                 alt="${safeArticle.title}"
                 class="news-image"
                 loading="lazy"
                 onerror="this.src='images/fallback.jpg'">
            <div class="news-content">
                <span class="news-category">${safeArticle.category}</span>
                <h3 class="news-title">
                    <a href="${safeArticle.url}" class="news-link">
                        ${safeArticle.title}
                    </a>
                </h3>
                <p class="news-description">${safeArticle.description}</p>
                <div class="news-meta">
                    <time datetime="${article.date}">${safeArticle.date}</time>
                    <button class="share-button" 
                            onclick="showShareOverlay('${safeArticle.url}', '${safeArticle.title}')"
                            aria-label="Share this article">
                        <i class="fas fa-share-alt" aria-hidden="true"></i>
                    </button>
                </div>
            </div>
        </article>
    `;
}

export function showError(message, context = 'general') {
    console.error(`[${context}] ${message}`);
    
    return `
        <div class="error-container" role="alert">
            <div class="error-icon">
                <i class="fas fa-exclamation-circle" aria-hidden="true"></i>
            </div>
            <p class="error-message">${shareHandler.sanitizeShareData(message)}</p>
            <button onclick="location.reload()" 
                    class="retry-button"
                    aria-label="Reload the page">
                <i class="fas fa-redo" aria-hidden="true"></i> Try Again
            </button>
        </div>
    `;
}

export function showLoadingState(container) {
    if (!container) return;

    container.setAttribute('aria-busy', 'true');
    container.innerHTML = `
        <div class="loading-container" role="alert" aria-live="polite">
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin" aria-hidden="true"></i>
            </div>
            <p class="loading-text">Loading content...</p>
        </div>
        ${Array(6).fill(0).map(() => `
            <div class="news-card shimmer" aria-hidden="true">
                <div class="news-image-container"></div>
                <div class="news-content">
                    <div class="news-category-placeholder"></div>
                    <div class="news-title-placeholder"></div>
                    <div class="news-description-placeholder"></div>
                </div>
            </div>
        `).join('')}
    `;
}

export function showNotification(type, message, duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.setAttribute('role', 'alert');
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}" 
               aria-hidden="true"></i>
            <p>${shareHandler.sanitizeShareData(message)}</p>
        </div>
        <button class="close-notification" 
                aria-label="Close notification"
                onclick="this.parentElement.remove()">
            <i class="fas fa-times" aria-hidden="true"></i>
        </button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}
