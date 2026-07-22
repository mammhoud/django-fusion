import { create } from 'zustand';
import api from './api';

export interface Supplier { id: number; name: string; contact_name: string | null; email: string | null; phone: string | null; address: string | null; tax_id: string | null; payment_terms: string | null; is_active: boolean; created_at: string; updated_at: string; }

interface SupplierStore {
  suppliers: Supplier[]; loading: boolean; error: string | null;
  fetchAll: (includeInactive?: boolean) => Promise<void>;
  create: (d: Partial<Supplier>) => Promise<Supplier>;
  update: (id: number, d: Partial<Supplier>) => Promise<Supplier>;
  remove: (id: number) => Promise<void>;
}

export const useSupplierStore = create<SupplierStore>()((set) => ({
  suppliers: [], loading: false, error: null,
  fetchAll: async (includeInactive = false) => {
    set({ loading: true, error: null });
    try { set({ suppliers: await api.get<Supplier[]>(`/suppliers?include_inactive=${includeInactive}`) }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const s = await api.post<Supplier>('/suppliers', d); set((state) => ({ suppliers: [...state.suppliers, s] }); return s; },
  update: async (id, d) => { const s = await api.patch<Supplier>(`/suppliers/${id}`, d); set((state) => ({ suppliers: state.suppliers.map(x => x.id === id ? s : x) }); return s; },
  remove: async (id) => { await api.patch(`/suppliers/${id}`, { is_active: false }); set((state) => ({ suppliers: state.suppliers.filter(x => x.id !== id) }); },
}));
