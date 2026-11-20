/* Axiogram: εφαρμογή (service worker).
   Πάντα δοκιμάζει πρώτα το δίκτυο, ώστε οι τιμές να είναι οι τελευταίες.
   Αν δεν υπάρχει internet, δείχνει ό,τι αποθηκεύτηκε την τελευταία φορά. */
var CACHE = "agora-v38";
var SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.pathname.indexOf("/__/") === 0) return; // σελίδες σύνδεσης Google/Firebase
  if (url.origin !== self.location.origin) return; // Firebase, γραμματοσειρές κ.λπ. απευθείας
  e.respondWith(
    fetch(req).then(function (res) {
      if (res && res.ok) {
        var copy = res.clone();
        var key = url.origin + url.pathname; // χωρίς ?t=… ώστε να μένει ένα αντίγραφο ανά αρχείο
        caches.open(CACHE).then(function (c) { c.put(key, copy); });
      }
      return res;
    }).catch(function () {
      return caches.match(url.origin + url.pathname).then(function (r) {
        return r || caches.match("index.html");
      });
    })
  );
});

/* ειδοποιήσεις τιμών (Firebase Cloud Messaging, μηνύματα μόνο με δεδομένα) */
self.addEventListener("push", function (e) {
  var j = {};
  try { j = e.data ? e.data.json() : {}; } catch (x) { j = { data: { title: "Axiogram", body: e.data ? e.data.text() : "" } }; }
  var d = j.data || {}, n = j.notification || {};
  var title = d.title || n.title || "Axiogram";
  e.waitUntil(self.registration.showNotification(title, {
    body: d.body || n.body || "",
    icon: "icons/icon-192.png",
    badge: "icons/favicon-32.png",
    tag: d.tag || undefined,
    renotify: !!d.tag,
    data: { url: d.url || "./" }
  }));
});
self.addEventListener("notificationclick", function (e) {
  e.notification.close();
  var url = new URL((e.notification.data && e.notification.data.url) || "./", self.location.href).href;
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      if (c.url.indexOf(self.location.origin) === 0 && "focus" in c) { if ("navigate" in c) c.navigate(url).catch(function () {}); return c.focus(); }
    }
    return self.clients.openWindow(url);
  }));
});
