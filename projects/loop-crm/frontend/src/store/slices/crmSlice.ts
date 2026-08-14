// crmSlice — deals + pipeline state (Twenty DNA).
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface Deal {
  id: string;
  name: string;
  company: string;
  value: number;
  stage: string;
  stage_type: string;
}

interface CrmState {
  deals: Deal[];
  loading: boolean;
}

const initialState: CrmState = { deals: [], loading: false };

const crmSlice = createSlice({
  name: 'crm',
  initialState,
  reducers: {
    setDeals(state, action: PayloadAction<Deal[]>) {
      state.deals = action.payload;
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
  },
});

export const { setDeals, setLoading } = crmSlice.actions;
export default crmSlice.reducer;
