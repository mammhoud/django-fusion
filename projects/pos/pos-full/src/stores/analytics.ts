import { create } from 'zustand';
import api from './api';

export interface AnalyticsData { total_sales: number; total_orders: number; total_customers: number; top_products: any[]; daily_sales: any[]; }

interface AnalyticsStore { data: AnalyticsData | null; loading: boolean; error: string | null; fetch: () => Promise<void>; }

export const useAnalyticsStore = create<AnalyticsStore>((set) => ({
  data: null, loading: false, error: null,
  fetch: async () => { set({ loading: true, error: null });
    try { set({ data: await api.get<AnalyticsData>('/analytics') }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
}));
