// Loop-CRM Redux store — the single source of truth for client data on the
// data-API road. RTK slices for config (renderMode), CRM (deals/pipeline) and
// marketing (posts/campaigns) replace ad-hoc Alpine/x-data state for data-heavy
// islands (mirrors the landing-fusion Redux decision to shrink Alpine).
import { configureStore } from '@reduxjs/toolkit';
import configReducer from './slices/configSlice';
import crmReducer from './slices/crmSlice';
import marketingReducer from './slices/marketingSlice';

export const store = configureStore({
  reducer: {
    config: configReducer,
    crm: crmReducer,
    marketing: marketingReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
