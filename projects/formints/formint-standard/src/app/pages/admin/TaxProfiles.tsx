import { useCallback, useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import Card from '../../../components/ui/Card';
import PageLayout from '../../../components/layout/PageLayout';
import RoleGate from '../../../components/RoleGate';
import { TaxProfile } from '../../../types';

const SETTINGS_PERMISSION = 'manage:settings';

export default function TaxProfiles() {
  const [profiles, setProfiles] = useState<TaxProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [form, setForm] = useState({ name: '', rate: '0', isDefault: false });

  const loadProfiles = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const rows = await invoke<TaxProfile[]>('list_tax_profiles', { activeOnly: false, search: null });
      setProfiles(rows ?? []);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProfiles();
  }, [loadProfiles]);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await invoke('create_tax_profile', {
        name: form.name,
        rate: Number(form.rate) / 100,
        isDefault: form.isDefault,
      });
      setForm({ name: '', rate: '0', isDefault: false });
      setFormOpen(false);
      await loadProfiles();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  const remove = async (id: number) => {
    if (!window.confirm('Deactivate this tax profile?')) return;
    try {
      await invoke('delete_tax_profile', { id });
      await loadProfiles();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    }
  };

  return (
    <PageLayout title="Tax profiles" background="bg-base-200/50">
      <div className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div><h1 className="text-2xl font-bold text-base-content">Tax profiles</h1><p className="text-sm text-base-content/55">Keep named rates consistent across products and sales.</p></div>
          <RoleGate permission={SETTINGS_PERMISSION}><button type="button" className="btn btn-primary gap-2" onClick={() => setFormOpen(open => !open)}><span className="ri-add-line" /> Add profile</button></RoleGate>
        </div>

        {error && <div role="alert" className="alert alert-error">{error}</div>}

        {formOpen && <RoleGate permission={SETTINGS_PERMISSION}><Card padding="md"><form onSubmit={submit} className="grid grid-cols-1 gap-3 md:grid-cols-4"><input className="input" required placeholder="Profile name" value={form.name} onChange={event => setForm({ ...form, name: event.target.value })} /><input className="input" required min="0" max="100" step="0.01" type="number" placeholder="Rate (%)" value={form.rate} onChange={event => setForm({ ...form, rate: event.target.value })} /><label className="flex items-center gap-2 text-sm"><input type="checkbox" className="checkbox checkbox-primary" checked={form.isDefault} onChange={event => setForm({ ...form, isDefault: event.target.checked })} /> Set default</label><div className="flex gap-2"><button className="btn btn-primary" type="submit">Save profile</button><button className="btn btn-ghost" type="button" onClick={() => setFormOpen(false)}>Cancel</button></div></form></Card></RoleGate>}

        {isLoading ? <div className="py-12 text-center text-base-content/50">Loading tax profiles…</div> : <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">{profiles.map(profile => <Card key={profile.id} padding="md" className={!profile.is_active ? 'opacity-60' : undefined}><div className="flex items-start justify-between gap-3"><div><p className="text-lg font-semibold">{profile.name}</p><p className="text-sm text-base-content/55">{(profile.rate * 100).toFixed(2)}%</p></div>{profile.is_default && <span className="badge badge-primary badge-soft">Default</span>}</div><div className="mt-4 flex items-center justify-between text-sm text-base-content/60"><span>{profile.is_active ? 'Active' : 'Inactive'}</span>{profile.is_active && <RoleGate permission={SETTINGS_PERMISSION}><button type="button" className="btn btn-ghost btn-sm text-error" onClick={() => remove(profile.id)}>Deactivate</button></RoleGate>}</div></Card>)}</div>}
      </div>
    </PageLayout>
  );
}
