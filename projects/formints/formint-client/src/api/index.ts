/**
 * POS API Client
 * Communicates with the Django portal (django-fusion backend on :8075).
 *
 * This edition has no Python sidecar — the register talks to the Django
 * backend for catalog JSON (/api/catalog/), recent orders (/api/orders/),
 * health (/fusion/health/) and the fusion render-mode contract (/fusion/*).
 *
 * API URLs are read from the settings store (user-configurable).
 */

import { useSettingsStore } from '../utils/settings';

function getPortalUrl(): string {
  try {
    const store = useSettingsStore();
    return store.portalUrl || 'http://localhost:8075';
  } catch {
    return 'http://localhost:8075';
  }
}

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${getPortalUrl()}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

// ── Catalog (Django GET /api/catalog/) ─────────────────────────

export interface CatalogProduct {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: string;
  compare_at_price: string | null;
  image_url: string;
  unit: string;
  category: string;
  tags: string[];
  is_featured: boolean;
}

export interface CatalogResponse {
  shop: { name: string; tagline: string; order_types: { value: string; label: string }[] };
  categories: { id: number; name: string; slug: string; glyph: string; description: string }[];
  products: CatalogProduct[];
}

export interface Product {
  id: number;
  name: string;
  price: number;
  unit: string;
  category?: string;
  image?: string;
  is_featured: boolean;
}

export async function getProducts(): Promise<Product[]> {
  const data = await apiGet<CatalogResponse>('/api/catalog/');
  return data.products.map((p) => ({
    id: p.id,
    name: p.name,
    price: Number(p.price),
    unit: p.unit,
    category: p.category,
    image: p.image_url || undefined,
    is_featured: p.is_featured,
  }));
}

// ── Orders (Django GET /api/orders/) ───────────────────────────

export interface OrderItemApi {
  id: number;
  product_name: string;
  unit_price: string;
  quantity: number;
  subtotal: string;
}

export interface OrderApi {
  id: number;
  reference: string;
  customer_name: string;
  status: string;
  order_type: string;
  total_amount: string;
  currency: string;
  created_at: string;
  items: OrderItemApi[];
}

/** Full detail payload — GET /api/orders/<pk>/ adds the customer + totals. */
export interface OrderDetailApi extends OrderApi {
  customer_email: string;
  customer_phone: string;
  notes: string;
  subtotal: string;
  discount: string;
  tax: string;
  payment_method: string;
  promo_code: string;
  ready_at: string | null;
  table_number: string;
  delivery_address: string;
  delivery_city: string;
  delivery_zip: string;
}

export interface OrdersResponse {
  orders: OrderApi[];
}

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
  reference: string;
  order_type: string;
  total_amount: number;
  currency: string;
  date: string;
  time: string;
  status: string;
  items: SaleItem[];
}

export interface SaleDetail extends Sale {
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  notes: string;
  subtotal: number;
  discount: number;
  tax: number;
  payment_method: string;
  promo_code: string;
  ready_at: string | null;
  table_number: string;
  delivery_address: string;
  delivery_city: string;
  delivery_zip: string;
}

function mapOrderToSale(o: OrderApi): Sale {
  const created = new Date(o.created_at);
  return {
    id: o.id,
    reference: o.reference,
    order_type: o.order_type,
    total_amount: Number(o.total_amount),
    currency: o.currency,
    date: created.toLocaleDateString(),
    time: created.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    status: o.status,
    items: o.items.map((i) => ({
      id: i.id,
      product_name: i.product_name,
      price: Number(i.unit_price),
      quantity: i.quantity,
      unit: 'each',
      subtotal: Number(i.subtotal),
    })),
  };
}

export async function getSales(): Promise<Sale[]> {
  const data = await apiGet<OrdersResponse>('/api/orders/');
  return data.orders.map(mapOrderToSale);
}

/** One line of a register ticket being submitted. */
export interface OrderLineInput {
  product_id: number;
  quantity: number;
  note?: string;
}

/** Create an order from the register ticket — POST /api/orders/. */
export async function createOrder(input: {
  items: OrderLineInput[];
  order_type: string;
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
  notes?: string;
  ready_at?: string | null;
  table_number?: string;
  delivery_address?: string;
  delivery_city?: string;
  delivery_zip?: string;
  payment_method?: string;
  promo_code?: string;
}): Promise<SaleDetail> {
  const response = await fetch(`${getPortalUrl()}/api/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.error || `API error: ${response.status}`);
  }
  const data = await response.json();
  return {
    ...mapOrderToSale(data),
    customer_name: data.customer_name,
    customer_email: data.customer_email,
    customer_phone: data.customer_phone,
    notes: data.notes,
    subtotal: Number(data.subtotal),
    discount: Number(data.discount ?? 0),
    tax: Number(data.tax),
    payment_method: data.payment_method ?? 'cash',
    promo_code: data.promo_code ?? '',
    ready_at: data.ready_at ?? null,
    table_number: data.table_number ?? '',
    delivery_address: data.delivery_address ?? '',
    delivery_city: data.delivery_city ?? '',
    delivery_zip: data.delivery_zip ?? '',
  };
}

/** Advance an order's fulfilment status — POST /api/orders/<pk>/status/. */
export async function updateOrderStatus(id: number, status: string): Promise<SaleDetail> {
  const response = await fetch(`${getPortalUrl()}/api/orders/${id}/status/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null);
    throw new Error(detail?.error || `API error: ${response.status}`);
  }
  const data = await response.json();
  return {
    ...mapOrderToSale(data),
    customer_name: data.customer_name,
    customer_email: data.customer_email,
    customer_phone: data.customer_phone,
    notes: data.notes,
    subtotal: Number(data.subtotal),
    discount: Number(data.discount ?? 0),
    tax: Number(data.tax),
    payment_method: data.payment_method ?? 'cash',
    promo_code: data.promo_code ?? '',
    ready_at: data.ready_at ?? null,
    table_number: data.table_number ?? '',
    delivery_address: data.delivery_address ?? '',
    delivery_city: data.delivery_city ?? '',
    delivery_zip: data.delivery_zip ?? '',
  };
}

/** Fetch one order's full detail — GET /api/orders/<pk>/. */
export async function getSale(id: number): Promise<SaleDetail> {
  const data = await apiGet<OrderDetailApi>(`/api/orders/${id}/`);
  return {
    ...mapOrderToSale(data),
    customer_name: data.customer_name,
    customer_email: data.customer_email,
    customer_phone: data.customer_phone,
    notes: data.notes,
    subtotal: Number(data.subtotal),
    discount: Number(data.discount ?? 0),
    tax: Number(data.tax),
    payment_method: data.payment_method ?? 'cash',
    promo_code: data.promo_code ?? '',
    ready_at: data.ready_at ?? null,
    table_number: data.table_number ?? '',
    delivery_address: data.delivery_address ?? '',
    delivery_city: data.delivery_city ?? '',
    delivery_zip: data.delivery_zip ?? '',
  };
}

// ── Health (Django GET /fusion/health/) ────────────────────────

export interface HealthStatus {
  service: string;
  status: string;
  db_available: boolean;
}

export async function getHealth(): Promise<HealthStatus> {
  await apiGet<{ status: number; data: { fusion_render_first: boolean } }>('/fusion/health/');
  return { service: 'Django portal', status: 'ok', db_available: true };
}

// ── Fusion contract (from the Django portal /fusion/*) ────────────────
// django-fusion exposes the render-mode / assets / session-mode contract;
// the client reads it to surface version + render-mode data in Settings.

export interface FusionAssets {
  version: string;
  static_url: string;
  fusion_render_first: boolean;
  enabled: boolean;
  webpack_enabled: boolean;
  webpack_bundle_dir: string;
  top: Record<string, unknown>;
  bottom: Record<string, unknown>;
  fonts: string[];
  preconnect: string[];
}

export interface FusionRenderMode {
  fusion_render_first: boolean;
  mode: 'fusion-render' | 'data-api';
  content: { html: string; data: string };
  session_cached: boolean;
  pointer: string;
}

export interface FusionSessionMode {
  fusion_render_first: boolean;
  session_cached: boolean;
  session_preference: boolean | null;
  default: boolean;
  htmx: boolean;
}

export async function getFusionAssets(): Promise<FusionAssets> {
  return apiGet<FusionAssets>('/fusion/assets/');
}

export async function getFusionRenderMode(): Promise<FusionRenderMode> {
  return apiGet<FusionRenderMode>('/fusion/render-mode/');
}

export async function getFusionSessionMode(): Promise<FusionSessionMode> {
  return apiGet<FusionSessionMode>('/fusion/session-mode/');
}

export async function setFusionSessionMode(value: boolean): Promise<FusionSessionMode> {
  const response = await fetch(`${getPortalUrl()}/fusion/session-mode/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ fusion_render_first: value }),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function clearFusionSessionMode(): Promise<FusionSessionMode> {
  const response = await fetch(`${getPortalUrl()}/fusion/session-mode/`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}
