/**
 * Zustand Settings Store — app settings via Robyn API.
 * Replaces: invoke('get_settings'), invoke('save_settings'),
 *           invoke('import_database_cmd'), invoke('export_database_cmd'),
 *           invoke('change_password_cmd')
 */
import { create } from 'zustand';
import api from './api';

export interface Settings {
  id: number; restaurant_name: string | null; address: string | null;
  phone: string | null; email: string | null; tax_rate: string | null;
  currency: string; opening_time: string | null; closing_time: string | null;
  receipt_footer: string | null; logo: string | null;
  dine_in_tables: number; delivery_fee: number; delivery_fee_per_km: number;
}

interface SettingsStore {
  settings: Settings | null; loading: boolean; error: string | null;
  fetch: () => Promise<void>;
  save: (data: Partial<Settings>) => Promise<Settings>;
  exportDb: () => Promise<string>;
  importDb: (base64: string) => Promise<void>;
  changePassword: (email: string, oldPw: string, newPw: string) => Promise<void>;
}

export const useSettingsStore = create<SettingsStore>((set) => ({
  settings: null, loading: false, error: null,
  fetch: async () => {
    set({ loading: true, error: null });
    try { set({ settings: await api.get<Settings>('/settings') }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  save: async (data) => {
    const s = await api.patch<Settings>('/settings', data);
    set({ settings: s }); return s;
  },
  exportDb: async () => await api.get<{ data: string }>('/database/export').then(r => r.data),
  importDb: async (base64) => { await api.post('/database/import', { data: base64 }); },
  changePassword: async (email, oldPw, newPw) => {
    await api.post('/auth/change-password', { email, old_password: oldPw, new_password: newPw });
  },
}));
