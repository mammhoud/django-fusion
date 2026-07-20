import { create } from 'zustand';
import api from './api';

export interface Payroll { id: number; employee_id: number; period_start: string; period_end: string; regular_hours: number; overtime_hours: number; total_pay: number; status: string; created_at: string; updated_at: string; }

interface PayrollStore {
  payrolls: Payroll[]; loading: boolean; error: string | null;
  fetchAll: (employeeId?: number) => Promise<void>;
  create: (d: Partial<Payroll>) => Promise<Payroll>;
  update: (id: number, d: Partial<Payroll>) => Promise<Payroll>;
  remove: (id: number) => Promise<void>;
}

export const usePayrollStore = create<PayrollStore>()((set) => ({
  payrolls: [], loading: false, error: null,
  fetchAll: async (employeeId?) => { set({ loading: true, error: null });
    try { set({ payrolls: await api.get<Payroll[]>(`/payrolls${employeeId ? '?employee_id=' + employeeId : ''}`) }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const p = await api.post<Payroll>('/payrolls', d); set((state) => ({ payrolls: [...state.payrolls, p] })); return p; },
  update: async (id, d) => { const p = await api.patch<Payroll>(`/payrolls/${id}`, d); set((state) => ({ payrolls: state.payrolls.map(x => x.id === id ? p : x) })); return p; },
  remove: async (id) => { await api.delete(`/payrolls/${id}`); set((state) => ({ payrolls: state.payrolls.filter(x => x.id !== id) })); },
}));
