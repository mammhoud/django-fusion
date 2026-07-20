/**
 * Zustand Recipe Store — CRUD for recipes via Robyn API.
 * Replaces: invoke('get_recipes'), invoke('create_recipe'), invoke('update_recipe'),
 *           invoke('soft_delete_recipe'), invoke('get_recipe_ingredients'),
 *           invoke('add_recipe_ingredient'), invoke('delete_recipe_ingredient')
 */
import { create } from 'zustand';
import api from './api';

export interface Recipe {
  id: number; product_id: number; recipe_type_id: number;
  yield_quantity: number; is_active: boolean;
  created_at: string; updated_at: string; uploaded: boolean;
}
export interface RecipeIngredient {
  id: number; recipe_id: number; ingredient_id: number;
  quantity: number; unit: string | null; preparation_note: string | null;
  created_at: string; updated_at: string;
}

interface RecipeStore {
  recipes: Recipe[]; recipeIngredients: Record<number, RecipeIngredient[]>;
  loading: boolean; error: string | null;
  fetchAll: (includeInactive?: boolean) => Promise<void>;
  create: (recipe: Partial<Recipe>, ingredients: Partial<RecipeIngredient>[]) => Promise<Recipe>;
  update: (id: number, data: Partial<Recipe>) => Promise<Recipe>;
  remove: (id: number) => Promise<void>;
  fetchIngredients: (recipeId: number) => Promise<RecipeIngredient[]>;
  addIngredient: (data: Partial<RecipeIngredient>) => Promise<RecipeIngredient>;
  removeIngredient: (id: number) => Promise<void>;
}

export const useRecipeStore = create<RecipeStore>()((set) => ({
  recipes: [], recipeIngredients: {}, loading: false, error: null,
  fetchAll: async (includeInactive = false) => {
    set({ loading: true, error: null });
    try { set({ recipes: await api.get<Recipe[]>(`/recipes?include_inactive=${includeInactive}`) }); }
    catch (e: any) { set({ error: e.message }); }
    finally { set({ loading: false }); }
  },
  create: async (recipe, ingredients) => {
    const r = await api.post<Recipe>('/recipes', { recipe, ingredients });
    set((state) => ({ recipes: [...state.recipes, r] })); return r;
  },
  update: async (id, data) => {
    const r = await api.patch<Recipe>(`/recipes/${id}`, data);
    set((state) => ({ recipes: state.recipes.map(x => x.id === id ? r : x) })); return r;
  },
  remove: async (id) => {
    await api.patch(`/recipes/${id}`, { is_active: false });
    set((state) => ({ recipes: state.recipes.filter(x => x.id !== id) }));
  },
  fetchIngredients: async (recipeId) => {
    const items = await api.get<RecipeIngredient[]>(`/recipes/${recipeId}/ingredients`);
    set((state) => ({ recipeIngredients: { ...state.recipeIngredients, [recipeId]: items } }));
    return items;
  },
  addIngredient: async (data) => {
    const ri = await api.post<RecipeIngredient>('/recipe-ingredients', data);
    set((state) => {
      const items = [...(state.recipeIngredients[ri.recipe_id] || []), ri];
      return { recipeIngredients: { ...state.recipeIngredients, [ri.recipe_id]: items } };
    });
    return ri;
  },
  removeIngredient: async (id) => {
    await api.delete(`/recipe-ingredients/${id}`);
  },
}));
