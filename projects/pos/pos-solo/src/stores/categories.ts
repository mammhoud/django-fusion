/**
 * Zustand Category Store — CRUD for categories via Robyn API.
 * Replaces: invoke('get_categories'), invoke('add_category')
 */
import { create } from 'zustand';
import api from './api';

export interface Category { id: number; name: string; created_at: string; updated_at: string; }

interface CategoryStore {
  categories: Category[]; loading: boolean; error: string | null;
  fetchAll: () => Promise<void>;
  create: (data: Partial<Category>) => Promise<Category>;
}

export const useCategoryStore = create<CategoryStore>()((set) => ({
  categories: [], loading: false, error: null,
  fetchAll: async () => {
    set({ loading: true, error: null });
    try { set({ categories: await api.get<Category[]>('/categories') }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  create: async (data) => {
    const c = await api.post<Category>('/categories', data);
    set((state) => ({ categories: [...state.categories, c] })); return c;
  },
}));
