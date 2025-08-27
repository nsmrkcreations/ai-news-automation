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

function updateBreakingNews(article) {
    const breakingNews = document.querySelector('.breaking-card');
    if (breakingNews) {
        breakingNews.innerHTML = `
            <img src="${article.image || 'https://source.unsplash.com/random/800x400/?news'}" alt="${article.title}" class="breaking-image">
            <div class="breaking-content">
                <span class="news-category" style="--category-color: ${getCategoryColor(article.category)}">${article.category}</span>
                <h2 class="breaking-title">${article.title}</h2>
                <p class="breaking-excerpt">${article.description || ''}</p>
                <div class="breaking-meta">
                    <time>${article.date}</time>
                    <button class="share-trigger" onclick="showShareOverlay('${article.title}', '${article.url}')">
                        <i class="fas fa-share-alt"></i>
                    </button>
                </div>
            </div>
        `;
    }
}

function createArticleCard(article) {
    const div = document.createElement('div');
    div.className = 'news-card';
    div.innerHTML = `
        <img src="${article.image || 'https://source.unsplash.com/random/800x400/?news'}" alt="${article.title}" class="news-image">
        <div class="news-content">
            <span class="news-category" style="--category-color: ${getCategoryColor(article.category)}">${article.category}</span>
            <h3 class="news-title">${article.title}</h3>
            <p class="news-excerpt">${article.description || ''}</p>
            <div class="news-meta">
                <time>${article.date}</time>
                <span class="reading-time">${article.readingTime}</span>
                <button class="share-trigger" onclick="showShareOverlay('${article.title}', '${article.url}')">
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
