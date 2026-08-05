# POS Full — Component Patterns

> **Directory:** `docs/typescript/`
> **Framework:** React 18 + TypeScript + Vite + Tailwind CSS

---

## Standard Page Component Pattern

```tsx
import PageLayout from '@/components/layout/PageLayout';
import { FusionPage } from '@/components/fusion/FusionPage';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { useState } from 'react';
// RTK Query hooks
import { useGetXQuery, useAddXMutation } from '@/store/api/endpoints/resource';

export default function MyPage() {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);

  const { data, isLoading, error } = useGetXQuery();
  const [addItem] = useAddXMutation();

  const handleSubmit = async (e: React.FormEvent) => { ... };

  return (
    <PageLayout title={t('myPage.title')} background="bg-slate-100 dark:bg-slate-900">
      {/* Header with Add button */}
      <div className="flex justify-between items-center gap-3">
        <h1 className="text-2xl font-bold">{t('myPage.title')}</h1>
        <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }}
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg">
          Add Item
        </motion.button>
      </div>

      {/* Search bar */}
      <div className="card--glass rounded-xl p-3">...</div>

      {/* Data grid — 4 states handled by FusionPage */}
      <FusionPage standalone data={data?.items} isLoading={isLoading} error={error}>
        {(items, _fallback) => (/* render */)}
      </FusionPage>
    </PageLayout>
  );
}
```

## CRUD Form Modal Pattern

```tsx
// State
const [editing, setEditing] = useState<Item | null>(null);
const [form, setForm] = useState<ItemForm>(initialForm);

// Open add
const handleAdd = () => {
  setEditing(null);
  setForm(initialForm);
  setShowForm(true);
};

// Open edit
const handleEdit = (item: Item) => {
  setEditing(item);
  setForm({ name: item.name, ... });
  setShowForm(true);
};

// Submit
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (editing) {
    await updateItem({ id: editing.id, data: form }).unwrap();
  } else {
    await addItem(form).unwrap();
  }
  setShowForm(false);
};

// Delete
const handleDelete = async (id: number) => {
  if (!confirm(t('common.confirmDelete'))) return;
  await deleteItem(id).unwrap();
};
```

## Card Grid Pattern

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map((item, idx) => (
    <motion.div
      key={item.id}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="card--glass rounded-xl p-4"
    >
      <div className="flex items-start justify-between">
        <h3 className="font-semibold">{item.name}</h3>
        <div className="flex gap-1">
          <button onClick={() => handleEdit(item)} className="p-2 text-slate-600 hover:text-teal-600">
            <MdEdit />
          </button>
          <button onClick={() => handleDelete(item.id)} className="p-2 text-slate-600 hover:text-red-600">
            <MdDelete />
          </button>
        </div>
      </div>
    </motion.div>
  ))}
</div>
```

## Debounced Search Pattern

```tsx
import { useDebouncedSearch } from '@/hooks/useDebouncedSearch';

const { query, setQuery, debouncedQuery, isPending } = useDebouncedSearch();

// Filter based on debounced query
const filtered = debouncedQuery
  ? items.filter(i => i.name.toLowerCase().includes(debouncedQuery.toLowerCase()))
  : items;

// Search input with loading spinner
<input value={query} onChange={e => setQuery(e.target.value)} />
{isPending && <Spinner />}
```

## Status Toast Pattern

```tsx
import { useStatusToast } from '@/hooks/useStatusToast';
import StatusToast from '@/components/pos/StatusToast';

const { status, showSuccess, showError, dismiss } = useStatusToast();

// On success
await addItem(form).unwrap();
showSuccess(t('common.saved'));

// On error
catch (error) {
  showError(t('common.error'));
}

// Render
<StatusToast type={status?.type} message={status?.message}
  visible={!!status} onDismiss={dismiss} />
```
