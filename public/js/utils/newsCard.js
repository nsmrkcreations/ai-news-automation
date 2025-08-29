// newsCard.js - News card renderer
export function renderNewsCard(article) {
    const card = document.createElement('article');
    card.className = 'news-card';
    
    // Create image with fallback
    const imgContainer = document.createElement('div');
    imgContainer.className = 'news-image-container';
    
    const img = document.createElement('img');
    img.className = 'news-image';
    img.src = article.urlToImage || `/images/news/${article.category || 'fallback'}.jpg`;
    img.alt = article.title;
    img.onerror = () => {
        img.src = '/images/fallback.jpg';
    };
    
    imgContainer.appendChild(img);
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'news-content';
    
    // Add category
    if (article.category) {
        const category = document.createElement('div');
        category.className = 'news-category';
        category.textContent = article.category.charAt(0).toUpperCase() + article.category.slice(1);
        content.appendChild(category);
    }
    
    // Add title
    const title = document.createElement('h2');
    title.className = 'news-title';
    title.textContent = article.title;
    content.appendChild(title);
    
    // Add description
    const description = document.createElement('p');
    description.className = 'news-excerpt';
    description.textContent = article.description || article.content || '';
    content.appendChild(description);
    
    // Add metadata
    const meta = document.createElement('div');
    meta.className = 'news-meta';
    
    const source = document.createElement('span');
    source.className = 'news-source';
    source.textContent = article.source;
    
    const date = document.createElement('time');
    date.className = 'news-date';
    date.dateTime = article.publishedAt;
    const pubDate = new Date(article.publishedAt);
    date.textContent = pubDate.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
    
    meta.appendChild(source);
    meta.appendChild(date);
    content.appendChild(meta);
    
    // Add read more link
    const link = document.createElement('a');
    link.href = article.url;
    link.className = 'btn btn-primary';
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Read More';
    content.appendChild(link);
    
    // Assemble card
    card.appendChild(imgContainer);
    card.appendChild(content);
    
    return card;
}
