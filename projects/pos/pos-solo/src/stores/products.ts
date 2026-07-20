/**
 * Zustand Product Store — manages products via Robyn sidecar API.
 * Replaces: invoke('get_products'), invoke('add_product'), invoke('update_product'), invoke('delete_product')
 */

import { create } from 'zustand';
import api from './api';

export interface Product {
  id: number;
  name: string;
  price: number;
  unit: string;
  category_id: number | null;
  image: string | null;
  created_at: string;
  updated_at: string;
  uploaded: boolean;
}

interface ProductStore {
  products: Product[];
  loading: boolean;
  error: string | null;
  fetchAll: () => Promise<void>;
  create: (data: Partial<Product>) => Promise<Product>;
  update: (id: number, data: Partial<Product>) => Promise<Product>;
  remove: (id: number) => Promise<void>;
}

export const useProductStore = create<ProductStore>()((set) => ({
  products: [],
  loading: false,
  error: null,

  fetchAll: async () => {
    set({ loading: true, error: null });
    try {
      const products = await api.get<Product[]>('/products');
      set({ products });
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ loading: false });
    }
  },

  create: async (data) => {
    const product = await api.post<Product>('/products', data);
    set((state) => ({ products: [...state.products, product] }));
    return product;
  },

  update: async (id, data) => {
    const product = await api.patch<Product>(`/products/${id}`, data);
    set((state) => ({ products: state.products.map(p => p.id === id ? product : p) }));
    return product;
  },

  remove: async (id) => {
    await api.delete(`/products/${id}`);
    set((state) => ({ products: state.products.filter(p => p.id !== id) }));
  },
}));
