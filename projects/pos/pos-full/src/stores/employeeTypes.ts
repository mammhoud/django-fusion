import { create } from 'zustand';
import api from './api';

export interface EmployeeType { id: number; name: string; description: string | null; is_active: boolean; created_at: string; updated_at: string; }

interface EmployeeTypeStore {
  types: EmployeeType[]; loading: boolean; error: string | null;
  fetchAll: (includeInactive?: boolean) => Promise<void>;
  create: (d: Partial<EmployeeType>) => Promise<EmployeeType>;
  update: (id: number, d: Partial<EmployeeType>) => Promise<EmployeeType>;
  remove: (id: number) => Promise<void>;
}

export const useEmployeeTypeStore = create<EmployeeTypeStore>()((set) => ({
  types: [], loading: false, error: null,
  fetchAll: async (includeInactive = false) => {
    set({ loading: true, error: null });
    try { set({ types: await api.get<EmployeeType[]>(`/employee-types?include_inactive=${includeInactive}`) }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const t = await api.post<EmployeeType>('/employee-types', d); set((state) => ({ types: [...state.types, t] })); return t; },
  update: async (id, d) => { const t = await api.patch<EmployeeType>(`/employee-types/${id}`, d); set((state) => ({ types: state.types.map(x => x.id === id ? t : x) })); return t; },
  remove: async (id) => { await api.patch(`/employee-types/${id}`, { is_active: false }); set((state) => ({ types: state.types.filter(x => x.id !== id) })); },
}));
