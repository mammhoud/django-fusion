// useLiveSync — flip a short-lived "synced" flag when a realtime refresh lands.
// Islands call ``flash()`` in their realtime callback; the flag stays true for
// ``durationMs`` (re-arming on each event) so the UI can show a pulsing chip
// that fades out on its own.

import { useCallback, useEffect, useRef, useState } from 'react';

export interface LiveSyncState {
  /** True from the moment a refresh lands until the flash window closes. */
  synced: boolean;
  /** Mark a refresh as landed (re-arms the auto-dismiss timer). */
  flash: () => void;
}

export function useLiveSync(durationMs = 2600): LiveSyncState {
  const [synced, setSynced] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const flash = useCallback(() => {
    setSynced(true);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setSynced(false), durationMs);
  }, [durationMs]);

  useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    },
    [],
  );

  return { synced, flash };
}
