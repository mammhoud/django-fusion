import { create } from 'zustand';
import api from './api';

export interface Transaction { id: number; type: string; amount: number; description: string; date: string; }

interface TxnStore { transactions: Transaction[]; loading: boolean; error: string | null; fetchAll: () => Promise<void>; remove: (id: number) => Promise<void>; }

export const useTransactionStore = create<TxnStore>()((set) => ({
  transactions: [], loading: false, error: null,
  fetchAll: async () => { set({ loading: true, error: null });
    try { set({ transactions: await api.get<Transaction[]>('/transactions') }); } catch (e: any) { set({ error: e.message }); } finally { set({ loading: false }); }
  },
  remove: async (id) => { await api.delete(`/transactions/${id}`); set((state) => ({ transactions: state.transactions.filter(x => x.id !== id) })); },
}));
