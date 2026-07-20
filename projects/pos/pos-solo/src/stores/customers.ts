/**
 * Zustand Customer Store — manages customers via Robyn sidecar API.
 * Replaces: invoke('get_customers'), invoke('add_customer'), invoke('update_customer'), invoke('delete_customer')
 */

import { create } from 'zustand';
import api from './api';

export interface Customer {
  id: number;
  name: string;
  phone: string | null;
  email: string | null;
  loyalty_points: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

interface CustomerStore {
  customers: Customer[];
  loading: boolean;
  error: string | null;
  fetchAll: () => Promise<void>;
  create: (data: Partial<Customer>) => Promise<Customer>;
  update: (id: number, data: Partial<Customer>) => Promise<Customer>;
  remove: (id: number) => Promise<void>;
}

export const useCustomerStore = create<CustomerStore>()((set) => ({
  customers: [],
  loading: false,
  error: null,
  fetchAll: async () => {
    set({ loading: true, error: null });
    try { set({ customers: await api.get<Customer[]>('/customers') }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  create: async (data) => {
    const c = await api.post<Customer>('/customers', data);
    set((state) => ({ customers: [...state.customers, c] }));
    return c;
  },
  update: async (id, data) => {
    const c = await api.patch<Customer>(`/customers/${id}`, data);
    set((state) => ({ customers: state.customers.map(x => x.id === id ? c : x) }));
    return c;
  },
  remove: async (id) => {
    await api.delete(`/customers/${id}`);
    set((state) => ({ customers: state.customers.filter(x => x.id !== id) }));
  },
}));
