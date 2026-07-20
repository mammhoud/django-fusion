import { create } from 'zustand';
import api from './api';

export interface TaxReport { id: number; period_start: string; period_end: string; total_sales: number; total_tax: number; transaction_count: number; generated_at: string; }

interface TaxReportStore {
  reports: TaxReport[]; loading: boolean; error: string | null;
  fetchAll: () => Promise<void>;
  create: (d: Partial<TaxReport>) => Promise<TaxReport>;
  remove: (id: number) => Promise<void>;
}

export const useTaxReportStore = create<TaxReportStore>()((set) => ({
  reports: [], loading: false, error: null,
  fetchAll: async () => { set({ loading: true, error: null });
    try { set({ reports: await api.get<TaxReport[]>('/tax-reports') }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const r = await api.post<TaxReport>('/tax-reports', d); set((state) => ({ reports: [...state.reports, r] })); return r; },
  remove: async (id) => { await api.delete(`/tax-reports/${id}`); set((state) => ({ reports: state.reports.filter(x => x.id !== id) })); },
}));
