/**
 * Theme Manager - Light/Dark Mode with System Detection
 * Combines Style 1 (Dark) and Style 2 (Light) with smooth transitions
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.init();
    }

    init() {
        // Apply initial theme
        this.applyTheme(this.currentTheme);
        
        // Create theme toggle button
        this.createThemeToggle();
        
        // Listen for system theme changes
        this.watchSystemTheme();
        
        // Listen for storage changes (sync across tabs)
        window.addEventListener('storage', (e) => {
            if (e.key === 'theme-preference') {
                this.currentTheme = e.newValue || this.getSystemTheme();
                this.applyTheme(this.currentTheme);
                this.updateToggleButton();
            }
        });
    }

    getSystemTheme() {
        // Default to light theme, but respect system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    getStoredTheme() {
        return localStorage.getItem('theme-preference');
    }

    setStoredTheme(theme) {
        if (theme === 'system') {
            localStorage.removeItem('theme-preference');
        } else {
            localStorage.setItem('theme-preference', theme);
        }
    }

    applyTheme(theme) {
        const root = document.documentElement;
        
        // Remove existing theme attributes
        root.removeAttribute('data-theme');
        
        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else if (theme === 'light') {
            // Light theme is default in CSS, no attribute needed
        } else if (theme === 'system') {
            // Let CSS handle system preference
            const systemTheme = this.getSystemTheme();
            if (systemTheme === 'dark') {
                root.setAttribute('data-theme', 'dark');
            }
        }

        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: theme }
        }));
    }

    updateMetaThemeColor(theme) {
        let themeColor = '#ffffff'; // Light theme default
        
        if (theme === 'dark' || (theme === 'system' && this.getSystemTheme() === 'dark')) {
            themeColor = '#0f0f23'; // Dark theme color
        }
        
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = themeColor;
    }

    toggleTheme() {
        const themes = ['light', 'dark', 'system'];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        
        this.currentTheme = themes[nextIndex];
        this.setStoredTheme(this.currentTheme);
        this.applyTheme(this.currentTheme);
        this.updateToggleButton();
    }

    createThemeToggle() {
        // Remove existing toggle if present
        const existingToggle = document.querySelector('.theme-toggle');
        if (existingToggle) {
            existingToggle.remove();
        }

        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle theme');
        toggle.setAttribute('title', 'Switch between light, dark, and system theme');
        
        toggle.innerHTML = `
            <span class="icon light-icon">☀️</span>
            <span class="icon dark-icon">🌙</span>
            <span class="theme-text">Theme</span>
        `;
        
        toggle.addEventListener('click', () => this.toggleTheme());
        
        document.body.appendChild(toggle);
        this.updateToggleButton();
    }

    updateToggleButton() {
        const toggle = document.querySelector('.theme-toggle');
        if (!toggle) return;

        const lightIcon = toggle.querySelector('.light-icon');
        const darkIcon = toggle.querySelector('.dark-icon');
        const themeText = toggle.querySelector('.theme-text');
        
        // Update button content based on current theme
        switch (this.currentTheme) {
            case 'light':
                lightIcon.style.display = 'inline';
                darkIcon.style.display = 'none';
                themeText.textContent = 'Light';
                toggle.setAttribute('title', 'Current: Light theme. Click for Dark theme.');
                break;
            case 'dark':
                lightIcon.style.display = 'none';
                darkIcon.style.display = 'inline';
                themeText.textContent = 'Dark';
                toggle.setAttribute('title', 'Current: Dark theme. Click for System theme.');
                break;
            case 'system':
                const systemTheme = this.getSystemTheme();
                if (systemTheme === 'dark') {
                    lightIcon.style.display = 'none';
                    darkIcon.style.display = 'inline';
                } else {
                    lightIcon.style.display = 'inline';
                    darkIcon.style.display = 'none';
                }
                themeText.textContent = 'Auto';
                toggle.setAttribute('title', 'Current: System theme. Click for Light theme.');
                break;
        }
    }

    watchSystemTheme() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addEventListener('change', (e) => {
                if (this.currentTheme === 'system') {
                    this.applyTheme('system');
                    this.updateToggleButton();
                }
            });
        }
    }

    // Public API
    getCurrentTheme() {
        return this.currentTheme;
    }

    setTheme(theme) {
        if (['light', 'dark', 'system'].includes(theme)) {
            this.currentTheme = theme;
            this.setStoredTheme(theme);
            this.applyTheme(theme);
            this.updateToggleButton();
        }
    }

    // Utility method to check if dark theme is active
    isDarkMode() {
        if (this.currentTheme === 'dark') return true;
        if (this.currentTheme === 'system') return this.getSystemTheme() === 'dark';
        return false;
    }
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
