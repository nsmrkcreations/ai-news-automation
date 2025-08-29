// Service Worker with automatic cache invalidation
const VERSION = new Date().toISOString();
const CACHE_NAME = `newssurge-${VERSION}`;
const DYNAMIC_CACHE = 'newssurge-dynamic';

// Assets that should be cached immediately
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/css/styles.css',
  '/js/main.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
];

// Assets that should never be cached
const NEVER_CACHE = [
  '/data/news.json',  // Always get fresh news
  '/api/',            // Never cache API calls
];

// Install event - cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches and claim clients
self.addEventListener('activate', event => {
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(name => name.startsWith('newssurge-') && name !== CACHE_NAME && name !== DYNAMIC_CACHE)
            .map(name => caches.delete(name))
        );
      }),
      // Clean dynamic cache if it's a new day
      caches.open(DYNAMIC_CACHE).then(cache => {
        return cache.keys().then(requests => {
          return Promise.all(
            requests.map(request => cache.delete(request))
          );
        });
      }),
      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - smart caching strategy
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Never cache certain paths
  if (NEVER_CACHE.some(path => url.pathname.includes(path))) {
    event.respondWith(fetch(event.request));
    return;
  }

  // Network-first strategy for HTML pages
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match('/offline.html'))
    );
    return;
  }

  // Cache-first strategy for static assets
  if (STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
    return;
  }

  // Network-first with dynamic caching for everything else
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone the response as it can only be used once
        const responseToCache = response.clone();
        
        // Cache successful responses
        if (response.ok) {
          caches.open(DYNAMIC_CACHE)
            .then(cache => cache.put(event.request, responseToCache));
        }
        
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
