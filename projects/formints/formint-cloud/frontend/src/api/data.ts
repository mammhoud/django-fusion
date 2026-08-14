/**
 * Data API
 * ========
 * Read-only access to the Rust-managed SQLite database via the server.
 *
 * Endpoints:
 *   GET /api/sales          — list all sales with line items
 *   GET /api/sales/<id>     — get a single sale with line items
 *   GET /api/products       — list all products
 *   GET /api/settings       — get app settings
 *   GET /invoice/render/<id> — render an invoice as HTML
 */

import server, { SERVER_BASE } from './server';

// ---- Types ----------------------------------------------------------------

export interface ServerSaleItem {
  id: number;
  sale_id: number;
  product_name: string;
  price: number;
  quantity: number;
  unit: string;
  subtotal: number;
}

export interface ServerSale {
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
  items: ServerSaleItem[];
}

export interface ServerProduct {
  id: number;
  name: string;
  price: number;
  unit: string;
  category_id: number | null;
  image: string | null;
}

export interface ServerSettings {
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
    server.get<ServerSale[]>('/api/sales'),

  /**
   * Get a single sale by ID with line items.
   */
  getSale: (saleId: number) =>
    server.get<ServerSale>(`/api/sales/${saleId}`),

  /**
   * List all products.
   */
  listProducts: () =>
    server.get<ServerProduct[]>('/api/products'),

  /**
   * Get app settings.
   */
  getSettings: () =>
    server.get<ServerSettings>('/api/settings'),

  /**
   * Get the URL for a server-rendered invoice.
   * Open this URL in the system browser or an iframe.
   */
  getInvoiceUrl: (
    saleId: number,
    type: InvoiceType = 'commercial',
    design: InvoiceDesign = 'modern',
  ): string =>
    `${SERVER_BASE}/invoice/render/${saleId}?type=${type}&design=${design}`,

  /**
   * Fetch the rendered invoice HTML from the server.
   */
  getInvoiceHtml: (
    saleId: number,
    type: InvoiceType = 'commercial',
    design: InvoiceDesign = 'modern',
  ) =>
    server.get<string>(`/invoice/render/${saleId}?type=${type}&design=${design}`),
};

export default data;
