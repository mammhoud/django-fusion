import { create } from 'zustand';
import api from './api';

export interface ReceiptTemplate { id: number; name: string; template_body: string; is_default: boolean; created_at: string; updated_at: string; }

interface ReceiptTemplateStore {
  templates: ReceiptTemplate[]; loading: boolean; error: string | null;
  fetchAll: () => Promise<void>;
  fetchDefault: () => Promise<ReceiptTemplate>;
  create: (d: Partial<ReceiptTemplate>) => Promise<ReceiptTemplate>;
  update: (id: number, d: Partial<ReceiptTemplate>) => Promise<ReceiptTemplate>;
  remove: (id: number) => Promise<void>;
}

export const useReceiptTemplateStore = create<ReceiptTemplateStore>()((set) => ({
  templates: [], loading: false, error: null,
  fetchAll: async () => { set({ loading: true, error: null });
    try { set({ templates: await api.get<ReceiptTemplate[]>('/receipt-templates') }); }
    catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  fetchDefault: async () => await api.get<ReceiptTemplate>('/receipt-templates/default'),
  create: async (d) => { const t = await api.post<ReceiptTemplate>('/receipt-templates', d); set((state) => ({ templates: [...state.templates, t] }); return t; },
  update: async (id, d) => { const t = await api.patch<ReceiptTemplate>(`/receipt-templates/${id}`, d); set((state) => ({ templates: state.templates.map(x => x.id === id ? t : x) }); return t; },
  remove: async (id) => { await api.delete(`/receipt-templates/${id}`); set((state) => ({ templates: state.templates.filter(x => x.id !== id) }); },
}));
