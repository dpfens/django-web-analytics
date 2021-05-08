class IndexedDBStorageAdapter {
    constructor(database, version) {
        this.database = database;
        this.version = version;
        var self = this;
        this.dbPromise = new Promise(function (resolve, reject) {
            const request = indexedDB.open(database, version);
            request.onupgradeneeded = self.upgrade.bind(self);
            request.onsuccess = function (event) {
                const db = event.target.result;
                resolve(db);
            };
            request.onerror = (e) => {
                console.log(e.error);
                reject(e);
            };
        });
    }
    upgrade(event) {
        throw Error('A custom upgrade function must be implemented to handle ' + event.toString());
    }
    keyCursor(storeName, indexName) {
        return this.dbPromise.then(function (db) {
            const transaction = db.transaction(storeName, "readonly"), store = transaction.objectStore(storeName), index = store.index(indexName);
            transaction.oncomplete = function () { };
            return new Promise(function (resolve, reject) {
                var request = index.openKeyCursor();
                request.onsuccess = function (event) {
                    resolve(event);
                };
                request.onerror = function (event) {
                    reject(event);
                };
            });
        });
    }
    getAll(storeName, indexName, range) {
        return this.dbPromise.then(function (db) {
            const transaction = db.transaction(storeName, "readonly"), store = transaction.objectStore(storeName);
            transaction.oncomplete = function () { };
            if (indexName && range) {
                var index = store.index(indexName), request = index.openCursor(range);
                return new Promise(function (resolve, reject) {
                    request.onsuccess = function (event) {
                        resolve(event.target.result);
                    };
                    request.onerror = function (event) {
                        reject(event);
                    };
                });
            }
            var request = store.getAll();
            return new Promise(function (resolve, reject) {
                request.onsuccess = function (event) {
                    resolve(event.target.result);
                };
                request.onerror = function (event) {
                    reject(event);
                };
            });
        });
    }
    get(storeName, ...ids) {
        return this.dbPromise.then(function (db) {
            const transaction = db.transaction(storeName, "readonly"), store = transaction.objectStore(storeName);
            transaction.oncomplete = function () { };
            var promises = [];
            for (var i = 0; i < ids.length; i++) {
                const request = store.get(ids[i]), prom = new Promise(function (resolve, reject) {
                    request.onsuccess = (response) => { resolve(response); };
                    request.onerror = (response) => { reject(response); };
                });
                promises.push(prom);
            }
            return Promise.all(promises);
        });
    }
    add(storeName, ...items) {
        return this.dbPromise.then(function (db) {
            const transaction = db.transaction(storeName, "readwrite"), store = transaction.objectStore(storeName);
            var promises = [];
            for (var i = 0; i < items.length; i++) {
                const request = store.add(items[i]), prom = new Promise(function (resolve, reject) {
                    request.onsuccess = (response) => { resolve(response); };
                    request.onerror = (response) => { reject(response); };
                });
                promises.push(prom);
            }
            return Promise.all(promises);
        });
    }
    update(storeName, ...items) {
        return this.dbPromise.then(function (db) {
            const transaction = db.transaction(storeName, "readwrite"), store = transaction.objectStore(storeName);
            transaction.oncomplete = function () { };
            var promises = [];
            for (var i = 0; i < items.length; i++) {
                var request = store.put(items[i]), prom = new Promise(function (resolve, reject) {
                    request.onsuccess = function (event) {
                        resolve(event.target.result);
                    };
                    request.onerror = function (event) {
                        reject(event);
                    };
                });
                promises.push(prom);
            }
            return Promise.all(promises);
        });
    }
    delete(storeName, ...ids) {
        return this.dbPromise.then(function (db) {
            const transaction = db.transaction(storeName, "readwrite"), store = transaction.objectStore(storeName);
            transaction.oncomplete = function () { };
            var promises = [];
            for (var i = 0; i < ids.length; i++) {
                var request = store.delete(ids[i]), prom = new Promise(function (resolve, reject) {
                    request.onsuccess = function (event) {
                        resolve(event.target.result);
                    };
                    request.onerror = function (event) {
                        reject(event);
                    };
                });
                promises.push(prom);
            }
            return Promise.all(promises);
        });
    }
}
class StorageAdapter {
    constructor(storage, key) {
        this.key = key;
        this.storage = storage;
        this.data = storage.get(key);
    }
    getAll() {
        var output = [];
        for (var id in this.data) {
            var item = this.data[id];
            output.push(item);
        }
        return output;
    }
    get(id) {
        return this.data[id];
    }
    add(item) {
        var keys = Object.keys(this.data);
        this.data[keys.length] = item;
        this.storage.setItem(this.key, this.data);
    }
    update(id, item) {
        if (id) {
            this.data[id] = item;
        }
        this.storage.setItem(this.key, this.data);
    }
    delete(...ids) {
        for (var i = 0; i < ids.length; i++) {
            var id = ids[i];
            if (id in this.data) {
                delete this.data[id];
            }
        }
        this.storage.setItem(this.key, this.data);
    }
}
class AsynchronousStorageAdapter {
    constructor(storage, key) {
        this.key = key;
        this.storage = storage;
        this.data = storage.get(key);
    }
    getAll() {
        const self = this;
        return Promise.resolve().then(function () {
            var output = [];
            for (var id in self.data) {
                var item = self.data[id];
                output.push(item);
            }
            return output;
        });
    }
    get(id) {
        var self = this;
        return Promise.resolve().then(function () {
            return self.data[id];
        });
    }
    add(item) {
        var self = this;
        return Promise.resolve().then(function () {
            var keys = Object.keys(self.data);
            var openKey = keys.length;
            while (openKey in self.data) {
                openKey++;
            }
            self.data[openKey] = item;
            self.storage.setItem(self.key, self.data);
        });
    }
    update(id, item) {
        if (id) {
            this.data[id] = item;
        }
        const self = this;
        return Promise.resolve().then(function () {
            self.storage.setItem(self.key, self.data);
        });
    }
    delete(...ids) {
        for (var i = 0; i < ids.length; i++) {
            var id = ids[i];
            if (id in this.data) {
                delete this.data[id];
            }
        }
        const self = this;
        return Promise.resolve().then(function () {
            self.storage.setItem(self.key, self.data);
        });
    }
}
var analytics;
(function (analytics) {
    function isDoNotTrack() {
        var value = window.navigator.doNotTrack, output = value === '1';
        return output;
    }
    function isAllowedToTrack() {
        return !isDoNotTrack() && !window.doNotTrack;
    }
    analytics.isAllowedToTrack = isAllowedToTrack;
})(analytics || (analytics = {}));
var analytics;
(function (analytics) {
    function recur(obj) {
        var result = {}, _tmp;
        for (var i in obj) {
            // enabledPlugin is too nested, also skip functions
            if (i === 'enabledPlugin' || typeof obj[i] === 'function') {
                continue;
            }
            else if (typeof obj[i] === 'object') {
                // get props recursively
                _tmp = recur(obj[i]);
                // if object is not {}
                if (Object.keys(_tmp).length) {
                    result[i] = _tmp;
                }
            }
            else {
                // string, number or boolean
                result[i] = obj[i];
            }
        }
        return result;
    }
    function gatherLocation() {
        return recur(window.location);
    }
    function gatherScreen() {
        let output = recur(window.screen);
        return output;
    }
    function gatherNavigation() {
        let output = recur(window.navigator);
        return output;
    }
    function gatherPosition() {
        var data = {
            'scrollTop': document.documentElement.scrollTop,
            'scrollLeft': document.documentElement.scrollLeft,
        };
        return data;
    }
    function gather() {
        return {
            "referrer": document.referrer,
            "documentURL": document.URL,
            "title": document.title,
            "navigation": gatherNavigation(),
            "screen": gatherScreen(),
            "location": gatherLocation(),
            "position": gatherPosition()
        };
    }
    analytics.gather = gather;
})(analytics || (analytics = {}));
/// <reference path="storage.ts" />
/// <reference path="privacy.ts" />
/// <reference path="data.ts" />
var analytics;
(function (analytics) {
    const token = '{{ csrf_token }}';
    function initialize() {
        navigator.serviceWorker.register('/.js');
    }
    analytics.initialize = initialize;
    let EventTypes;
    (function (EventTypes) {
        EventTypes[EventTypes["Error"] = 0] = "Error";
        EventTypes[EventTypes["PageView"] = 1] = "PageView";
        EventTypes[EventTypes["Interaction"] = 2] = "Interaction";
        EventTypes[EventTypes["Conversion"] = 3] = "Conversion";
        EventTypes[EventTypes["Unknown"] = 4] = "Unknown";
    })(EventTypes || (EventTypes = {}));
    class AnalyticsEventStorageAdapter extends IndexedDBStorageAdapter {
        upgrade(event) {
            let db = event.target.result, store = 'event', options = {
                keyPath: 'id',
                autoIncrement: true
            };
            db.createObjectStore(store, options);
        }
    }
    analytics.eventAdapter = new AnalyticsEventStorageAdapter('analytics', 1);
    function event(name, types, categories, value, data) {
        if (!analytics.isAllowedToTrack()) {
            return;
        }
        const now = new Date(), requestData = analytics.gather(), payLoad = {
            'name': name,
            'types': types,
            'categories': categories,
            'value': value,
            'request': requestData,
            'datetime': now,
            'data': data
        };
        return sendEvent(payLoad).then(function (response) {
            if (response.error) {
                analytics.eventAdapter.add('event', payLoad).then(function () { });
            }
        }).catch(function () {
            analytics.eventAdapter.add('event', payLoad).then(function () { });
        });
    }
    analytics.event = event;
    function sendEvent(data) {
        const url = "{% url 'webanalytics:event' %}", fetchOptions = {
            headers: {
                "X-CSRFToken": token,
                "Accept": "application/json",
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            method: 'POST'
        };
        return fetch(url, fetchOptions).then(function (response) {
            return response.json();
        });
    }
    analytics.sendEvent = sendEvent;
    function sync() {
        return analytics.eventAdapter.getAll('event')
            .then(function (values) {
            var promises = [];
            for (var i = 0; i < values.length; i++) {
                var value = values[i], prom = analytics.sendEvent(value)
                    .then(function (response) {
                    if (!response.error) {
                        return analytics.eventAdapter.delete('event', value.id);
                    }
                });
                promises.push(prom);
            }
            return Promise.all(promises);
        });
    }
    analytics.sync = sync;
    function sendPerformances() {
        var payload = [], entries = window.performance.getEntries();
        for (var i = 0; i < entries.length; i++) {
            var entry = entries[i].toJSON();
            payload.push(entry);
        }
        const url = "{% url 'webanalytics:performance' %}", fetchOptions = {
            headers: {
                "X-CSRFToken": token,
                "Accept": "application/json",
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            method: 'POST'
        };
        return fetch(url, fetchOptions).then(function (response) {
            return response.json();
        });
    }
    analytics.sendPerformances = sendPerformances;
})(analytics || (analytics = {}));
//# sourceMappingURL=analytics.js.map