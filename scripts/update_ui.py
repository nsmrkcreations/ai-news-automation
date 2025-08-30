import os
import shutil

def update_files():
    # Create backup directory
    backup_dir = 'backup'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup current files
    files_to_backup = ['public/index.html', 'public/css/styles.css']
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, os.path.basename(file)))
    
    # Create styles.css content
    styles_content = """/* Bulletin News Theme */
:root {
    /* Colors */
    --primary-color: #FF0000;
    --text-color: #1A1A1A;
    --background-color: #FFFFFF;
    --card-background: #FFFFFF;
    --border-color: #E5E5E5;
    --text-secondary: #666666;
    
    /* Layout */
    --header-height: 64px;
    --container-width: 1200px;
    --grid-gap: 24px;
    
    /* Typography */
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-size-xs: 12px;
    --font-size-sm: 13px;
    --font-size-base: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 24px;
    --line-height-tight: 1.3;
    --line-height-normal: 1.5;
}

/* Base Styles */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: var(--font-primary);
    line-height: var(--line-height-normal);
    color: var(--text-color);
    background: var(--background-color);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.container {
    max-width: var(--container-width);
    margin: 0 auto;
    padding: 0 20px;
}

/* Header & Navigation */
.header {
    height: var(--header-height);
    border-bottom: 1px solid var(--border-color);
    background: var(--background-color);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
}

.logo {
    font-size: var(--font-size-lg);
    font-weight: 600;
    color: var(--text-color);
    text-decoration: none;
}

.nav-links {
    display: flex;
    gap: 32px;
}

.nav-links a {
    color: var(--text-color);
    text-decoration: none;
    font-size: var(--font-size-base);
    font-weight: 500;
    padding: 8px 0;
    position: relative;
}

.nav-links a::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 2px;
    background-color: var(--primary-color);
    transform: scaleX(0);
    transition: transform 0.3s ease;
}

.nav-links a:hover::after,
.nav-links a.active::after {
    transform: scaleX(1);
}

/* Section Headers */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 40px 0 24px;
}

.section-title {
    font-size: var(--font-size-xl);
    font-weight: 600;
    color: var(--text-color);
}

.see-all {
    color: var(--primary-color);
    text-decoration: none;
    font-size: var(--font-size-sm);
    font-weight: 500;
}

/* News Grid */
.news-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--grid-gap);
}

/* News Card */
.news-card {
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.news-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-card__image {
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
}

.news-card__content {
    padding: 16px;
}

.news-card__category {
    font-size: var(--font-size-xs);
    font-weight: 500;
    color: var(--primary-color);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.news-card__title {
    font-size: var(--font-size-base);
    font-weight: 600;
    line-height: var(--line-height-tight);
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.news-card__meta {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
}

/* Featured Story */
.featured-story {
    margin-top: 32px;
}

.featured-grid {
    grid-template-columns: repeat(2, 1fr);
}

.featured-grid .news-card__title {
    font-size: var(--font-size-lg);
}

/* Story Icons */
.story-icons {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.story-icon {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 8px;
}

.story-icon__image {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    object-fit: cover;
}

.story-icon__title {
    font-size: var(--font-size-sm);
    font-weight: 500;
    color: var(--text-color);
}

/* Responsive Design */
@media (max-width: 1200px) {
    .news-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .featured-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 900px) {
    .news-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .nav-links {
        display: none;
    }
}

@media (max-width: 600px) {
    .news-grid {
        grid-template-columns: 1fr;
    }
    
    .section-header {
        flex-direction: column;
        gap: 8px;
        align-items: flex-start;
    }
}"""

    # Create index.html content
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI-Powered News - Stay informed with Bulletin">
    <meta name="theme-color" content="#ffffff">
    <title>Bulletin - AI-Powered News</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Styles -->
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="css/share.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Meta -->
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/png" href="images/icon-192.png">
    <link rel="apple-touch-icon" href="images/icon-192.png">
    
    <!-- Scripts -->
    <script src="js/main.js" type="module" defer></script>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <a href="/" class="logo">Bulletin</a>
                <div class="nav-links">
                    <a href="/" class="active">Home</a>
                    <a href="/world">World</a>
                    <a href="/politics">Politics</a>
                    <a href="/business">Business</a>
                    <a href="/technology">Technology</a>
                </div>
            </nav>
        </div>
    </header>

    <main class="container">
        <!-- Featured Story -->
        <section class="featured-story">
            <div class="section-header">
                <h2 class="section-title">Latest News</h2>
                <a href="/latest" class="see-all">See all →</a>
            </div>
            <div class="news-grid featured-grid">
                <!-- Featured stories will be inserted here -->
            </div>
        </section>

        <!-- Bulletin Story -->
        <section class="bulletin-story">
            <div class="section-header">
                <h2 class="section-title">Bulletin Story</h2>
                <a href="/stories" class="see-all">See all →</a>
            </div>
            <div class="story-icons">
                <!-- Story icons will be inserted here -->
            </div>
        </section>

        <!-- Must Read -->
        <section class="must-read">
            <div class="section-header">
                <h2 class="section-title">Must Read</h2>
                <a href="/must-read" class="see-all">See all →</a>
            </div>
            <div class="news-grid">
                <!-- News cards will be inserted here -->
            </div>
        </section>

        <!-- Editor's Pick -->
        <section class="editors-pick">
            <div class="section-header">
                <h2 class="section-title">Editor's Pick</h2>
                <a href="/editors-pick" class="see-all">See all →</a>
            </div>
            <div class="news-grid">
                <!-- Editor's pick stories will be inserted here -->
            </div>
        </section>
    </main>
</body>
</html>"""

    # Write the files
    with open('public/css/styles.css', 'w', encoding='utf-8') as f:
        f.write(styles_content)
        
    with open('public/index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)

if __name__ == '__main__':
    update_files()
