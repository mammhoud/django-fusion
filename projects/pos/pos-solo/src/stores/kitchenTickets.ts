import { create } from 'zustand';
import api from './api';

export interface KitchenTicket { id: number; sale_id: number; status: string; priority: number; notes: string | null; created_at: string; completed_at: string | null; }

interface KTStore {
  tickets: KitchenTicket[]; loading: boolean; error: string | null;
  fetchAll: (status?: string) => Promise<void>;
  create: (d: Partial<KitchenTicket>) => Promise<KitchenTicket>;
  update: (id: number, d: Partial<KitchenTicket>) => Promise<KitchenTicket>;
  remove: (id: number) => Promise<void>;
}

export const useKitchenTicketStore = create<KTStore>()((set) => ({
  tickets: [], loading: false, error: null,
  fetchAll: async (status?) => { set({ loading: true, error: null });
    try { set({ tickets: await api.get<KitchenTicket[]>(`/kitchen-tickets${status ? '?status=' + status : ''}`) }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const t = await api.post<KitchenTicket>('/kitchen-tickets', d); set((state) => ({ tickets: [...state.tickets, t] })); return t; },
  update: async (id, d) => { const t = await api.patch<KitchenTicket>(`/kitchen-tickets/${id}`, d); set((state) => ({ tickets: state.tickets.map(x => x.id === id ? t : x) })); return t; },
  remove: async (id) => { await api.delete(`/kitchen-tickets/${id}`); set((state) => ({ tickets: state.tickets.filter(x => x.id !== id) })); },
}));
