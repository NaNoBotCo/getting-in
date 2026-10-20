/* Keeps the pages opened once readable without internet. Network first; the cached copy when there is no network. */
var CACHE = "getting-in-v2";
var CORE = ["./", "assets/style.css", "assets/app.js", "assets/icon.svg", "manifest.webmanifest"];
self.addEventListener("install", function (e) { e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); })); });
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(function (r) {
    if (r.ok && r.type === "basic") { var copy = r.clone(); e.waitUntil(caches.open(CACHE).then(function (c) { return c.put(e.request, copy); })); }
    return r;
  }).catch(function () {
    return caches.match(e.request, { ignoreSearch: true }).then(function (hit) {
      if (hit) return hit;
      if (e.request.mode === "navigate") return caches.match("./").then(function (home) { return home || new Response("Offline", { status: 503 }); });
      return new Response("", { status: 503, statusText: "Offline" });
    });
  }));
});
