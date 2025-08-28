function showShareOverlay(title, url) {
    const overlay = document.getElementById('shareOverlay');
    const shareTitle = document.getElementById('shareTitle');
    
    // Update share title
    shareTitle.textContent = title;
    
    // Update share buttons
    document.getElementById('twitterShare').href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`;
    document.getElementById('facebookShare').href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    document.getElementById('linkedinShare').href = `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
    
    // Show overlay
    overlay.style.display = 'flex';
    setTimeout(() => overlay.classList.add('active'), 10);
}

function hideShareOverlay() {
    const overlay = document.getElementById('shareOverlay');
    overlay.classList.remove('active');
    setTimeout(() => overlay.style.display = 'none', 300);
}

function copyLink() {
    const shareTitle = document.getElementById('shareTitle');
    const url = window.location.href;
    
    navigator.clipboard.writeText(url).then(() => {
        const copyButton = document.getElementById('copyButton');
        const originalText = copyButton.textContent;
        copyButton.textContent = 'Copied!';
        setTimeout(() => {
            copyButton.textContent = originalText;
        }, 2000);
    });
}
