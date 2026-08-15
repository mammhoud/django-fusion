import { useCallback, useEffect, useMemo, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useAuth } from '../contexts/AuthContext';

export type PermissionKey = string;

interface PermissionState {
  permissions: Set<PermissionKey>;
  isLoading: boolean;
  error: string | null;
}

/** Resolve permissions once per signed-in user and expose a stable gate helper. */
export function usePermissions() {
  const { user } = useAuth();
  const [state, setState] = useState<PermissionState>({
    permissions: new Set(),
    isLoading: Boolean(user),
    error: null,
  });

  const refresh = useCallback(async () => {
    if (!user) {
      setState({ permissions: new Set(), isLoading: false, error: null });
      return;
    }

    setState(previous => ({ ...previous, isLoading: true, error: null }));
    try {
      const resolved = await invoke<string[]>('resolve_permissions_cmd', { userId: user.id });
      setState({ permissions: new Set(resolved ?? []), isLoading: false, error: null });
    } catch (error) {
      setState({
        permissions: new Set(),
        isLoading: false,
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }, [user]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const can = useCallback(
    (permission: PermissionKey) => {
      // Unauthenticated local mode is intentionally unrestricted; the Rust
      // command remains authoritative whenever an account is signed in.
      return !user || state.permissions.has(permission);
    },
    [state.permissions, user],
  );

  return useMemo(
    () => ({ ...state, can, refresh }),
    [can, refresh, state],
  );
}
