import { create } from 'zustand';
import api from './api';

export interface ReportMetadata { id: number; report_type: string; format: string; file_path: string; parameters: string | null; generated_by: number | null; created_at: string; }

interface ReportStore { reports: ReportMetadata[]; loading: boolean; error: string | null; fetchAll: () => Promise<void>; create: (d: Partial<ReportMetadata>) => Promise<ReportMetadata>; remove: (id: number) => Promise<void>; }

export const useReportStore = create<ReportStore>()((set) => ({
  reports: [], loading: false, error: null,
  fetchAll: async () => { set({ loading: true, error: null });
    try { set({ reports: await api.get<ReportMetadata[]>('/report-metadata') }); } catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const r = await api.post<ReportMetadata>('/report-metadata', d); set((state) => ({ reports: [...state.reports, r] })); return r; },
  remove: async (id) => { await api.delete(`/report-metadata/${id}`); set((state) => ({ reports: state.reports.filter(x => x.id !== id) })); },
}));
