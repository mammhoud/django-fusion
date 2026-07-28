'use client';

import { Provider } from 'react-redux';
import { store } from '@/store';
import { FusionMiddleware } from '@/components/FusionMiddleware';
import { ToastProvider } from '@/components/ui';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <FusionMiddleware>
        <ToastProvider>
          {children}
        </ToastProvider>
      </FusionMiddleware>
    </Provider>
  );
}
