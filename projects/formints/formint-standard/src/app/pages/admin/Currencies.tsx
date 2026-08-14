import { useCallback, useEffect, useMemo, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import Card from '../../../components/ui/Card';
import PageLayout from '../../../components/layout/PageLayout';
import RoleGate from '../../../components/RoleGate';
import { Currency } from '../../../types';

const SETTINGS_PERMISSION = 'manage:settings';

export default function Currencies() {
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [form, setForm] = useState({ code: '', name: '', symbol: '', exchangeRate: '1', isDefault: false });

  const loadCurrencies = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const rows = await invoke<Currency[]>('list_currencies', {
        activeOnly: false,
        search: search.trim() || null,
      });
      setCurrencies(rows ?? []);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setIsLoading(false);
    }
  }, [search]);

  useEffect(() => {
    void loadCurrencies();
  }, [loadCurrencies]);

  const activeCurrencies = useMemo(() => currencies.filter(currency => currency.is_active), [currencies]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await invoke('create_currency', {
        code: form.code,
        name: form.name,
        symbol: form.symbol,
        exchangeRate: Number(form.exchangeRate),
        isDefault: form.isDefault,
      });
      setForm({ code: '', name: '', symbol: '', exchangeRate: '1', isDefault: false });
      setFormOpen(false);
      await loadCurrencies();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const remove = async (id: number) => {
    if (!window.confirm('Deactivate this currency?')) return;
    try {
      await invoke('delete_currency', { id });
      await loadCurrencies();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  return (
    <PageLayout title="Currencies" background="bg-base-200/50">
      <div className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-base-content">Currencies</h1>
            <p className="text-sm text-base-content/55">Manage active ISO-4217 currencies and the default sale currency.</p>
          </div>
          <RoleGate permission={SETTINGS_PERMISSION}>
            <button type="button" className="btn btn-primary gap-2" onClick={() => setFormOpen(open => !open)}>
              <span className="ri-add-line" /> Add currency
            </button>
          </RoleGate>
        </div>

        {error && <div role="alert" className="alert alert-error">{error}</div>}

        {formOpen && (
          <RoleGate permission={SETTINGS_PERMISSION}>
            <Card padding="md">
              <form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-5">
                <input className="input" required maxLength={3} placeholder="Code (USD)" value={form.code} onChange={event => setForm({ ...form, code: event.target.value })} />
                <input className="input" required placeholder="Name" value={form.name} onChange={event => setForm({ ...form, name: event.target.value })} />
                <input className="input" placeholder="Symbol ($)" value={form.symbol} onChange={event => setForm({ ...form, symbol: event.target.value })} />
                <input className="input" required min="0.000001" step="any" type="number" placeholder="Rate" value={form.exchangeRate} onChange={event => setForm({ ...form, exchangeRate: event.target.value })} />
                <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="checkbox checkbox-primary" checked={form.isDefault} onChange={event => setForm({ ...form, isDefault: event.target.checked })} /> Set default</label>
                <div className="flex gap-2 md:col-span-5"><button className="btn btn-primary" type="submit">Save currency</button><button className="btn btn-ghost" type="button" onClick={() => setFormOpen(false)}>Cancel</button></div>
              </form>
            </Card>
          </RoleGate>
        )}

        <Card padding="sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <input className="input max-w-sm" placeholder="Search currencies" value={search} onChange={event => setSearch(event.target.value)} />
            <span className="text-sm text-base-content/55">{activeCurrencies.length} active · {currencies.length} total</span>
          </div>
        </Card>

        {isLoading ? <div className="py-12 text-center text-base-content/50">Loading currencies…</div> : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {currencies.map(currency => (
              <Card key={currency.id} padding="md" className={!currency.is_active ? 'opacity-60' : undefined}>
                <div className="flex items-start justify-between gap-3">
                  <div><p className="text-lg font-semibold">{currency.symbol || currency.code} {currency.code}</p><p className="text-sm text-base-content/55">{currency.name}</p></div>
                  {currency.is_default && <span className="badge badge-primary badge-soft">Default</span>}
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-base-content/60"><span>Rate {currency.exchange_rate}</span><span>{currency.is_active ? 'Active' : 'Inactive'}</span></div>
                {currency.is_active && <RoleGate permission={SETTINGS_PERMISSION}><button type="button" className="btn btn-ghost btn-sm mt-3 text-error" onClick={() => remove(currency.id)}>Deactivate</button></RoleGate>}
              </Card>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
