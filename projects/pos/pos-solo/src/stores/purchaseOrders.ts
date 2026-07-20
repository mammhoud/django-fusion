import { create } from 'zustand';
import api from './api';

export interface PurchaseOrder { id: number; supplier_id: number; reference_number: string | null; status: string; total_amount: number; expected_date: string | null; notes: string | null; created_at: string; updated_at: string; }
export interface PurchaseOrderItem { id: number; purchase_order_id: number; ingredient_id: number; quantity: number; cost_per_unit: number; received_quantity: number; }

interface POStore {
  orders: PurchaseOrder[]; items: Record<number, PurchaseOrderItem[]>; loading: boolean; error: string | null;
  fetchAll: () => Promise<void>;
  create: (order: Partial<PurchaseOrder>, items: Partial<PurchaseOrderItem>[]) => Promise<PurchaseOrder>;
  update: (id: number, d: Partial<PurchaseOrder>) => Promise<PurchaseOrder>;
  remove: (id: number) => Promise<void>;
  fetchItems: (orderId: number) => Promise<void>;
}

export const usePurchaseOrderStore = create<POStore>()((set) => ({
  orders: [], items: {}, loading: false, error: null,
  fetchAll: async () => { set({ loading: true, error: null });
    try { set({ orders: await api.get<PurchaseOrder[]>('/purchase-orders') }); } catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (order, items) => { const o = await api.post<PurchaseOrder>('/purchase-orders', { order, items }); set((state) => ({ orders: [...state.orders, o] })); return o; },
  update: async (id, d) => { const o = await api.patch<PurchaseOrder>(`/purchase-orders/${id}`, d); set((state) => ({ orders: state.orders.map(x => x.id === id ? o : x) })); return o; },
  remove: async (id) => { await api.delete(`/purchase-orders/${id}`); set((state) => ({ orders: state.orders.filter(x => x.id !== id) })); },
  fetchItems: async (orderId) => { const i = await api.get<PurchaseOrderItem[]>(`/purchase-orders/${orderId}/items`); set((state) => ({ items: { ...state.items, [orderId]: i } })); },
}));
