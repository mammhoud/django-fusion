/**
 * Zustand Inventory Store — ingredients and transactions via Robyn API.
 * Replaces: invoke('get_ingredients'), invoke('add_ingredient'), invoke('update_ingredient'),
 *           invoke('soft_delete_ingredient'), invoke('add_inventory_transaction'),
 *           invoke('get_inventory_transactions'), invoke('get_inventory_adjustments')
 */
import { create } from 'zustand';
import api from './api';

export interface Ingredient {
  id: number; name: string; unit: string; current_quantity: number;
  reorder_level: number; reorder_quantity: number; cost_per_unit: number;
  is_active: boolean; created_at: string; updated_at: string; uploaded: boolean;
}
export interface InventoryTransaction {
  id: number; ingredient_id: number; transaction_type: string;
  quantity_change: number; reference_id: number | null; note: string | null;
  created_at: string; uploaded: boolean;
}
export interface InventoryAdjustment {
  id: number; ingredient_id: number; previous_quantity: number;
  new_quantity: number; reason: string; created_by: string | null;
  created_at: string; uploaded: boolean;
}

interface InventoryStore {
  ingredients: Ingredient[]; transactions: InventoryTransaction[];
  adjustments: InventoryAdjustment[]; loading: boolean; error: string | null;
  fetchIngredients: (includeInactive?: boolean) => Promise<void>;
  createIngredient: (data: Partial<Ingredient>) => Promise<Ingredient>;
  updateIngredient: (id: number, data: Partial<Ingredient>) => Promise<Ingredient>;
  removeIngredient: (id: number) => Promise<void>;
  fetchTransactions: (ingredientId?: number) => Promise<void>;
  addTransaction: (tx: Partial<InventoryTransaction>, reason?: string, createdBy?: string) => Promise<InventoryTransaction>;
  fetchAdjustments: (ingredientId?: number) => Promise<void>;
}

export const useInventoryStore = create<InventoryStore>()((set) => ({
  ingredients: [], transactions: [], adjustments: [], loading: false, error: null,
  fetchIngredients: async (includeInactive = false) => {
    set({ loading: true, error: null });
    try { set({ ingredients: await api.get<Ingredient[]>(`/ingredients?include_inactive=${includeInactive}`) }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  createIngredient: async (data) => {
    const i = await api.post<Ingredient>('/ingredients', data);
    set((state) => ({ ingredients: [...state.ingredients, i] }); return i;
  },
  updateIngredient: async (id, data) => {
    const i = await api.patch<Ingredient>(`/ingredients/${id}`, data);
    set((state) => ({ ingredients: state.ingredients.map(x => x.id === id ? i : x) }); return i;
  },
  removeIngredient: async (id) => {
    await api.patch(`/ingredients/${id}`, { is_active: false });
    set((state) => ({ ingredients: state.ingredients.filter(x => x.id !== id) });
  },
  fetchTransactions: async (ingredientId?) => {
    set({ loading: true });
    const q = ingredientId ? `?ingredient_id=${ingredientId}` : '';
    try { set({ transactions: await api.get<InventoryTransaction[]>(`/inventory${q}`) }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  addTransaction: async (tx, reason?, createdBy?) => {
    const t = await api.post<InventoryTransaction>('/inventory', { transaction: tx, adjustment_reason: reason, created_by: createdBy });
    set((state) => ({ transactions: [...state.transactions, t] }); return t;
  },
  fetchAdjustments: async (ingredientId?) => {
    const q = ingredientId ? `?ingredient_id=${ingredientId}` : '';
    try { set({ adjustments: await api.get<InventoryAdjustment[]>(`/inventory/adjustments${q}`) }); }
    catch (e: any) { set({ error: e.message }); }
  },
}));
