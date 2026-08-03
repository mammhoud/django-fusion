import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import PageLayout from '../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import { Customer } from '../../types';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import { useStatusToast } from '../../hooks/useStatusToast';
import { useApiMutation } from '../../hooks/useApiMutation';
import Card from '../../components/ui/Card';
import StatusToast from '../../components/ui/StatusToast';

export default function Customers() {
  const { t } = useTranslation();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Customer | null>(null);
  const [form, setForm] = useState({ name: '', phone: '', email: '', notes: '' });

  // Status toast — quick pipe through the shared hook so load / mutation
  // errors can't silently disappear into console.error.
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  // AJAX-style debounced search — shared hook. Rename-destructure keeps the
  // existing JSX variable names (`search`, `debouncedSearch`, `isFiltering`).
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  useEffect(() => {
    loadCustomers();
  }, []);

  // ── Real-time customer updates from other windows ──
  useEffect(() => {
    const unlisten = listen('customers-updated', () => {
      loadCustomers({ quiet: true });
    });
    return () => { unlisten.then(fn => fn()); };
  }, []);

  const loadCustomers = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<Customer[]>('get_customers');
      setCustomers(data);
    } catch (error) {
      console.error('Error loading customers:', error);
      // Quiet reloads (post-mutation) must still surface failures — the user
      // needs to know if their add/edit didn't actually persist.
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  // ── Mutation hook — matches backend CRUD commands add/update/delete_customer ──
  const customerApi = useApiMutation<Customer>({
    singular: 'customer',
    createArg: 'customer',
  });

  // Shared mutation failure handling: quiet reload + visible error toast.
  const onMutationError = (err: Error) => {
    showError(`${t('common.error')}: ${err.message}`);
    loadCustomers({ quiet: true });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editing) {
      await customerApi.update(editing.id, form, {
        onSuccess: () => {
          window.dispatchEvent(new CustomEvent('customer-updated', { detail: { action: 'update', id: editing.id } }));
          setShowForm(false);
          setEditing(null);
          setForm({ name: '', phone: '', email: '', notes: '' });
          showSuccess(t('common.saved'));
          // Quiet reload — don't pulse the skeleton just because the form closed.
          loadCustomers({ quiet: true });
        },
        onError: onMutationError,
      });
    } else {
      await customerApi.create(form, {
        onSuccess: () => {
          window.dispatchEvent(new CustomEvent('customer-updated', { detail: { action: 'add' } }));
          setShowForm(false);
          setEditing(null);
          setForm({ name: '', phone: '', email: '', notes: '' });
          showSuccess(t('common.saved'));
          loadCustomers({ quiet: true });
        },
        onError: onMutationError,
      });
    }
  };

  const handleEdit = (customer: Customer) => {
    setEditing(customer);
    setForm({
      name: customer.name,
      phone: customer.phone || '',
      email: customer.email || '',
      notes: customer.notes || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    await customerApi.remove(id, {
      onSuccess: () => {
        showSuccess(t('common.deleted'));
        loadCustomers({ quiet: true });
      },
      onError: onMutationError,
    });
  };

  const q = debouncedSearch.trim().toLowerCase();
  const filteredCustomers = q
    ? customers.filter(c => {
        const haystack = [c.name, c.phone || '', c.email || '', c.notes || '']
          .join(' ')
          .toLowerCase();
        return haystack.includes(q);
      })
    : customers;

  return (
    <PageLayout title={t('customers.title')}>
      <div className="space-y-4">
        {/* ── Title row with inline search + add button ── */}
        <div className="flex items-center gap-2">
          <h1 className="text-lg font-bold text-base-content shrink-0">{t('customers.title')}</h1>
          <div className="relative flex-1 max-w-64">
            <span className="ri-search-line absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-base-content/50" />
            <div className="field">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('customers.searchPlaceholder') || 'Search...'}
                aria-label={t('customers.searchPlaceholder') || 'Search customers'}
                className="input w-full h-8 text-xs pl-8"
              />
            </div>
            {isFiltering ? (
              <div className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            ) : search ? (
              <button
                onClick={() => setSearch('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <span className="ri-close-line ri-12px" />
              </button>
            ) : null}
          </div>
          <span className="text-[11px] text-base-content/40 whitespace-nowrap shrink-0">
            {filteredCustomers.length}/{customers.length}
          </span>
          <button
            onClick={() => { setShowForm(true); setEditing(null); setForm({ name: '', phone: '', email: '', notes: '' }); }}
            className="btn btn-primary btn-sm gap-1 shrink-0"
          >
            <span className="ri-add-line ri-14px" />
            <span className="text-xs">{t('customers.addCustomer')}</span>
          </button>
        </div>

        {showForm && (
          <form
            onSubmit={handleSubmit}
          >
            <Card padding="md" className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="field"><input type="text" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder={t('customers.name')} required className="input w-full" /></div>
              <div className="field"><input type="text" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} placeholder={t('customers.phone')} className="input w-full" /></div>
              <div className="field"><input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder={t('customers.email')} className="input w-full" /></div>
              <div className="field"><input type="text" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder={t('customers.notes')} className="input w-full" /></div>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">
                {editing ? t('common.update') : t('common.save')}
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost">
                {t('common.cancel')}
              </button>
            </div>
            </Card>
          </form>
        )}

        {isLoading ? (
          <Card padding="2xl" center>
            <div className="w-6 h-6 border-2 border-teal-400 border-t-transparent rounded-full inline-block mb-2 animate-spin" />
            <p className="text-base-content/50 text-sm">{t('common.loading')}</p>
          </Card>
        ) : filteredCustomers.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No matches found.')
              : (t('customers.noCustomers'))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {filteredCustomers.map(customer => (
              <div
                key={customer.id}
              >
                <Card padding="md">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                      <span className="ri-user-line ri-20px" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">{customer.name}</h3>
                      <div className="flex items-center gap-1 text-sm text-base-content/50">
                        <span className="ri-star-line text-amber-500" />
                        <span>{customer.loyalty_points.toFixed(0)} {t('customers.points')}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleEdit(customer)} className="p-2 text-slate-600 hover:text-primary">
                      <span className="ri-pencil-line" />
                    </button>
                    <button onClick={() => handleDelete(customer.id)} className="p-2 text-slate-600 hover:text-red-600">
                      <span className="ri-delete-bin-line" />
                    </button>
                  </div>
                </div>
                <div className="mt-3 space-y-1 text-sm text-base-content/60">
                  {customer.phone && <div className="flex items-center gap-1"><span className="ri-phone-line" /> {customer.phone}</div>}
                  {customer.email && <div className="flex items-center gap-1"><span className="ri-mail-line" /> {customer.email}</div>}
                </div>
              </Card>
            </div>
            ))}
          </div>
        )}
      </div>

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}

