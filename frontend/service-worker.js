/*
  Garden & Grace — The Good Neighbor Guard
  Built by Christopher Hughes · Sacramento, CA
  Created with the help of AI collaborators (Claude · GPT · Gemini · Groq)
  Truth · Safety · We Got Your Back
*/

// ── Bump this version every deploy to auto-bust Aubrey's cache ──
const CACHE_NAME = "garden-grace-v5";

const STATIC_ASSETS = [
  "/",
  "/static/css/app.css",
  "/static/js/app.js",
  "/static/js/auth.js",
  "/static/js/garden.js",
  "/static/js/birds.js",
  "/static/js/fishing.js",
  "/static/js/recipes.js",
  "/static/js/build.js",
  "/static/manifest.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  // API calls: always network, never cache
  if (event.request.url.includes("/auth/") || event.request.url.includes("/features/")) {
    return;
  }

  // Static assets: network first, fall back to cache
  // This means Aubrey always gets fresh files if she has signal,
  // and the cached version only kicks in if she's offline
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Save fresh copy to cache while we're at it
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
