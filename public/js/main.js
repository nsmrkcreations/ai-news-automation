// Main application script
document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Initialize theme toggle
        initializeThemeToggle();
        
        // Set up mobile menu if it exists
        setupMobileMenu();
        
        // Initialize news data integration if on main page
        if (document.getElementById('featured-news') || document.getElementById('news-grid')) {
            console.log('Initializing news data integration...');
            const newsApp = new NewsDataIntegration();
            await newsApp.initialize();
        }
        
        // Initialize categories handler if on categories page
        if (document.getElementById('news-container')) {
            console.log('Categories page detected, handler will be initialized by categories.js');
        }
        
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
