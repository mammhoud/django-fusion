/** Redux slice for toast notifications — replaces Alpine $store('toast'). */
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export interface ToastState {
  visible: boolean;
  message: string;
  variant: 'success' | 'error' | 'info' | 'warning';
}

const initialState: ToastState = {
  visible: false,
  message: '',
  variant: 'success',
};

const toastSlice = createSlice({
  name: 'toast',
  initialState,
  reducers: {
    showToast(
      state,
      action: PayloadAction<{
        message: string;
        variant?: ToastState['variant'];
      }>
    ) {
      state.message = action.payload.message;
      state.variant = action.payload.variant || 'success';
      state.visible = true;
    },
    hideToast(state) {
      state.visible = false;
    },
  },
});

export const { showToast, hideToast } = toastSlice.actions;
export default toastSlice.reducer;
