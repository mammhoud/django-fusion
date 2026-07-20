import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { MdPerson, MdPhone, MdEmail, MdStars, MdAdd, MdEdit, MdDelete, MdSearch, MdClose } from 'react-icons/md';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import { Customer } from '../types';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';
import { useStatusToast } from '../hooks/useStatusToast';
import StatusToast from '../components/StatusToast';
import {
  useGetCustomersQuery,
  useAddCustomerMutation,
  useUpdateCustomerMutation,
  useDeleteCustomerMutation,
} from '../store/api/endpoints/customers';

export default function Customers() {
  const { t } = useTranslation();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Customer | null>(null);
  const [form, setForm] = useState({ name: '', phone: '', email: '', notes: '' });

  // Status toast
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  // Debounced search
  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  // RTK Query — paginated fetch with auto-caching
  const [page] = useState(1);
  const { data, isLoading } = useGetCustomersQuery({ page, per_page: 200 });
  const [addCustomer] = useAddCustomerMutation();
  const [updateCustomer] = useUpdateCustomerMutation();
  const [deleteCustomer] = useDeleteCustomerMutation();

  // Sync RTK Query data to local state
  useEffect(() => {
    if (data?.data) setCustomers(data.data);
  }, [data]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        await updateCustomer({ id: editing.id, data: form }).unwrap();
      } else {
        await addCustomer(form).unwrap();
      }
      setShowForm(false);
      setEditing(null);
      setForm({ name: '', phone: '', email: '', notes: '' });
      showSuccess(t('common.saved'));
    } catch (error) {
      console.error('Error saving customer:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
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
    try {
      await deleteCustomer(id).unwrap();
      showSuccess(t('common.deleted'));
    } catch (error) {
      console.error('Error deleting customer:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
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
    <PageLayout title={t('customers.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex justify-between items-center gap-3">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('customers.title')}</h1>
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => { setShowForm(true); setEditing(null); setForm({ name: '', phone: '', email: '', notes: '' }); }}
            className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition-colors shrink-0"
          >
            <MdAdd /> {t('customers.addCustomer')}
          </motion.button>
        </div>

        {/* Search bar */}
        <div className="card--glass rounded-xl p-3">
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <MdSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('customers.searchPlaceholder') || 'Search customers...'}
                aria-label={t('customers.searchPlaceholder') || 'Search customers'}
                className="w-full pl-10 pr-9 py-2 rounded-lg bg-white/50 dark:bg-white/5
                  border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white
                  placeholder:text-slate-400 dark:placeholder:text-gray-500
                  focus:outline-none focus:border-teal-400 transition-colors text-sm"
              />
              {isFiltering ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  aria-label="filtering"
                  className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4
                    border-2 border-teal-400 border-t-transparent rounded-full"
                />
              ) : search ? (
                <button
                  onClick={() => setSearch('')}
                  aria-label={t('common.clear')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-white"
                >
                  <MdClose className="w-4 h-4" />
                </button>
              ) : null}
            </div>
            <span className="text-xs text-slate-500 dark:text-gray-400 whitespace-nowrap">
              {filteredCustomers.length} / {customers.length}
            </span>
          </div>
        </div>

        {showForm && (
          <motion.form
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            onSubmit={handleSubmit}
            className="card--glass rounded-xl p-4 space-y-3"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <input
                type="text"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                placeholder={t('customers.name')}
                required
                className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white"
              />
              <input
                type="text"
                value={form.phone}
                onChange={e => setForm({ ...form, phone: e.target.value })}
                placeholder={t('customers.phone')}
                className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white"
              />
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                placeholder={t('customers.email')}
                className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white"
              />
              <input
                type="text"
                value={form.notes}
                onChange={e => setForm({ ...form, notes: e.target.value })}
                placeholder={t('customers.notes')}
                className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white"
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">
                {editing ? t('common.update') : t('common.save')}
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-slate-300 dark:bg-slate-700 rounded-lg">
                {t('common.cancel')}
              </button>
            </div>
          </motion.form>
        )}

        {isLoading ? (
          <div className="card--glass rounded-xl p-8 text-center">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              className="w-6 h-6 border-2 border-teal-400 border-t-transparent rounded-full inline-block mb-2"
            />
            <p className="text-slate-500 dark:text-gray-400 text-sm">{t('common.loading')}</p>
          </div>
        ) : filteredCustomers.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            {debouncedSearch
              ? (t('common.noDataFound') || 'No matches found.')
              : (t('customers.noCustomers'))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCustomers.map(customer => (
              <motion.div
                key={customer.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="card--glass rounded-xl p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-teal-100 dark:bg-teal-900/30 flex items-center justify-center text-teal-600 dark:text-teal-400">
                      <MdPerson className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">{customer.name}</h3>
                      <div className="flex items-center gap-1 text-sm text-slate-500 dark:text-gray-400">
                        <MdStars className="text-amber-500" />
                        <span>{customer.loyalty_points.toFixed(0)} {t('customers.points')}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleEdit(customer)} className="p-2 text-slate-600 hover:text-teal-600">
                      <MdEdit />
                    </button>
                    <button onClick={() => handleDelete(customer.id)} className="p-2 text-slate-600 hover:text-red-600">
                      <MdDelete />
                    </button>
                  </div>
                </div>
                <div className="mt-3 space-y-1 text-sm text-slate-600 dark:text-gray-400">
                  {customer.phone && <div className="flex items-center gap-1"><MdPhone /> {customer.phone}</div>}
                  {customer.email && <div className="flex items-center gap-1"><MdEmail /> {customer.email}</div>}
                </div>
              </motion.div>
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
