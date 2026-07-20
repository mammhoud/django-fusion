import { create } from 'zustand';
import api from './api';

export interface EmployeeSchedule { id: number; employee_id: number; shift_start: string; shift_end: string; status: string; notes: string | null; created_at: string; updated_at: string; }

interface EmployeeScheduleStore {
  schedules: EmployeeSchedule[]; loading: boolean; error: string | null;
  fetchAll: (employeeId?: number) => Promise<void>;
  create: (d: Partial<EmployeeSchedule>) => Promise<EmployeeSchedule>;
  update: (id: number, d: Partial<EmployeeSchedule>) => Promise<EmployeeSchedule>;
  remove: (id: number) => Promise<void>;
}

export const useEmployeeScheduleStore = create<EmployeeScheduleStore>()((set) => ({
  schedules: [], loading: false, error: null,
  fetchAll: async (employeeId?) => { set({ loading: true, error: null });
    try { set({ schedules: await api.get<EmployeeSchedule[]>(`/employee-schedules${employeeId ? '?employee_id=' + employeeId : ''}`) }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const s = await api.post<EmployeeSchedule>('/employee-schedules', d); set((state) => ({ schedules: [...state.schedules, s] }); return s; },
  update: async (id, d) => { const s = await api.patch<EmployeeSchedule>(`/employee-schedules/${id}`, d); set((state) => ({ schedules: state.schedules.map(x => x.id === id ? s : x) }); return s; },
  remove: async (id) => { await api.delete(`/employee-schedules/${id}`); set((state) => ({ schedules: state.schedules.filter(x => x.id !== id) }); },
}));
