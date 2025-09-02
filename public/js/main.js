// News integration script
document.addEventListener('DOMContentLoaded', async function() {
    let currentCategory = 'all';
    let newsData = [];
    
    // Load news data
    fetch('/data/news.json')
        .then(response => response.json())
        .then(data => {
            console.log('Loaded news data:', data);
            newsData = data;
            updateLinks();
            displayNews(newsData);
            setupCategoryLinks();
            setupSearch();
        })
        .catch(error => console.error('Error loading news:', error));
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
