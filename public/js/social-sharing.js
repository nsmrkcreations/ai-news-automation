/**
 * Social Sharing Functionality
 */

class SocialSharing {
    constructor() {
        this.init();
    }

    init() {
        this.addSocialButtons();
        this.setupEventListeners();
    }

    addSocialButtons() {
        // Add social sharing buttons to news cards
        const newsCards = document.querySelectorAll('.news-card, .news-card-small, .news-card-large');
        
        newsCards.forEach(card => {
            if (!card.querySelector('.social-share')) {
                this.addShareButtonsToCard(card);
            }
        });
    }

    addShareButtonsToCard(card) {
        const shareContainer = document.createElement('div');
        shareContainer.className = 'social-share';
        shareContainer.innerHTML = `
            <button class="share-btn" title="Share this article">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/>
                </svg>
            </button>
            <div class="share-dropdown" style="display: none;">
                <button class="share-option twitter" data-platform="twitter">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                    </svg>
                    Twitter
                </button>
                <button class="share-option facebook" data-platform="facebook">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                    Facebook
                </button>
                <button class="share-option linkedin" data-platform="linkedin">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                    LinkedIn
                </button>
                <button class="share-option whatsapp" data-platform="whatsapp">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.465 3.488"/>
                    </svg>
                    WhatsApp
                </button>
                <button class="share-option copy" data-platform="copy">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                    Copy Link
                </button>
            </div>
        `;

        // Insert before the content div or at the end
        const contentDiv = card.querySelector('.content');
        if (contentDiv) {
            contentDiv.appendChild(shareContainer);
        } else {
            card.appendChild(shareContainer);
        }
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            // Handle share button clicks
            if (e.target.closest('.share-btn')) {
                e.preventDefault();
                e.stopPropagation();
                const shareBtn = e.target.closest('.share-btn');
                const dropdown = shareBtn.nextElementSibling;
                
                // Close other dropdowns
                document.querySelectorAll('.share-dropdown').forEach(d => {
                    if (d !== dropdown) d.style.display = 'none';
                });
                
                // Toggle current dropdown
                dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
            }
            
            // Handle share option clicks
            else if (e.target.closest('.share-option')) {
                e.preventDefault();
                e.stopPropagation();
                const option = e.target.closest('.share-option');
                const platform = option.dataset.platform;
                const card = option.closest('.news-card, .news-card-small, .news-card-large');
                
                this.shareArticle(platform, card);
                
                // Close dropdown
                option.closest('.share-dropdown').style.display = 'none';
            }
            
            // Close dropdowns when clicking outside
            else if (!e.target.closest('.social-share')) {
                document.querySelectorAll('.share-dropdown').forEach(d => {
                    d.style.display = 'none';
                });
            }
        });
    }

    shareArticle(platform, card) {
        const title = this.getArticleTitle(card);
        const url = this.getArticleUrl(card);
        const description = this.getArticleDescription(card);
        
        const shareData = {
            title: title,
            url: url,
            text: description
        };

        switch (platform) {
            case 'twitter':
                this.shareToTwitter(shareData);
                break;
            case 'facebook':
                this.shareToFacebook(shareData);
                break;
            case 'linkedin':
                this.shareToLinkedIn(shareData);
                break;
            case 'whatsapp':
                this.shareToWhatsApp(shareData);
                break;
            case 'copy':
                this.copyToClipboard(shareData.url);
                break;
        }
    }

    getArticleTitle(card) {
        const titleElement = card.querySelector('.title, h3, h4');
        return titleElement ? titleElement.textContent.trim() : 'Check out this news article';
    }

    getArticleUrl(card) {
        // Try to get URL from onclick attribute or href
        const onclick = card.getAttribute('onclick');
        if (onclick && onclick.includes('window.open')) {
            const match = onclick.match(/window\.open\(['"]([^'"]+)['"]/);
            if (match) return match[1];
        }
        
        const link = card.querySelector('a');
        if (link) return link.href;
        
        return window.location.href;
    }

    getArticleDescription(card) {
        const descElement = card.querySelector('.description, p');
        return descElement ? descElement.textContent.trim().substring(0, 200) : '';
    }

    shareToTwitter(data) {
        const text = `${data.title}\n\n${data.text}`;
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(data.url)}`;
        window.open(url, '_blank', 'width=550,height=420');
    }

    shareToFacebook(data) {
        const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(data.url)}&quote=${encodeURIComponent(data.title)}`;
        window.open(url, '_blank', 'width=550,height=420');
    }

    shareToLinkedIn(data) {
        const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(data.url)}&title=${encodeURIComponent(data.title)}&summary=${encodeURIComponent(data.text)}`;
        window.open(url, '_blank', 'width=550,height=420');
    }

    shareToWhatsApp(data) {
        const text = `${data.title}\n\n${data.text}\n\n${data.url}`;
        const url = `https://wa.me/?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
    }

    async copyToClipboard(url) {
        try {
            await navigator.clipboard.writeText(url);
            this.showCopyFeedback('Link copied to clipboard!');
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = url;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showCopyFeedback('Link copied to clipboard!');
        }
    }

    showCopyFeedback(message) {
        // Create temporary feedback element
        const feedback = document.createElement('div');
        feedback.className = 'copy-feedback';
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--accent-primary);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            z-index: 10000;
            font-weight: 500;
            box-shadow: var(--shadow-hover);
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(feedback);
            }, 300);
        }, 2000);
    }
}

// Initialize social sharing when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // Wait for news cards to be loaded
        setTimeout(() => {
            window.socialSharing = new SocialSharing();
        }, 1000);
    });
} else {
    setTimeout(() => {
        window.socialSharing = new SocialSharing();
    }, 1000);
}
