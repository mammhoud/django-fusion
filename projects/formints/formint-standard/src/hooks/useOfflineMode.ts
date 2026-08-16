import { useEffect, useState } from 'react';

/**
 * True while the device is offline (or before the first online event).
 * Community is offline-first by design — this surfaces that state in the UI
 * so the operator always knows data is staying on this device.
 */
export function useOfflineMode(): boolean {
  const [offline, setOffline] = useState(
    () => typeof navigator !== 'undefined' && !navigator.onLine,
  );

  useEffect(() => {
    const goOffline = () => setOffline(true);
    const goOnline = () => setOffline(false);
    window.addEventListener('offline', goOffline);
    window.addEventListener('online', goOnline);
    return () => {
      window.removeEventListener('offline', goOffline);
      window.removeEventListener('online', goOnline);
    };
  }, []);

  return offline;
}
