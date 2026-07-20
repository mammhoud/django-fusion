import { create } from 'zustand';
import api from './api';

export interface DeliveryType { id: number; name: string; description: string | null; fee_multiplier: number; is_active: boolean; created_at: string; updated_at: string; }

interface DeliveryTypeStore {
  types: DeliveryType[]; loading: boolean; error: string | null;
  fetchAll: (includeInactive?: boolean) => Promise<void>;
  create: (d: Partial<DeliveryType>) => Promise<DeliveryType>;
  update: (id: number, d: Partial<DeliveryType>) => Promise<DeliveryType>;
  remove: (id: number) => Promise<void>;
}

export const useDeliveryTypeStore = create<DeliveryTypeStore>()((set) => ({
  types: [], loading: false, error: null,
  fetchAll: async (includeInactive = false) => {
    set({ loading: true, error: null });
    try { set({ types: await api.get<DeliveryType[]>(`/delivery-types?include_inactive=${includeInactive}`) }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const t = await api.post<DeliveryType>('/delivery-types', d); set((state) => ({ types: [...state.types, t] })); return t; },
  update: async (id, d) => { const t = await api.patch<DeliveryType>(`/delivery-types/${id}`, d); set((state) => ({ types: state.types.map(x => x.id === id ? t : x) })); return t; },
  remove: async (id) => { await api.patch(`/delivery-types/${id}`, { is_active: false }); set((state) => ({ types: state.types.filter(x => x.id !== id) })); },
}));
