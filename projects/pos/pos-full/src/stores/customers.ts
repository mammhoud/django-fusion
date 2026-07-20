import { defineStore } from 'pinia';
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

interface CustomerState {
  customers: Customer[];
  loading: boolean;
  error: string | null;
}

export const useCustomerStore = defineStore('customers', {
  state: (): CustomerState => ({ customers: [], loading: false, error: null }),
  actions: {
    async fetchAll() {
      this.loading = true;
      try { this.customers = await api.get<Customer[]>('/customers'); }
      catch (e: any) { this.error = e.message; }
      finally { this.loading = false; }
    },
    async create(data: Partial<Customer>) { return await api.post<Customer>('/customers', data); },
    async update(id: number, data: Partial<Customer>) { return await api.patch<Customer>(`/customers/${id}`, data); },
    async remove(id: number) { await api.delete(`/customers/${id}`); this.customers = this.customers.filter(c => c.id !== id); },
  },
});
