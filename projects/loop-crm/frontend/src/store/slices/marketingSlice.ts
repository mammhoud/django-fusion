// marketingSlice — scheduled posts + campaigns state (Postiz DNA).
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface ScheduledPost {
  id: string;
  content: string;
  channel: string;
  scheduled_at: string;
  status: string;
}

interface MarketingState {
  posts: ScheduledPost[];
  loading: boolean;
}

const initialState: MarketingState = { posts: [], loading: false };

const marketingSlice = createSlice({
  name: 'marketing',
  initialState,
  reducers: {
    setPosts(state, action: PayloadAction<ScheduledPost[]>) {
      state.posts = action.payload;
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
  },
});

export const { setPosts, setLoading } = marketingSlice.actions;
export default marketingSlice.reducer;
