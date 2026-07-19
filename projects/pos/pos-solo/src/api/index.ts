/**
 * POS Sidecar API
 * ==================
 * Central barrel export for all sidecar API modules.
 *
 * Usage:
 *   import { sidecar, chat, tickets, data } from './api';
 *
 *   // Health check
 *   const running = await sidecar.healthCheck();
 *
 *   // Chat
 *   const history = await chat.getHistory('room-1');
 *   const cleanup = createChatWs({ room: 'room-1', onMessage: (msg) => {} });
 *
 *   // Tickets
 *   const result = await tickets.list();
 *   await tickets.create({ name: 'John', email: '...', subject: '...', message: '...' });
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

export { chat, createChatWs } from './chat';
export type {
  ChatMessage,
  ChatHistoryResponse,
  WsChatFrame,
  WsConnState,
  ChatWsConnection,
  ChatWsOptions,
} from './chat';

export { tickets } from './tickets';
export type {
  SupportTicket,
  CreateTicketPayload,
  UpdateTicketPayload,
  TicketStatus,
} from './tickets';

export { data } from './data';
export type {
  SidecarSale,
  SidecarSaleItem,
  SidecarProduct,
  SidecarSettings,
  InvoiceType,
  InvoiceDesign,
} from './data';
