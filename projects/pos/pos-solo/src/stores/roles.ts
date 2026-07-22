import { create } from 'zustand';
import api from './api';

export interface Role { id: number; name: string; permissions: string; is_active: boolean; created_at: string; updated_at: string; }

interface RoleStore {
  roles: Role[]; loading: boolean; error: string | null;
  fetchAll: () => Promise<void>; create: (d: Partial<Role>) => Promise<Role>;
  update: (id: number, d: Partial<Role>) => Promise<Role>; remove: (id: number) => Promise<void>;
  fetchUserRoles: (userId: number) => Promise<Role[]>;
  assign: (userId: number, roleId: number) => Promise<void>;
  unassign: (userId: number, roleId: number) => Promise<void>;
}

export const useRoleStore = create<RoleStore>()((set) => ({
  roles: [], loading: false, error: null,
  fetchAll: async () => { set({ loading: true, error: null });
    try { set({ roles: await api.get<Role[]>('/roles') }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  create: async (d) => { const r = await api.post<Role>('/roles', d); set((state) => ({ roles: [...state.roles, r] }); return r; },
  update: async (id, d) => { const r = await api.patch<Role>(`/roles/${id}`, d); set((state) => ({ roles: state.roles.map(x => x.id === id ? r : x) }); return r; },
  remove: async (id) => { await api.patch(`/roles/${id}`, { is_active: false }); set((state) => ({ roles: state.roles.filter(x => x.id !== id) }); },
  fetchUserRoles: async (userId) => await api.get<Role[]>(`/users/${userId}/roles`),
  assign: async (userId, roleId) => { await api.post('/user-roles', { user_id: userId, role_id: roleId }); },
  unassign: async (userId, roleId) => { await api.delete(`/user-roles/${userId}/${roleId}`); },
}));
