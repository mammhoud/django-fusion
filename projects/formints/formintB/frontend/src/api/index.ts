/**
 * POS Sidecar API
 * ==================
 * Central barrel export for all sidecar API modules.
 *
 * Usage:
 *   import { sidecar, data } from './api';
 *
 *   // Health check
 *   const running = await sidecar.healthCheck();
 *
 *   // Data
 *   const sales = await data.listSales();
 *   const url = data.getInvoiceUrl(42, 'commercial', 'modern');
 */

export { sidecar, SIDECAR_BASE, SIDECAR_WS_BASE } from './sidecar';
export type {
  SidecarResponse,
  HealthResponse,
} from './sidecar';

export { data } from './data';
export type {
  SidecarSale,
  SidecarSaleItem,
  SidecarProduct,
  SidecarSettings,
  InvoiceType,
  InvoiceDesign,
} from './data';

export { createSyncEventsWs } from './sync-events';
export type {
  SyncEventFrame,
  SyncEventsOptions,
  SyncEventsConnection,
} from './sync-events';
