/**
 * Browser client for the Loop-CRM django-bolt API.
 *
 * Access and refresh tokens are kept in sessionStorage by default. A storage
 * adapter can be injected for tests or an application-owned vault. The client
 * never logs token values and retries a protected request at most once.
 */

export interface StoredAuthSession {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  refreshExpiresAt?: number;
  role?: string;
}

export interface TokenResponse {
  token: string;
  refresh_token: string;
  token_type: 'Bearer' | string;
  expires_in: number;
  refresh_expires_in?: number;
  role?: string;
}

export interface StorageAdapter {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export interface BoltApiClientOptions {
  baseUrl?: string;
  apiPrefix?: string;
  fallbackPrefix?: string;
  storage?: StorageAdapter;
  storageKey?: string;
  fetchImpl?: typeof fetch;
  clock?: () => number;
  refreshSkewSeconds?: number;
}

export interface RequestOptions extends RequestInit {
  auth?: boolean;
  retry401?: boolean;
}

const DEFAULT_STORAGE_KEY = 'loop-crm.auth.v1';

class MemoryStorage implements StorageAdapter {
  private values = new Map<string, string>();

  getItem(key: string): string | null {
    return this.values.get(key) ?? null;
  }

  setItem(key: string, value: string): void {
    this.values.set(key, value);
  }

  removeItem(key: string): void {
    this.values.delete(key);
  }
}

function browserStorage(): StorageAdapter {
  if (typeof window === 'undefined') return new MemoryStorage();
  try {
    return window.sessionStorage;
  } catch {
    return new MemoryStorage();
  }
}

function environmentValue(name: string, fallback: string): string {
  const environment = (import.meta as ImportMeta & { env?: Record<string, string> }).env;
  return environment?.[name] ?? fallback;
}

function normalizePrefix(prefix: string): string {
  if (!prefix) return '';
  return `/${prefix.replace(/^\/+|\/+$/g, '')}`;
}

function decodeExpiry(token: string): number | undefined {
  try {
    const payload = token.split('.')[1];
    if (!payload) return undefined;
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=');
    const claims = JSON.parse(atob(padded)) as { exp?: number };
    return typeof claims.exp === 'number' ? claims.exp * 1000 : undefined;
  } catch {
    return undefined;
  }
}

export class BoltApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, payload: unknown) {
    super(`Loop CRM API request failed (${status})`);
    this.name = 'BoltApiError';
    this.status = status;
    this.payload = payload;
  }
}

export class BoltApiClient {
  readonly baseUrl: string;
  readonly apiPrefix: string;
  readonly fallbackPrefix: string;

  private readonly storage: StorageAdapter;
  private readonly storageKey: string;
  private readonly fetchImpl: typeof fetch;
  private readonly clock: () => number;
  private readonly refreshSkewSeconds: number;
  private refreshInFlight: Promise<boolean> | null = null;
  private listeners = new Set<(session: StoredAuthSession | null) => void>();

  constructor(options: BoltApiClientOptions = {}) {
    this.baseUrl = (options.baseUrl ?? environmentValue('PUBLIC_BACKEND_URL', '')).replace(/\/$/, '');
    this.apiPrefix = normalizePrefix(options.apiPrefix ?? environmentValue('PUBLIC_API_PREFIX', '/bolt'));
    this.fallbackPrefix = normalizePrefix(options.fallbackPrefix ?? environmentValue('PUBLIC_API_FALLBACK_PREFIX', '/apis/core'));
    this.storage = options.storage ?? browserStorage();
    this.storageKey = options.storageKey ?? DEFAULT_STORAGE_KEY;
    this.fetchImpl = options.fetchImpl ?? fetch;
    this.clock = options.clock ?? (() => Date.now());
    this.refreshSkewSeconds = options.refreshSkewSeconds ?? 30;
  }

  get session(): StoredAuthSession | null {
    const serialized = this.storage.getItem(this.storageKey);
    if (!serialized) return null;
    try {
      const session = JSON.parse(serialized) as StoredAuthSession;
      if (!session.accessToken || !session.refreshToken || !session.expiresAt) {
        this.clearSession();
        return null;
      }
      return session;
    } catch {
      this.clearSession();
      return null;
    }
  }

  get authenticated(): boolean {
    return this.session !== null;
  }

  onAuthChange(listener: (session: StoredAuthSession | null) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  async login(subject: string, role = 'viewer', ttl?: number): Promise<StoredAuthSession> {
    const body = { subject, role, ...(ttl ? { ttl } : {}) };
    let response: Response;
    let usedFallback = false;
    try {
      response = await this.send(this.apiPrefix, '/auth/token', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      });
    } catch {
      usedFallback = true;
      response = await this.send(this.fallbackPrefix, '/auth/token', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      });
    }
    if (!response.ok && !usedFallback && this.fallbackPrefix !== this.apiPrefix) {
      response = await this.send(this.fallbackPrefix, '/auth/token', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: { 'Content-Type': 'application/json' },
      });
    }
    const payload = await this.parse<TokenResponse>(response);
    if (!response.ok) throw new BoltApiError(response.status, payload);
    return this.storeTokenResponse(payload);
  }

  async refresh(): Promise<boolean> {
    if (this.refreshInFlight) return this.refreshInFlight;
    const current = this.session;
    if (!current?.refreshToken) return false;

    this.refreshInFlight = this.rotateRefreshToken(current.refreshToken).finally(() => {
      this.refreshInFlight = null;
    });
    return this.refreshInFlight;
  }

  logout(): void {
    this.clearSession();
  }

  async ensureAccessToken(): Promise<string | null> {
    const current = this.session;
    if (!current) return null;
    const refreshAt = this.clock() + this.refreshSkewSeconds * 1000;
    if (current.expiresAt > refreshAt) return current.accessToken;
    return (await this.refresh()) ? this.session?.accessToken ?? null : null;
  }

  async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { auth = true, retry401 = true, ...init } = options;
    const accessToken = auth ? await this.ensureAccessToken() : null;
    let response: Response;

    try {
      response = await this.send(this.apiPrefix, path, init, accessToken);
    } catch (error) {
      if (this.fallbackPrefix === this.apiPrefix) throw error;
      response = await this.send(this.fallbackPrefix, path, init, null);
    }

    if (response.status === 401 && retry401 && auth) {
      if (await this.refresh()) {
        response = await this.send(this.apiPrefix, path, init, this.session?.accessToken ?? null);
      }
      if (response.status === 401 && this.fallbackPrefix !== this.apiPrefix) {
        this.clearSession();
        response = await this.send(this.fallbackPrefix, path, init, null);
      }
      if (response.status === 401) this.clearSession();
    } else if ([404, 405, 501].includes(response.status) && this.fallbackPrefix !== this.apiPrefix) {
      response = await this.send(this.fallbackPrefix, path, init, null);
    }

    const payload = await this.parse<T>(response);
    if (!response.ok) throw new BoltApiError(response.status, payload);
    return payload;
  }

  get<T>(path: string, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(path, { ...options, method: 'GET' });
  }

  post<T>(path: string, body: unknown, options: RequestOptions = {}): Promise<T> {
    return this.request<T>(path, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
      headers: { 'Content-Type': 'application/json', ...options.headers },
    });
  }

  private async rotateRefreshToken(refreshToken: string): Promise<boolean> {
    const body = JSON.stringify({ refresh_token: refreshToken });
    const init: RequestInit = {
      method: 'POST',
      body,
      headers: { 'Content-Type': 'application/json' },
    };
    try {
      let response = await this.send(this.apiPrefix, '/auth/refresh', init);
      if (!response.ok && this.fallbackPrefix !== this.apiPrefix) {
        response = await this.send(this.fallbackPrefix, '/auth/refresh', init);
      }
      if (!response.ok) {
        this.clearSession();
        return false;
      }
      const payload = await this.parse<TokenResponse>(response);
      if (!response.ok || !payload?.token || !payload?.refresh_token) {
        this.clearSession();
        return false;
      }
      this.storeTokenResponse(payload);
      return true;
    } catch {
      this.clearSession();
      return false;
    }
  }

  private storeTokenResponse(payload: TokenResponse): StoredAuthSession {
    if (!payload?.token || !payload?.refresh_token || !Number.isFinite(payload.expires_in)) {
      throw new Error('The API returned an incomplete token response');
    }
    const now = this.clock();
    const session: StoredAuthSession = {
      accessToken: payload.token,
      refreshToken: payload.refresh_token,
      expiresAt: now + payload.expires_in * 1000,
      refreshExpiresAt: payload.refresh_expires_in
        ? now + payload.refresh_expires_in * 1000
        : decodeExpiry(payload.refresh_token),
      role: payload.role,
    };
    this.storage.setItem(this.storageKey, JSON.stringify(session));
    this.listeners.forEach((listener) => listener(session));
    return session;
  }

  private clearSession(): void {
    this.storage.removeItem(this.storageKey);
    this.listeners.forEach((listener) => listener(null));
  }

  private async send(prefix: string, path: string, init: RequestInit, token?: string | null): Promise<Response> {
    const headers = new Headers(init.headers);
    if (token) headers.set('Authorization', `Bearer ${token}`);
    const url = `${this.baseUrl}${prefix}${path.startsWith('/') ? path : `/${path}`}`;
    const response = await this.fetchImpl(url, { ...init, headers });
    // Warn when the deprecated /api/v1/ fallback is engaged, so operators
    // and developers see it in the console before the sunset date.
    if (prefix === this.fallbackPrefix && this.fallbackPrefix !== this.apiPrefix) {
      const deprecation = response.headers.get('Deprecation');
      if (deprecation === 'true') {
        const sunset = response.headers.get('Sunset') ?? 'unknown';
        console.warn(
          `[Loop CRM] compatibility API road is deprecated (Sunset: ${sunset}). ` +
            `Migrate to /apis/core/ (named road) or /bolt/ (Bolt runtime).`,
        );
      }
    }
    return response;
  }

  private async parse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type') ?? '';
    if (!contentType.includes('application/json')) return (await response.text()) as T;
    return (await response.json()) as T;
  }
}

export const boltApi = new BoltApiClient();
