// Main application initialization
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize services
    const newsService = new NewsService();
    const newsUI = new NewsUI(newsService);
    
    // Initialize theme system
    const themeManager = new ThemeManager();
    
    // Initialize breaking news
    const breakingNewsTicker = new BreakingNewsTicker(
        document.querySelector('.breaking-news-ticker')
    );
    
    try {
        // Load and render news
        await newsUI.initialize();
        
        // Set up mobile menu
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        const mainNav = document.querySelector('.main-nav');
        if (mobileMenuToggle && mainNav) {
            mobileMenuToggle.addEventListener('click', () => {
                mainNav.classList.toggle('active');
                const isExpanded = mainNav.classList.contains('active');
                mobileMenuToggle.setAttribute('aria-expanded', isExpanded);
            });
        }
        
        // Set up search functionality
        const searchForm = document.querySelector('.search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const searchInput = searchForm.querySelector('input');
                if (searchInput.value.trim()) {
                    // Implement search functionality
                    console.log('Searching for:', searchInput.value);
                }
            });
        }
        
        // Category navigation
        const categoryLinks = document.querySelectorAll('.nav-link');
        categoryLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                categoryLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                const category = link.getAttribute('data-category');
                // Implement category filtering
                console.log('Switching to category:', category);
            });
        });
        
    } catch (error) {
        console.error('Application initialization failed:', error);
    }
});
