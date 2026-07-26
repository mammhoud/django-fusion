import { BaseManager } from './base-manager.js';

export class ModuleManager extends BaseManager {
    constructor(config = {}) {
        super({
            cacheModules:    true,
            debug:           false,
            lazyLoad:        true,
            skipMissing:     true,
            batchSize:       4,
            prioritySorting: true,
            prefetchOnIdle:  false,
            retryFailed:     false,
            maxRetries:      2,
            ...config,
        });

        this.modules       = new Map();
        this.cache         = new Map();
        this.loadedModules = new Map();
        this.loadingModules = new Set();
        this.failedModules  = new Set();

        this.metrics = {
            loadTimes:     new Map(),
            cacheHits:     0,
            cacheMisses:   0,
            retryAttempts: 0,
            prefetches:    0,
        };
    }

    // ── Registration ─────────────────────────────────────────

    registerModule(id, config) {
        if (!config.loader && !config.component) {
            throw new Error(`Module "${id}" must have a loader or component`);
        }
        this.modules.set(id, {
            id,
            name:         id,
            priority:     50,
            alwaysLoad:   false,
            category:     'general',
            dependencies: [],
            requires:     [],
            critical:     false,
            version:      '1.0.0',
            description:  '',
            tags:         [],
            condition:    () => true,
            onLoad:       null,
            onError:      null,
            ...config,
        });
        this.log(`📦 Registered: ${id}`);
        return this;
    }

    registerModules(modules) {
        modules.forEach(m => this.registerModule(m.id, m));
        // Warn about missing deps
        for (const [id, cfg] of this.modules) {
            const missing = cfg.dependencies.filter(d => !this.modules.has(d));
            if (missing.length) this.log(`⚠️ ${id} missing deps: ${missing.join(', ')}`);
        }
        return this;
    }

    // ── Loading ──────────────────────────────────────────────

    async load(moduleIds, context = {}) {
        const ids = Array.isArray(moduleIds) ? moduleIds : [moduleIds];
        const filtered = ids.filter(id => {
            const cfg = this.modules.get(id);
            return cfg && cfg.condition(context);
        });
        const resolved = this.resolveDependencies(filtered);
        const sorted   = this.sortByPriority(resolved);
        return this.loadBatchWithProgress(sorted, context);
    }

    resolveDependencies(ids) {
        const resolved = new Set();
        const seen     = new Set();
        const resolve  = (id) => {
            if (seen.has(id)) return;
            seen.add(id);
            const cfg = this.modules.get(id);
            if (!cfg) return;
            cfg.dependencies.forEach(dep => { if (!resolved.has(dep)) resolve(dep); });
            resolved.add(id);
        };
        ids.forEach(resolve);
        return [...resolved];
    }

    sortByPriority(ids) {
        return [...ids].sort((a, b) => {
            const pa = this.modules.get(a)?.priority ?? 50;
            const pb = this.modules.get(b)?.priority ?? 50;
            return pa - pb;
        });
    }

    async loadBatchWithProgress(ids, context) {
        const results = [];
        const total   = ids.length;
        this.dispatch('modules:loading:start', { total, modules: ids });

        for (let i = 0; i < ids.length; i += this.config.batchSize) {
            const batch = ids.slice(i, i + this.config.batchSize);
            this.dispatch('modules:batch:start', { batch, index: i, total });
            const batchResults = await this._loadBatch(batch, context);
            results.push(...batchResults);
            this.dispatch('modules:batch:complete', {
                batch,
                loaded: batchResults.length,
                failed: batch.length - batchResults.length,
            });
        }

        this.dispatch('modules:loading:complete', { loaded: results.length, total });
        return results;
    }

    async _loadBatch(ids, context) {
        const settled = await Promise.allSettled(ids.map(id => this.loadOne(id, context)));
        return settled.filter(r => r.status === 'fulfilled').map(r => r.value);
    }

    async loadOne(moduleId, context = {}) {
        // Cache hit
        if (this.config.cacheModules && this.cache.has(moduleId)) {
            this.metrics.cacheHits++;
            this.dispatch('module:cache:hit', { moduleId });
            return this.cache.get(moduleId);
        }
        // Already loading — wait
        if (this.loadingModules.has(moduleId)) return this._waitFor(moduleId);
        // Previously failed, no retry
        if (this.failedModules.has(moduleId) && !this.config.retryFailed) {
            throw new Error(`Module "${moduleId}" previously failed`);
        }

        const cfg = this.modules.get(moduleId);
        if (!cfg) throw new Error(`Module "${moduleId}" not registered`);

        this.loadingModules.add(moduleId);
        this.metrics.cacheMisses++;
        const t0 = performance.now();

        try {
            this.dispatch('module:loading:start', { moduleId, cfg });

            const attempt = async (n = 1) => {
                try {
                    const mod      = await this._import(cfg, context);
                    const instance = this._extract(mod, cfg);
                    const init     = await this._initialize(moduleId, instance, context);

                    await cfg.onLoad?.(init, context);

                    if (this.config.cacheModules) this.cache.set(moduleId, init);
                    this.loadedModules.set(moduleId, init);
                    this.failedModules.delete(moduleId);

                    const loadTime = performance.now() - t0;
                    this.metrics.loadTimes.set(moduleId, loadTime);
                    this.dispatch('module:loaded', { moduleId, instance: init, loadTime, attempt: n });
                    return init;
                } catch (err) {
                    await cfg.onError?.(err, n);
                    if (n <= this.config.maxRetries && cfg.critical !== false) {
                        this.metrics.retryAttempts++;
                        this.dispatch('module:retry', { moduleId, attempt: n + 1, error: err.message });
                        return attempt(n + 1);
                    }
                    throw err;
                }
            };

            return await attempt();
        } catch (err) {
            this.failedModules.add(moduleId);
            if (cfg.fallback) {
                try {
                    const fb = await cfg.fallback();
                    this.dispatch('module:fallback:used', { moduleId });
                    return fb;
                } catch { /* ignore fallback error */ }
            }
            if (cfg.critical) {
                this.dispatch('module:critical:failed', { moduleId, error: err.message });
                throw new Error(`Critical module "${moduleId}" failed: ${err.message}`);
            }
            this.handleError(`Failed to load module "${moduleId}"`, err);
            throw err;
        } finally {
            this.loadingModules.delete(moduleId);
        }
    }

    // ── Import / Extract / Init ──────────────────────────────

    async _import(cfg, context) {
        if (cfg.loader)    return cfg.loader(context);
        if (cfg.component) return { default: cfg.component };
        if (cfg.url)       return import(/* webpackIgnore: true */ cfg.url);
        throw new Error(`No loader for module "${cfg.id}"`);
    }

    _extract(mod, cfg) {
        if (mod.default) {
            if (typeof mod.default === 'function') return mod.default;
            if (mod.default?.init || mod.default?.initialize) return mod.default;
            return mod.default;
        }
        if (cfg.exportName && mod[cfg.exportName]) return mod[cfg.exportName];
        const cls = cfg.name?.replace(/\s+/g, '');
        if (cls && mod[cls]) return mod[cls];
        return mod;
    }

    async _initialize(moduleId, instance, context) {
        if (!instance) return instance;
        const ctx = { ...context, loader: this, log: this.log.bind(this), dispatch: this.dispatch.bind(this) };
        try {
            if (typeof instance.init         === 'function') await instance.init(ctx);
            else if (typeof instance.initialize === 'function') await instance.initialize(ctx);
            else if (typeof instance.setup      === 'function') await instance.setup(ctx);
            else if (typeof instance            === 'function') {
                const obj = new instance(ctx);
                await obj.init?.(ctx);
                return obj;
            }
        } catch (err) {
            this.log(`⚠️ ${moduleId} init error: ${err.message}`);
        }
        return instance;
    }

    _waitFor(moduleId, timeout = 10_000) {
        return new Promise((resolve, reject) => {
            const start = Date.now();
            const tick  = setInterval(() => {
                if (this.loadedModules.has(moduleId)) {
                    clearInterval(tick);
                    resolve(this.loadedModules.get(moduleId));
                } else if (Date.now() - start > timeout) {
                    clearInterval(tick);
                    reject(new Error(`Timeout waiting for module "${moduleId}"`));
                }
            }, 50);
        });
    }

    // ── Prefetch ─────────────────────────────────────────────

    async prefetch(ids, priority = 'low') {
        if (!this.config.prefetchOnIdle || typeof requestIdleCallback !== 'function') return;
        return new Promise(resolve => {
            requestIdleCallback(async () => {
                this.metrics.prefetches++;
                const pending = ids.filter(id =>
                    !this.loadedModules.has(id) && !this.cache.has(id) && !this.loadingModules.has(id)
                );
                if (!pending.length) { resolve([]); return; }
                this.dispatch('modules:prefetch:start', { modules: pending, priority });
                const results = await Promise.allSettled(pending.map(async id => {
                    try {
                        const mod = await this._import(this.modules.get(id), {});
                        this.cache.set(id, mod);
                        return { id, success: true };
                    } catch (err) {
                        return { id, success: false, error: err.message };
                    }
                }));
                this.dispatch('modules:prefetch:complete', { results: results.map(r => r.value) });
                resolve(results.map(r => r.value));
            }, { timeout: 5000 });
        });
    }

    // ── Query ────────────────────────────────────────────────

    async getModule(id, fallback = null) {
        try {
            if (this.loadedModules.has(id)) return this.loadedModules.get(id);
            if (this.cache.has(id))         return this.cache.get(id);
            return await this.loadOne(id);
        } catch {
            return fallback;
        }
    }

    hasModule(id) {
        return this.modules.has(id) || this.loadedModules.has(id) || this.cache.has(id);
    }

    clearCache(pattern = null) {
        let cleared = 0;
        if (pattern) {
            const test = typeof pattern === 'function' ? pattern : k => new RegExp(pattern).test(k);
            for (const [k] of this.cache) {
                if (test(k)) { this.cache.delete(k); this.loadedModules.delete(k); cleared++; }
            }
        } else {
            cleared = this.cache.size;
            this.cache.clear();
            this.loadedModules.clear();
        }
        this.dispatch('cache:cleared', { cleared, pattern });
        return cleared;
    }

    // ── Metrics ──────────────────────────────────────────────

    getEnhancedMetrics() {
        const total = this.metrics.cacheHits + this.metrics.cacheMisses;
        const times = [...this.metrics.loadTimes.values()];
        return {
            registered:  this.modules.size,
            loaded:      this.loadedModules.size,
            cached:      this.cache.size,
            loading:     this.loadingModules.size,
            failed:      this.failedModules.size,
            cacheHits:   this.metrics.cacheHits,
            cacheMisses: this.metrics.cacheMisses,
            hitRate:     total > 0 ? `${(this.metrics.cacheHits / total * 100).toFixed(1)}%` : '0%',
            retries:     this.metrics.retryAttempts,
            prefetches:  this.metrics.prefetches,
            avgLoadTime: times.length ? times.reduce((a, b) => a + b, 0) / times.length : 0,
        };
    }
}

// ── Singleton ─────────────────────────────────────────────────
export const moduleManager = new ModuleManager();

if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        if (window.app) moduleManager.init(window.app).catch(console.error);
        window.moduleManager = moduleManager;
    });
}

export default moduleManager;
