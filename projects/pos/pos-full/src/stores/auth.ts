import { defineStore } from 'pinia';
import api from './api';

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  }),

  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      try {
        this.user = await api.post<User>('/auth/login', { email, password });
        this.isAuthenticated = true;
      } catch (e: any) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    async verify(email: string) {
      try {
        this.user = await api.post<User>('/auth/verify', { email });
        this.isAuthenticated = true;
      } catch {
        this.isAuthenticated = false;
      }
    },

    async sendConfirmationCode(email: string) {
      return await api.post('/auth/send-code', { email });
    },

    logout() {
      this.user = null;
      this.isAuthenticated = false;
    },
  },
});
