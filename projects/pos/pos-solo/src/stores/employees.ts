/**
 * Zustand Employee Store — CRUD for employees via Robyn API.
 * Replaces: invoke('get_employees'), invoke('add_employee'), invoke('update_employee'), invoke('soft_delete_employee')
 */
import { create } from 'zustand';
import api from './api';

export interface Employee {
  id: number; name: string; phone: string | null; email: string | null;
  employee_type_id: number; salary: number; is_active: boolean;
  joined_at: string | null; created_at: string; updated_at: string; uploaded: boolean;
}

interface EmployeeStore {
  employees: Employee[]; loading: boolean; error: string | null;
  fetchAll: (includeInactive?: boolean) => Promise<void>;
  create: (data: Partial<Employee>) => Promise<Employee>;
  update: (id: number, data: Partial<Employee>) => Promise<Employee>;
  remove: (id: number) => Promise<void>;
}

export const useEmployeeStore = create<EmployeeStore>()((set) => ({
  employees: [], loading: false, error: null,
  fetchAll: async (includeInactive = false) => {
    set({ loading: true, error: null });
    try { set({ employees: await api.get<Employee[]>(`/employees?include_inactive=${includeInactive}`) }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  create: async (data) => {
    const e = await api.post<Employee>('/employees', data);
    set((state) => ({ employees: [...state.employees, e] })); return e;
  },
  update: async (id, data) => {
    const e = await api.patch<Employee>(`/employees/${id}`, data);
    set((state) => ({ employees: state.employees.map(x => x.id === id ? e : x) })); return e;
  },
  remove: async (id) => {
    await api.patch(`/employees/${id}`, { is_active: false });
    set((state) => ({ employees: state.employees.filter(x => x.id !== id) }));
  },
}));
