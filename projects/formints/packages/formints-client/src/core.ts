/** Core HTTP client for the Formints POS API. Framework-agnostic (fetch only). */

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export interface FormintsClient {
  /** Perform a JSON request relative to the base URL. */
  request<T>(path: string, init?: RequestInit): Promise<T>;
}

export function createClient(baseUrl: string): FormintsClient {
  const root = baseUrl.replace(/\/$/, '');
  return {
    async request<T>(path: string, init: RequestInit = {}): Promise<T> {
      const res = await fetch(`${root}${path}`, {
        ...init,
        headers: {
          'content-type': 'application/json',
          ...(init.headers ?? {}),
        },
      });
      if (!res.ok) {
        throw new ApiError(res.status, `Request failed: ${res.status} ${res.statusText}`, await res.text());
      }
      const text = await res.text();
      return (text ? JSON.parse(text) : undefined) as T;
    },
  };
}
