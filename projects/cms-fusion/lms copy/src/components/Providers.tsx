'use client';

import { Provider } from 'react-redux';
import { store } from '@/store';
import { FusionMiddleware } from '@/components/FusionMiddleware';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <FusionMiddleware>
        {children}
      </FusionMiddleware>
    </Provider>
  );
}
