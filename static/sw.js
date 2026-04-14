const CACHE_NAME = 'cuacakita-v1';

self.addEventListener('install', (event) => {
    // Force the service worker to become the active service worker
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    // Take control of all open pages immediately
    event.waitUntil(clients.claim());
});

self.addEventListener('push', function(event) {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: data.icon || '/static/icons/icon-192x192.png',
            badge: '/static/icons/icon-192x192.png',
            data: {
                url: data.url || '/'
            }
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});

// Handle subscription renewal
self.addEventListener('pushsubscriptionchange', function(event) {
    console.log('Push subscription expired, renewing...');
    event.waitUntil(
        fetch('/api/vapid-public-key')
            .then(res => res.json())
            .then(data => {
                return self.registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(data.publicKey)
                });
            })
            .then(subscription => {
                return fetch('/api/subscribe', {
                    method: 'POST',
                    body: JSON.stringify({ subscription: subscription }),
                    headers: { 'Content-Type': 'application/json' }
                });
            })
            .catch(err => console.error('Failed to renew subscription', err))
    );
});

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = self.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}
