/**
 * POS Server API
 * ==================
 * Central barrel export for all server API modules.
 *
 * Usage:
 *   import { server, data } from './api';
 *
 *   // Health check
 *   const running = await server.healthCheck();
 *
 *   // Data
 *   const sales = await data.listSales();
 *   const url = data.getInvoiceUrl(42, 'commercial', 'modern');
 */

export { server, SERVER_BASE, SERVER_WS_BASE } from './server';
export type {
  ServerResponse,
  HealthResponse,
} from './server';

export { data } from './data';
export type {
  ServerSale,
  ServerSaleItem,
  ServerProduct,
  ServerSettings,
  InvoiceType,
  InvoiceDesign,
} from './data';

export { createSyncEventsWs } from './sync-events';
export type {
  SyncEventFrame,
  SyncEventsOptions,
  SyncEventsConnection,
} from './sync-events';

export { dashboard } from './dashboard';
export type {
  BranchHealth,
  BranchHealthDetail,
  BranchHealthDetailResponse,
  BranchesHealthResponse,
  QueueSummary,
  QueueByBranch,
  QueueByBranchResponse,
  QueueItem,
  QueueListResponse,
  SyncConflict,
  ConflictListResponse,
  ConflictStats,
  ConflictResolution,
  ActivityEntry,
  ActivityResponse,
  DashboardResponse,
} from './dashboard';
