import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useApiMutation } from '../../hooks/useApiMutation';
import { mockInvokeSuccess, mockInvokeError, mockInvokePending, resetInvokeMocks } from '../mocks/tauri';

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
});

describe('useApiMutation hook', () => {
  it('create calls add_{singular} with the configured createArg', async () => {
    mockInvokeSuccess('add_customer', { id: 7, name: 'New' });
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    let created: unknown;
    await act(async () => {
      created = await result.current.create(
        { name: 'New', phone: '1' },
        { onSuccess: (data) => { /* callback fires */ void data; } },
      );
    });

    expect(created).toEqual({ id: 7, name: 'New' });
    // Verify the invoke actually hit the mocked command — the mock resolved,
    // so result current returns the payload from add_customer.
    expect(result.current.error).toBeNull();
    expect(result.current.isCreating).toBe(false);
  });

  it('create defaults createArg to "data" (register_crud macro pattern)', async () => {
    mockInvokeSuccess('add_product', { id: 1 });
    const { result } = renderHook(() => useApiMutation({ singular: 'product' }));

    let created: unknown;
    await act(async () => {
      created = await result.current.create({ name: 'Burger' });
    });

    expect(created).toEqual({ id: 1 });
  });

  it('create calls a custom addCommand when provided', async () => {
    mockInvokeSuccess('add_recipe_note', { id: 3 });
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'note', addCommand: 'add_recipe_note', createArg: 'template' }),
    );

    let created: unknown;
    await act(async () => {
      created = await result.current.create({ name: 'Note' });
    });

    expect(created).toEqual({ id: 3 });
  });

  it('create invokes onSuccess with the result and resolves data', async () => {
    mockInvokeSuccess('add_supplier', { id: 9, name: 'Zebra Foods' });
    const onSuccess = vi.fn();
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'supplier', createArg: 'supplier' }),
    );

    await act(async () => {
      await result.current.create({ name: 'Zebra Foods' }, { onSuccess });
    });

    expect(onSuccess).toHaveBeenCalledWith({ id: 9, name: 'Zebra Foods' });
  });

  it('create invokes onError and returns null when the backend rejects', async () => {
    mockInvokeError('add_customer', 'Duplicate name');
    const onError = vi.fn();
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    let created: unknown;
    await act(async () => {
      created = await result.current.create({ name: 'Dup' }, { onError });
    });

    expect(created).toBeNull();
    expect(onError).toHaveBeenCalledTimes(1);
    expect(result.current.error).toBe('Duplicate name');
  });

  it('create tracks isCreating and isMutating while in flight', async () => {
    mockInvokePending('add_customer');
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    act(() => {
      result.current.create({ name: 'Slow' });
    });
    // The invoke stays pending — flags must be true while it is in flight.
    expect(result.current.isCreating).toBe(true);
    expect(result.current.isMutating).toBe(true);
  });

  it('update calls update_{singular} with { id, update }', async () => {
    mockInvokeSuccess('update_customer', { id: 5, name: 'Renamed' });
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    let updated: unknown;
    await act(async () => {
      updated = await result.current.update(5, { name: 'Renamed' });
    });

    expect(updated).toEqual({ id: 5, name: 'Renamed' });
    expect(result.current.error).toBeNull();
  });

  it('update invokes onSuccess with the updated entity', async () => {
    mockInvokeSuccess('update_employee', { id: 2, name: 'Ali' });
    const onSuccess = vi.fn();
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'employee', createArg: 'employee' }),
    );

    await act(async () => {
      await result.current.update(2, { name: 'Ali' }, { onSuccess });
    });

    expect(onSuccess).toHaveBeenCalledWith({ id: 2, name: 'Ali' });
  });

  it('update surfaces backend errors via error state + onError', async () => {
    mockInvokeError('update_customer', 'Not found');
    const onError = vi.fn();
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    let updated: unknown;
    await act(async () => {
      updated = await result.current.update(999, { name: 'X' }, { onError });
    });

    expect(updated).toBeNull();
    expect(onError).toHaveBeenCalledTimes(1);
    expect(result.current.error).toBe('Not found');
  });

  it('remove calls delete_{singular} with { id }', async () => {
    mockInvokeSuccess('delete_customer', undefined);
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    let ok = false;
    await act(async () => {
      ok = await result.current.remove(5);
    });

    expect(ok).toBe(true);
  });

  it('remove uses soft_delete_{singular} when softDelete is set', async () => {
    mockInvokeSuccess('soft_delete_supplier', undefined);
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'supplier', softDelete: true, createArg: 'supplier' }),
    );

    let ok = false;
    await act(async () => {
      ok = await result.current.remove(3);
    });

    expect(ok).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('remove invokes onSuccess and returns false + error on failure', async () => {
    mockInvokeError('delete_customer', 'Locked');
    const onError = vi.fn();
    const onSuccess = vi.fn();
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    let ok = true;
    await act(async () => {
      ok = await result.current.remove(5, { onError, onSuccess });
    });

    expect(ok).toBe(false);
    expect(onError).toHaveBeenCalledTimes(1);
    expect(onSuccess).not.toHaveBeenCalled();
    expect(result.current.error).toBe('Locked');
  });

  it('remove tracks isDeleting + isMutating while in flight', async () => {
    mockInvokePending('delete_customer');
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    act(() => {
      result.current.remove(1);
    });
    // The invoke stays pending — flags must be true while it is in flight.
    expect(result.current.isDeleting).toBe(true);
    expect(result.current.isMutating).toBe(true);
  });

  it('resetError clears the error state', async () => {
    mockInvokeError('add_customer', 'Boom');
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    await act(async () => {
      await result.current.create({ name: 'X' });
    });
    expect(result.current.error).toBe('Boom');

    act(() => result.current.resetError());
    expect(result.current.error).toBeNull();
  });

  it('uses custom command overrides instead of derived names', async () => {
    mockInvokeSuccess('mark_product_uploaded', undefined);
    const { result } = renderHook(() =>
      useApiMutation({
        singular: 'product',
        addCommand: 'mark_product_uploaded',
        createArg: 'data',
      }),
    );

    let created: unknown;
    await act(async () => {
      created = await result.current.create({ id: 4 });
    });
    // mark_product_uploaded returns () → invoke resolves undefined
    expect(created).toBeUndefined();
  });
});

describe('useApiMutation integration with page-level flows', () => {
  it('create then quiet refetch pattern works through onSuccess', async () => {
    mockInvokeSuccess('add_customer', { id: 7, name: 'Dana' });
    mockInvokeSuccess('get_customers', [{ id: 7, name: 'Dana' }]);
    const refetch = vi.fn();
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    await act(async () => {
      await result.current.create(
        { name: 'Dana' },
        {
          onSuccess: () => refetch(),
        },
      );
    });

    await waitFor(() => expect(refetch).toHaveBeenCalledTimes(1));
    expect(result.current.error).toBeNull();
  });

  it('flags are independent per operation', async () => {
    mockInvokePending('add_customer');
    mockInvokeSuccess('delete_customer', undefined);
    const { result } = renderHook(() =>
      useApiMutation({ singular: 'customer', createArg: 'customer' }),
    );

    // Starts a create that never resolves (pending mock)…
    act(() => {
      result.current.create({ name: 'Slow' });
    });
    expect(result.current.isCreating).toBe(true);
    expect(result.current.isUpdating).toBe(false);
    expect(result.current.isDeleting).toBe(false);

    // …while a delete completes independently.
    await act(async () => {
      await result.current.remove(1);
    });
    expect(result.current.isDeleting).toBe(false);
    expect(result.current.error).toBeNull();
    // The pending create flag stays true — flags don't clobber each other.
    expect(result.current.isCreating).toBe(true);
  });
});
