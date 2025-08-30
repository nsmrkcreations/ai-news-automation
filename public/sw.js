// Service Worker for PWA functionality
const CACHE_NAME = 'newsurgeai-v1.0.0';
const STATIC_CACHE = 'newsurgeai-static-v1.0.0';
const DYNAMIC_CACHE = 'newsurgeai-dynamic-v1.0.0';

// Static assets to cache
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/css/main.css',
    '/css/header.css',
    '/css/components.css',
    '/css/responsive.css',
    '/css/connection-status.css',
    '/js/main.js',
    '/js/utils/constants.js',
    '/js/utils/helpers.js',
    '/js/components/newsCard.js',
    '/js/components/breakingNews.js',
    '/js/components/heroSection.js',
    '/manifest.json',
    '/offline.html'
];

// Dynamic assets (news data, images)
const DYNAMIC_ASSETS = [
    '/data/news.json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Service Worker: Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('Service Worker: Static assets cached');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Failed to cache static assets', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Handle different types of requests
    if (request.method === 'GET') {
        // Static assets - cache first strategy
        if (STATIC_ASSETS.includes(url.pathname)) {
            event.respondWith(cacheFirst(request));
        }
        // News data - network first strategy
        else if (url.pathname === '/data/news.json') {
            event.respondWith(networkFirst(request));
        }
        // Images - cache first with fallback
        else if (request.destination === 'image') {
            event.respondWith(cacheFirstWithFallback(request));
        }
        // Other requests - network first
        else {
            event.respondWith(networkFirst(request));
        }
    }
});

// Cache first strategy (for static assets)
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Cache first strategy failed:', error);
        return new Response('Offline content not available', { status: 503 });
    }
}

// Network first strategy (for dynamic content)
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Network request failed, trying cache:', error);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/offline.html');
        }
        
        return new Response('Content not available offline', { status: 503 });
    }
}

// Cache first with fallback (for images)
async function cacheFirstWithFallback(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('Image request failed:', error);
        // Return a fallback image or placeholder
        return new Response(
            '<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#1a1a2e"/><text x="50%" y="50%" text-anchor="middle" fill="#e94560" font-family="Arial" font-size="16">Image unavailable</text></svg>',
            { headers: { 'Content-Type': 'image/svg+xml' } }
        );
    }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Service Worker: Background sync triggered');
    
    if (event.tag === 'background-news-sync') {
        event.waitUntil(syncNewsData());
    }
});

// Sync news data when back online
async function syncNewsData() {
    try {
        console.log('Service Worker: Syncing news data');
        const response = await fetch('/data/news.json');
        if (response.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put('/data/news.json', response.clone());
            
            // Notify clients about updated data
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
                client.postMessage({
                    type: 'NEWS_DATA_UPDATED',
                    timestamp: Date.now()
                });
            });
        }
    } catch (error) {
        console.error('Service Worker: Failed to sync news data', error);
    }
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Service Worker: Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New breaking news available!',
        icon: '/images/icon-192x192.png',
        badge: '/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Read Now',
                icon: '/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('NewSurgeAI - Breaking News', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Service Worker: Notification clicked');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            self.clients.openWindow('/')
        );
    }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker: Message received', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_NEWS_DATA') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE)
                .then(cache => cache.put('/data/news.json', new Response(JSON.stringify(event.data.data))))
        );
    }
});

// Error handling
self.addEventListener('error', (event) => {
    console.error('Service Worker: Error occurred', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
    console.error('Service Worker: Unhandled promise rejection', event.reason);
});