/**
 * POS-KO API Client — Zustand + Robyn Sidecar
 *
 * Replaces all Tauri invoke() calls with HTTP requests to the Robyn sidecar.
 * Used by Zustand stores to perform CRUD operations over REST APIs.
 *
 * Architecture:
 *   React (Zustand stores) → fetch() → Robyn sidecar (:8765/:8766) → Django ORM → SQLite
 */

const API_BASE = 'http://localhost:8765'; // pos-solo default; override via env

export interface ApiResponse<T> {
  ok: boolean;
  data: T | null;
  error: string | null;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  setBaseUrl(url: string) {
    this.baseUrl = url;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'GET' });
  }

  async post<T>(path: string, data: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(path: string, data: unknown): Promise<T> {
    return this.request<T>(path, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, { method: 'DELETE' });
  }
}

export const api = new ApiClient();

export default api;
