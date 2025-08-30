// News rendering utility
export class NewsRenderer {
    constructor(container) {
        this.container = container;
    }

    // Render a single news card
    renderNewsCard(article) {
        const card = document.createElement('div');
        card.className = 'news-card';
        
        const image = article.urlToImage || '/images/fallback.jpg';
        const category = article.category || 'general';
        
        card.innerHTML = `
            <img src="${image}" alt="${article.title}" class="news-card__image" onerror="this.src='/images/fallback.jpg'">
            <div class="news-card__content">
                <div class="news-card__category">${category}</div>
                <h3 class="news-card__title">${article.title}</h3>
                <div class="news-card__meta">
                    <span class="news-card__date">${new Date(article.publishedAt).toLocaleDateString()}</span>
                    <span class="news-card__source">${article.source.name}</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => {
            window.location.href = article.url;
        });
        
        return card;
    }

    // Render a list of news articles
    renderNewsList(articles, container = this.container) {
        container.innerHTML = '';
        articles.forEach(article => {
            container.appendChild(this.renderNewsCard(article));
        });
    }
}
