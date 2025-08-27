// Fetch news data from our JSON file
async function fetchNews() {
    try {
        const response = await fetch('/data/news.json');
        const articles = await response.json();
        updateNewsDisplay(articles);
    } catch (error) {
        console.error('Error fetching news:', error);
    }
}

function updateNewsDisplay(articles) {
    // Update breaking news with the first article
    if (articles.length > 0) {
        updateBreakingNews(articles[0]);
    }

    // Update latest news grid with remaining articles
    const latestNewsGrid = document.querySelector('.news-grid');
    latestNewsGrid.innerHTML = ''; // Clear existing content

    articles.slice(1).forEach(article => {
        const articleCard = createArticleCard(article);
        latestNewsGrid.appendChild(articleCard);
    });
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

function updateBreakingNews(article) {
    const breakingNews = document.querySelector('.breaking-card');
    if (!breakingNews) return;
    
    try {
        if (!article || typeof article !== 'object') {
            throw new Error('Invalid article data');
        }

        const safeArticle = {
            image: article.image || 'https://source.unsplash.com/random/800x400/?news',
            title: article.title || 'No title available',
            category: article.category || 'Uncategorized',
            description: article.description || '',
            date: article.date || 'No date available',
            url: article.url || '#'
        };

        breakingNews.innerHTML = `
            <img src="${safeArticle.image}" alt="${escapeHtml(safeArticle.title)}" class="breaking-image" onerror="this.src='images/fallback.jpg'">
            <div class="breaking-content">
                <span class="news-category" style="--category-color: ${getCategoryColor(safeArticle.category)}">${escapeHtml(safeArticle.category)}</span>
                <h2 class="breaking-title">${escapeHtml(safeArticle.title)}</h2>
                <p class="breaking-excerpt">${escapeHtml(safeArticle.description)}</p>
                <div class="breaking-meta">
                    <time>${escapeHtml(safeArticle.date)}</time>
                    <button class="share-trigger" onclick="showShareOverlay('${escapeHtml(safeArticle.url)}', '${escapeHtml(safeArticle.title)}')">
                        <i class="fas fa-share-alt"></i>
                    </button>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error updating breaking news:', error);
        breakingNews.innerHTML = `
            <div class="error-message">
                <p>Unable to display breaking news. Please try again later.</p>
            </div>
        `;
    }
}

function createArticleCard(article) {
    const div = document.createElement('div');
    div.className = 'news-card';
    
    const safeArticle = {
        image: article.image || 'images/fallback.jpg',
        title: article.title || 'No title available',
        category: article.category || 'Uncategorized',
        description: article.description || '',
        date: article.date || 'No date available',
        readingTime: article.readingTime || '0 min read',
        url: article.url || '#'
    };

    div.innerHTML = `
        <img src="${escapeHtml(safeArticle.image)}" alt="${escapeHtml(safeArticle.title)}" class="news-image" onerror="this.src='images/fallback.jpg'">
        <div class="news-content">
            <span class="news-category" style="--category-color: ${getCategoryColor(safeArticle.category)}">${escapeHtml(safeArticle.category)}</span>
            <h3 class="news-title">${escapeHtml(safeArticle.title)}</h3>
            <p class="news-excerpt">${escapeHtml(safeArticle.description)}</p>
            <div class="news-meta">
                <time>${escapeHtml(safeArticle.date)}</time>
                <span class="reading-time">${escapeHtml(safeArticle.readingTime)}</span>
                <button class="share-trigger" onclick="showShareOverlay('${escapeHtml(safeArticle.url)}', '${escapeHtml(safeArticle.title)}')">
                    <i class="fas fa-share-alt"></i>
                </button>
            </div>
        </div>
    `;
    return div;
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
    return colors[category] || colors.default;
}

// Fetch news when page loads
document.addEventListener('DOMContentLoaded', fetchNews);

// Refresh news every 5 minutes
setInterval(fetchNews, 5 * 60 * 1000);
