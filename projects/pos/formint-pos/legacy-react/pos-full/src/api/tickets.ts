/**
 * Support Tickets API
 * ===================
 * REST API for managing support tickets via the sidecar.
 *
 * Endpoints:
 *   GET    /api/support/tickets          — list all tickets
 *   POST   /api/support/ticket           — create a ticket
 *   PATCH  /api/support/ticket/<id>      — update ticket status
 */

import sidecar from './sidecar';

// ---- Types ----------------------------------------------------------------

export type TicketStatus = 'open' | 'in_progress' | 'resolved' | 'closed';

export interface SupportTicket {
  id: string;
  name: string;
  email: string;
  subject: string;
  message: string;
  status: TicketStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateTicketPayload {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface UpdateTicketPayload {
  status: TicketStatus;
}

// ---- API ------------------------------------------------------------------

export const tickets = {
  /**
   * List all support tickets.
   */
  list: () =>
    sidecar.get<SupportTicket[]>('/api/support/tickets'),

  /**
   * Create a new support ticket.
   */
  create: (payload: CreateTicketPayload) =>
    sidecar.post<SupportTicket>('/api/support/ticket', payload),

  /**
   * Update a ticket's status.
   */
  update: (ticketId: string, payload: UpdateTicketPayload) =>
    sidecar.patch<SupportTicket>(`/api/support/ticket/${ticketId}`, payload),
};

export default tickets;
