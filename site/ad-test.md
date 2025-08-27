---
layout: with-sidebar
title: Ad Preview & Testing
permalink: /ad-test/
---

<div class="ad-test-page">
    <h1>Ad Placement Preview</h1>
    <p class="notice">This is a testing page to preview different ad placements and layouts. Use this page to verify ad rendering and responsive behavior.</p>

    <section class="test-section">
        <h2>In-Feed Ad</h2>
        <div class="sample-feed">
            <div class="feed-item">
                <h3>Sample Article 1</h3>
                <p>This is a sample article summary to demonstrate how in-feed ads appear between content items.</p>
            </div>
            
            {% include ads.html type="in-feed" %}
            
            <div class="feed-item">
                <h3>Sample Article 2</h3>
                <p>Another sample article to show content flow around ads.</p>
            </div>
        </div>
    </section>

    <section class="test-section">
        <h2>In-Article Ad</h2>
        <div class="sample-article">
            <p>This is a sample paragraph showing how in-article ads appear within content. The ad should appear naturally between paragraphs.</p>
            
            {% include ads.html type="in-article" %}
            
            <p>This paragraph comes after the in-article ad to demonstrate content flow.</p>
        </div>
    </section>

    <section class="test-section">
        <h2>Matched Content Ad</h2>
        <div class="sample-matched">
            {% include ads.html type="matched-content" %}
        </div>
    </section>

    <section class="test-section">
        <h2>Mobile Responsiveness</h2>
        <div class="device-preview">
            <div class="mobile-view">
                <h3>Mobile View</h3>
                {% include ads.html type="in-article" %}
            </div>
        </div>
    </section>
</div>

<style>
.ad-test-page {
    padding: 2rem 0;
}

.notice {
    padding: 1rem;
    background: #fff3cd;
    border: 1px solid #ffeeba;
    border-radius: 4px;
    margin: 1rem 0;
}

.test-section {
    margin: 3rem 0;
    padding: 2rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.sample-feed .feed-item {
    padding: 1rem;
    margin: 1rem 0;
    background: #f8f9fa;
    border-radius: 4px;
}

.sample-article {
    max-width: 700px;
    margin: 0 auto;
}

.device-preview {
    margin: 2rem 0;
}

.mobile-view {
    max-width: 375px;
    margin: 0 auto;
    padding: 1rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
}

@media (prefers-color-scheme: dark) {
    .test-section {
        background: rgba(255,255,255,0.02);
    }
    
    .sample-feed .feed-item {
        background: rgba(255,255,255,0.05);
    }
    
    .notice {
        background: #2d2c0d;
        border-color: #3d3c1d;
    }
}
</style>

{% include ad-analytics.html %}
