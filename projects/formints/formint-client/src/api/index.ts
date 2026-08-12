/**
 * POS API Client
 * Communicates with POS sidecar (Sanic REST API on port 8765)
 * and Django Portal (port 8080-8082).
 *
 * API URLs are read from the settings store (user-configurable).
 */

import { useSettingsStore } from '../utils/settings';

// Env-driven defaults (Vite reads .env into import.meta.env). The settings
// store still wins when the user has configured custom URLs in the UI.
const ENV_SIDECAR_URL = (import.meta.env?.VITE_SIDECAR_URL as string | undefined) || 'http://localhost:8765';
const ENV_PORTAL_URL = (import.meta.env?.VITE_PORTAL_URL as string | undefined) || 'http://localhost:8080';

function getSidecarUrl(): string {
  try {
    const store = useSettingsStore();
    return store.sidecarUrl || ENV_SIDECAR_URL;
  } catch {
    return ENV_SIDECAR_URL;
  }
}

function getPortalUrl(): string {
  try {
    const store = useSettingsStore();
    return store.portalUrl || ENV_PORTAL_URL;
  } catch {
    return ENV_PORTAL_URL;
  }
}

interface FetchOptions {
  base?: 'sidecar' | 'portal';
}

async function apiGet<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const base = opts.base === 'portal' ? getPortalUrl() : getSidecarUrl();
  const response = await fetch(`${base}${path}`);
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

async function apiPost<T>(path: string, body: unknown, opts: FetchOptions = {}): Promise<T> {
  const base = opts.base === 'portal' ? getPortalUrl() : getSidecarUrl();
  const response = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

// ── Products (from Sanic sidecar JSON API) ───────────────────

export interface Product {
  id: number;
  name: string;
  price: number;
  unit: string;
  category_id: number;
  image?: string;
}

export async function getProducts(): Promise<Product[]> {
  return apiGet<Product[]>('/api/products');
}

// ── Sales (from Sanic sidecar JSON API) ─────────────────────

export interface SaleItem {
  id: number;
  product_name: string;
  price: number;
  quantity: number;
  unit: string;
  subtotal: number;
}

export interface Sale {
  id: number;
  total_amount: number;
  currency: string;
  date: string;
  time: string;
  status: string;
  items: SaleItem[];
}

export async function getSales(): Promise<Sale[]> {
  return apiGet<Sale[]>('/api/sales');
}

export async function getSale(id: number): Promise<Sale> {
  return apiGet<Sale>(`/api/sales/${id}`);
}

// ── Health (from Sanic sidecar) ─────────────────────────────

export interface HealthStatus {
  service: string;
  status: string;
  db_available: boolean;
}

export async function getHealth(): Promise<HealthStatus> {
  return apiGet<HealthStatus>('/health');
}
