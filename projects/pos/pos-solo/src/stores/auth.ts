/**
 * Zustand Auth Store — manages authentication via Robyn sidecar API.
 * Replaces: invoke('verify_user'), invoke('send_auth_confirmation_code'), invoke('login_user')
 */

import { create } from 'zustand';
import api from './api';

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  verify: (email: string) => Promise<void>;
  sendConfirmationCode: (email: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const user = await api.post<User>('/auth/login', { email, password });
      set({ user, isAuthenticated: true });
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ loading: false });
    }
  },

  verify: async (email) => {
    try {
      const user = await api.post<User>('/auth/verify', { email });
      set({ user, isAuthenticated: true });
    } catch {
      set({ isAuthenticated: false });
    }
  },

  sendConfirmationCode: async (email) => {
    await api.post('/auth/send-code', { email });
  },

  logout: () => set({ user: null, isAuthenticated: false }),
}));
