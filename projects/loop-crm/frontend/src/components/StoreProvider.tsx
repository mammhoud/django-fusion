import { Provider } from 'react-redux';
import type { ReactNode } from 'react';
import { store } from '@/store';

// StoreProvider — client-side island that wraps React islands in the Redux
// <Provider>. Astro can't nest <slot /> inside a React component, so this is
// the bridge each data-heavy island mounts around itself.
export default function StoreProvider({ children }: { children: ReactNode }) {
  return <Provider store={store}>{children}</Provider>;
}
