import { useCallback, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

// ── Types ────────────────────────────────────────────────────────────────

export interface UseApiMutationConfig {
  /**
   * Singular resource name used to derive command names:
   * `add_{singular}`, `update_{singular}`, and `delete_{singular}` /
   * `soft_delete_{singular}` (matches the backend `register_crud!` macro).
   */
  singular: string;
  /**
   * Use `soft_delete_{singular}` instead of `delete_{singular}`.
   * Default `false`.
   */
  softDelete?: boolean;
  /**
   * Argument name for the create payload. The `register_crud!` macro
   * generates `add_{s}(data)` so this defaults to `'data'`; handwritten
   * commands take the singular name instead (e.g. `add_customer(customer)`,
   * `add_note(template)`). Override when the command differs.
   */
  createArg?: string;
  /** Override the generated `add_{singular}` command name. */
  addCommand?: string;
  /** Override the generated `update_{singular}` command name. */
  updateCommand?: string;
  /** Override the generated `delete_{singular}` / `soft_delete_{singular}` command name. */
  deleteCommand?: string;
}

export interface MutationCallbacks<T = unknown> {
  /** Called with the backend result after a successful invoke. */
  onSuccess?: (data: T) => void;
  /** Called with the Error after a failed invoke. */
  onError?: (error: Error) => void;
}

export interface UseApiMutationResult<TEntity = unknown> {
  /**
   * Call `add_{singular}` with `{ [createArg]: payload }`.
   * Returns the created entity, or `null` on failure.
   */
  create: (
    payload: Record<string, unknown>,
    options?: MutationCallbacks<TEntity>,
  ) => Promise<TEntity | null>;
  /**
   * Call `update_{singular}` with `{ id, update }`.
   * Returns the updated entity, or `null` on failure.
   */
  update: (
    id: number,
    update: Record<string, unknown>,
    options?: MutationCallbacks<TEntity>,
  ) => Promise<TEntity | null>;
  /**
   * Call `delete_{singular}` / `soft_delete_{singular}` with `{ id }`.
   * Returns `true` on success, `false` on failure.
   */
  remove: (id: number, options?: MutationCallbacks<unknown>) => Promise<boolean>;
  /** True while any of create/update/remove is in flight. */
  isMutating: boolean;
  /** True while a create is in flight. */
  isCreating: boolean;
  /** True while an update is in flight. */
  isUpdating: boolean;
  /** True while a remove is in flight. */
  isDeleting: boolean;
  /** Latest mutation error message (or null). Cleared on each new call. */
  error: string | null;
  /** Clear the current error. */
  resetError: () => void;
}

// ── Internal helper ─────────────────────────────────────────────────────

function toErrorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

// ── Hook ────────────────────────────────────────────────────────────────

/**
 * Tauri mutation hook that matches the backend `register_crud!` pattern.
 *
 * Derives `add_{singular}` / `update_{singular}` / `delete_{singular}`
 * (or `soft_delete_{singular}`) command names from a singular resource name
 * and removes the repeated `try { invoke(...) } catch { showError(...) }`
 * boilerplate from CRUD pages.
 *
 * ```ts
 * const customerApi = useApiMutation<Customer>({
 *   singular: 'customer',
 *   createArg: 'customer', // add_customer(customer) — handwritten command
 * });
 *
 * // Add
 * const saved = await customerApi.create(form, {
 *   onSuccess: () => { setShowForm(false); showSuccess(t('common.saved')); refetch(); },
 *   onError: (err) => showError(`${t('common.error')}: ${err.message}`),
 * });
 *
 * // Update
 * await customerApi.update(id, form, { onSuccess, onError });
 *
 * // Delete (hard or soft per config)
 * await customerApi.remove(id, { onSuccess, onError });
 * ```
 */
export function useApiMutation<TEntity = unknown>(
  config: UseApiMutationConfig,
): UseApiMutationResult<TEntity> {
  const {
    singular,
    softDelete = false,
    createArg = 'data', // register_crud! macro generates `add_{s}(data)`
    addCommand = `add_${singular}`,
    updateCommand = `update_${singular}`,
    deleteCommand = softDelete ? `soft_delete_${singular}` : `delete_${singular}`,
  } = config;

  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(
    async (
      payload: Record<string, unknown>,
      options?: MutationCallbacks<TEntity>,
    ): Promise<TEntity | null> => {
      setIsCreating(true);
      setError(null);
      try {
        const data = await invoke<TEntity>(addCommand, { [createArg]: payload });
        options?.onSuccess?.(data);
        return data;
      } catch (err) {
        const msg = toErrorMessage(err);
        setError(msg);
        options?.onError?.(err instanceof Error ? err : new Error(msg));
        return null;
      } finally {
        setIsCreating(false);
      }
    },
    [addCommand, createArg],
  );

  const update = useCallback(
    async (
      id: number,
      update: Record<string, unknown>,
      options?: MutationCallbacks<TEntity>,
    ): Promise<TEntity | null> => {
      setIsUpdating(true);
      setError(null);
      try {
        const data = await invoke<TEntity>(updateCommand, { id, update });
        options?.onSuccess?.(data);
        return data;
      } catch (err) {
        const msg = toErrorMessage(err);
        setError(msg);
        options?.onError?.(err instanceof Error ? err : new Error(msg));
        return null;
      } finally {
        setIsUpdating(false);
      }
    },
    [updateCommand],
  );

  const remove = useCallback(
    async (id: number, options?: MutationCallbacks<unknown>): Promise<boolean> => {
      setIsDeleting(true);
      setError(null);
      try {
        await invoke<void>(deleteCommand, { id });
        options?.onSuccess?.(undefined);
        return true;
      } catch (err) {
        const msg = toErrorMessage(err);
        setError(msg);
        options?.onError?.(err instanceof Error ? err : new Error(msg));
        return false;
      } finally {
        setIsDeleting(false);
      }
    },
    [deleteCommand],
  );

  const resetError = useCallback(() => setError(null), []);

  return {
    create,
    update,
    remove,
    isMutating: isCreating || isUpdating || isDeleting,
    isCreating,
    isUpdating,
    isDeleting,
    error,
    resetError,
  };
}
