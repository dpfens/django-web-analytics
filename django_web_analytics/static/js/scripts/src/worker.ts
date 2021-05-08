/// <reference path="../../lib/src/main.ts" />

self.addEventListener('sync', function(event: any) {
  if (event.tag == 'analytics') {
    event.waitUntil(analytics.sync());
  }
});
