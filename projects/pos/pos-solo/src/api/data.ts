/**
 * Data API
 * ========
 * Read-only access to the Rust-managed SQLite database via the sidecar.
 *
 * Endpoints:
 *   GET /api/sales          — list all sales with line items
 *   GET /api/sales/<id>     — get a single sale with line items
 *   GET /api/products       — list all products
 *   GET /api/settings       — get app settings
 *   GET /invoice/render/<id> — render an invoice as HTML
 */

import sidecar, { SIDECAR_BASE } from './sidecar';

// ---- Types ----------------------------------------------------------------

export interface SidecarSaleItem {
  id: number;
  sale_id: number;
  product_name: string;
  price: number;
  quantity: number;
  unit: string;
  subtotal: number;
}

export interface SidecarSale {
  id: number;
  total_amount: number;
  currency: string;
  date: string;
  time: string;
  order_type: string;
  status: string;
  table_number: number | null;
  delivery_type_id: number | null;
  delivery_address: string | null;
  employee_id: number | null;
  customer_id: number | null;
  created_at: string;
  updated_at: string;
  items: SidecarSaleItem[];
}

export interface SidecarProduct {
  id: number;
  name: string;
  price: number;
  unit: string;
  category_id: number | null;
  image: string | null;
}

export interface SidecarSettings {
  id: number;
  restaurant_name: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  tax_rate: string | null;
  currency: string;
  opening_time: string | null;
  closing_time: string | null;
  receipt_footer: string | null;
  logo: string | null;
  dine_in_tables: number;
  delivery_fee: number;
  delivery_fee_per_km: number;
}

export type InvoiceType = 'tax' | 'commercial' | 'proforma' | 'credit' | 'receipt';
export type InvoiceDesign = 'modern' | 'classic' | 'minimal';

// ---- API ------------------------------------------------------------------

export const data = {
  /**
   * List all sales with line items.
   */
  listSales: () =>
    sidecar.get<SidecarSale[]>('/api/sales'),

  /**
   * Get a single sale by ID with line items.
   */
  getSale: (saleId: number) =>
    sidecar.get<SidecarSale>(`/api/sales/${saleId}`),

  /**
   * List all products.
   */
  listProducts: () =>
    sidecar.get<SidecarProduct[]>('/api/products'),

  /**
   * Get app settings.
   */
  getSettings: () =>
    sidecar.get<SidecarSettings>('/api/settings'),

  /**
   * Get the URL for a sidecar-rendered invoice.
   * Open this URL in the system browser or an iframe.
   */
  getInvoiceUrl: (
    saleId: number,
    type: InvoiceType = 'commercial',
    design: InvoiceDesign = 'modern',
  ): string =>
    `${SIDECAR_BASE}/invoice/render/${saleId}?type=${type}&design=${design}`,

  /**
   * Fetch the rendered invoice HTML from the sidecar.
   */
  getInvoiceHtml: (
    saleId: number,
    type: InvoiceType = 'commercial',
    design: InvoiceDesign = 'modern',
  ) =>
    sidecar.get<string>(`/invoice/render/${saleId}?type=${type}&design=${design}`),
};

export default data;
