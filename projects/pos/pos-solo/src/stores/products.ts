/**
 * Pinia Product Store — manages products via Robyn sidecar API.
 * Replaces: invoke('get_products'), invoke('add_product'), invoke('update_product'), invoke('delete_product')
 */

import { defineStore } from 'pinia';
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

interface ProductState {
  products: Product[];
  loading: boolean;
  error: string | null;
}

export const useProductStore = defineStore('products', {
  state: (): ProductState => ({
    products: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchAll() {
      this.loading = true;
      this.error = null;
      try {
        this.products = await api.get<Product[]>('/products');
      } catch (e: any) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    async create(data: Partial<Product>) {
      return await api.post<Product>('/products', data);
    },

    async update(id: number, data: Partial<Product>) {
      return await api.patch<Product>(`/products/${id}`, data);
    },

    async remove(id: number) {
      await api.delete(`/products/${id}`);
      this.products = this.products.filter(p => p.id !== id);
    },
  },
});
