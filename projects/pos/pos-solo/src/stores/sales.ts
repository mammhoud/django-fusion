/**
 * Zustand Sale Store — CRUD for sales via Robyn API.
 * Replaces: invoke('get_sales'), invoke('add_sale'), invoke('update_sale'), invoke('delete_sale')
 */
import { create } from 'zustand';
import api from './api';

export interface Sale {
  id: number; total_amount: number; currency: string; date: string; time: string;
  order_type: string; status: string; table_number: number | null;
  delivery_type_id: number | null; delivery_address: string | null;
  employee_id: number | null; customer_id: number | null;
  created_at: string; updated_at: string; uploaded: boolean;
}

interface SaleStore {
  sales: Sale[]; loading: boolean; error: string | null;
  fetchAll: () => Promise<void>;
  create: (sale: Partial<Sale>, items: any[]) => Promise<Sale>;
  update: (id: number, data: Partial<Sale>) => Promise<Sale>;
  remove: (id: number) => Promise<void>;
}

export const useSaleStore = create<SaleStore>()((set) => ({
  sales: [], loading: false, error: null,
  fetchAll: async () => {
    set({ loading: true, error: null });
    try { set({ sales: await api.get<Sale[]>('/sales') }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  create: async (sale, items) => {
    const s = await api.post<Sale>('/sales/with-items', { ...sale, items });
    set((state) => ({ sales: [...state.sales, s] })); return s;
  },
  update: async (id, data) => {
    const s = await api.patch<Sale>(`/sales/${id}`, data);
    set((state) => ({ sales: state.sales.map(x => x.id === id ? s : x) })); return s;
  },
  remove: async (id) => {
    await api.delete(`/sales/${id}`);
    set((state) => ({ sales: state.sales.filter(x => x.id !== id) }));
  },
}));
