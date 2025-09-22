// Main application script
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Initialize theme toggle
        initializeThemeToggle();
        
        // Set up mobile menu if it exists
        setupMobileMenu();
        
        // Initialize single-page navigation
        initializeSinglePageNavigation();
        
        // Initialize news data integration
        console.log('Initializing news data integration...');
        const newsApp = new NewsDataIntegration();
        await newsApp.initialize();
        
        console.log('Main application initialized successfully');
        
    } catch (error) {
        console.error('Application initialization failed:', error);
    }
});

function initializeThemeToggle() {
    // Theme toggle is now handled inline in HTML files to avoid conflicts
    console.log('Theme toggle initialization skipped - handled inline');
}

function setupMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    
    if (mobileMenuToggle && mobileNav) {
        mobileMenuToggle.addEventListener('click', () => {
            const isHidden = mobileNav.classList.contains('hidden');
            
            if (isHidden) {
                mobileNav.classList.remove('hidden');
                mobileMenuToggle.setAttribute('aria-expanded', 'true');
                mobileMenuToggle.querySelector('i').textContent = 'close';
            } else {
                mobileNav.classList.add('hidden');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                mobileMenuToggle.querySelector('i').textContent = 'menu';
            }
        });

        // Close mobile menu when clicking on links
        const mobileLinks = mobileNav.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileNav.classList.add('hidden');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
                mobileMenuToggle.querySelector('i').textContent = 'menu';
            });
        });
    }

    // Mobile theme toggle is handled in initializeThemeToggle function
}

function initializeSinglePageNavigation() {
    // Handle navigation links
    document.addEventListener('click', (e) => {
        const navLink = e.target.closest('[data-section]');
        if (navLink) {
            e.preventDefault();
            const section = navLink.getAttribute('data-section');
            const articleUrl = navLink.getAttribute('data-article-url');
            
            showSection(section, articleUrl);
            updateNavigation(section);
            
            // Update URL without page reload
            const url = section === 'home' ? '/' : `/#${section}`;
            history.pushState({ section, articleUrl }, '', url);
        }
    });
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', (e) => {
        const state = e.state || { section: 'home' };
        showSection(state.section, state.articleUrl);
        updateNavigation(state.section);
    });
    
    // Handle initial page load with hash
    const hash = window.location.hash.slice(1);
    const [initialSection, queryString] = hash.split('?');
    const section = initialSection || 'home';
    
    // Handle article URLs with query parameters
    if (section === 'article' && queryString) {
        const params = new URLSearchParams(queryString);
        const articleId = params.get('id');
        showSection(section, articleId);
    } else {
        showSection(section);
    }
    updateNavigation(section);
}

function showSection(sectionName, articleUrl = null) {
    // Hide all sections
    document.querySelectorAll('.section-content').forEach(section => {
        section.classList.add('hidden');
    });
    
    // Show the requested section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.remove('hidden');
        
        // Handle special cases
        if (sectionName === 'categories') {
            // Initialize categories view
            if (window.newsDataIntegration) {
                window.newsDataIntegration.renderCategories();
            }
        } else if (sectionName === 'article' && articleUrl) {
            // Load specific article
            if (window.newsDataIntegration) {
                window.newsDataIntegration.renderArticle(articleUrl);
            }
        }
    }
}

function updateNavigation(activeSection) {
    // Update navigation link states
    document.querySelectorAll('.nav-link').forEach(link => {
        const section = link.getAttribute('data-section') || link.getAttribute('href').slice(1);
        
        if (section === activeSection) {
            link.classList.remove('text-gray-600', 'dark:text-gray-300');
            link.classList.add('text-[var(--primary-color)]');
        } else {
            link.classList.remove('text-[var(--primary-color)]');
            link.classList.add('text-gray-600', 'dark:text-gray-300');
        }
    });
}

// Global functions for article sharing
function shareArticle(platform) {
    const url = encodeURIComponent(window.location.href);
    const title = encodeURIComponent(document.title);

    let shareUrl = '';
    if (platform === 'twitter') {
        shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
    } else if (platform === 'facebook') {
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    }

    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
    }
}

function copyArticleLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        // Show a temporary notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.innerHTML = '<i class="material-icons mr-2 text-sm">check</i>Link copied to clipboard!';
        document.body.appendChild(notification);

        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    });
}
