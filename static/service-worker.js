self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('utang-tracker').then(cache => {
      return cache.addAll([
        '/',
        '/static/styles.css',
        '/static/script.js',
        '/static/manifest.json'
      ]);
    })
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(response => response || fetch(e.request))
  );
});
