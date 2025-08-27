// Fetch and display news
async function fetchNews() {
    try {
        const response = await fetch('data/news.json');
        const articles = await response.json();
        displayNews(articles);
    } catch (error) {
        console.error('Error fetching news:', error);
    }
}

function displayNews(articles) {
    const newsGrid = document.getElementById('newsGrid');
    newsGrid.innerHTML = articles.map(article => `
        <div class="news-card">
            ${article.urlToImage ? `<img src="${article.urlToImage}" alt="${article.title}" class="news-image">` : ''}
            <div class="news-content">
                <div class="news-category">${article.category}</div>
                <h2 class="news-title">${article.title}</h2>
                <p class="news-description">${article.description}</p>
                <div class="news-meta">
                    <span class="news-date">${new Date(article.publishedAt).toLocaleDateString()}</span>
                    <button class="share-button" onclick="showShareOverlay('${article.url}', '${article.title.replace(/'/g, "\\'")}')">
                        <i class="fas fa-share-alt"></i>
                    </button>
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

// Initialize
document.addEventListener('DOMContentLoaded', fetchNews);
