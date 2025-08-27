// Focus trap utility for modal dialogs
export function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    // Store the element that had focus before opening the modal
    const previouslyFocused = document.activeElement;
    
    function handleTabKey(e) {
        const isTabPressed = e.key === 'Tab';
        
        if (!isTabPressed) return;
        
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    }
    
    // Focus the first element when the modal opens
    firstFocusable?.focus();
    
    element.addEventListener('keydown', handleTabKey);
    
    // Return cleanup function
    return () => {
        element.removeEventListener('keydown', handleTabKey);
        previouslyFocused?.focus();
    };
}

// Share functionality module
const shareModule = {
    activeCleanup: null,
    
    showShareOverlay(url, title, linkHandler) {
        try {
            const shareOverlay = document.getElementById('shareOverlay');
            const shareTitle = document.getElementById('shareTitle');
            if (!shareOverlay || !shareTitle) {
                throw new Error('Required share elements not found');
            }

            if (!linkHandler) {
                throw new Error('Share handler not initialized');
            }

            const safeUrl = linkHandler.validateUrl(url);
            const safeTitle = this.sanitizeShareData(title);

            // Make overlay accessible
            shareOverlay.setAttribute('role', 'dialog');
            shareOverlay.setAttribute('aria-label', 'Share article');
            shareOverlay.setAttribute('aria-modal', 'true');
            
            shareOverlay.style.display = 'flex';
            shareTitle.textContent = safeTitle;
            
            const socialButtons = {
                'twitterShare': {
                    url: `https://twitter.com/intent/tweet?text=${encodeURIComponent(safeTitle)}&url=${encodeURIComponent(safeUrl)}`,
                    label: 'Share on Twitter'
                },
                'facebookShare': {
                    url: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(safeUrl)}`,
                    label: 'Share on Facebook'
                },
                'linkedinShare': {
                    url: `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(safeUrl)}&title=${encodeURIComponent(safeTitle)}`,
                    label: 'Share on LinkedIn'
                }
            };

            Object.entries(socialButtons).forEach(([id, { url: href, label }]) => {
                const button = document.getElementById(id);
                if (button) {
                    button.href = href;
                    button.setAttribute('aria-label', label);
                    button.setAttribute('rel', 'noopener noreferrer');
                    button.setAttribute('target', '_blank');
                    
                    // Remove any existing event listeners
                    const newButton = button.cloneNode(true);
                    button.parentNode.replaceChild(newButton, button);
                    
                    // Add new event listener
                    newButton.addEventListener('click', () => {
                        linkHandler.trackLinkClick(href, 'share');
                    });
                }
            });

            // Handle escape key to close overlay
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    this.hideShareOverlay();
                }
            };
            document.addEventListener('keydown', handleEscape);

            // Set up focus trap
            const cleanup = trapFocus(shareOverlay);
            
            // Store cleanup functions
            this.activeCleanup = () => {
                document.removeEventListener('keydown', handleEscape);
                cleanup();
            };

        } catch (error) {
            console.error('Error showing share overlay:', error);
            throw error;
        }
    },

    hideShareOverlay() {
        try {
            const shareOverlay = document.getElementById('shareOverlay');
            if (shareOverlay) {
                shareOverlay.style.display = 'none';
                
                // Clean up event listeners and restore focus
                if (this.activeCleanup) {
                    this.activeCleanup();
                    this.activeCleanup = null;
                }
            }
        } catch (error) {
            console.error('Error hiding share overlay:', error);
        }
    },

    sanitizeShareData(data) {
        if (!data || typeof data !== 'string') return '';
        return data.replace(/[<>"']/g, '');
    }
};

export default shareModule;
