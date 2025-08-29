// Mobile menu functionality
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    const themeToggle = document.querySelector('.theme-toggle');

    menuToggle?.addEventListener('click', () => {
        mainNav?.classList.toggle('active');
        const isExpanded = mainNav?.classList.contains('active');
        menuToggle.setAttribute('aria-expanded', isExpanded.toString());
    });

    themeToggle?.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark-theme');
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        }
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // Check for saved theme preference
    if (localStorage.getItem('theme') === 'dark' || 
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark-theme');
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = 'fas fa-sun';
        }
    }

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        const target = e.target;
        if (!target.closest('.menu-toggle') && !target.closest('.main-nav') && mainNav?.classList.contains('active')) {
            mainNav.classList.remove('active');
            menuToggle?.setAttribute('aria-expanded', 'false');
        }
    });
});
