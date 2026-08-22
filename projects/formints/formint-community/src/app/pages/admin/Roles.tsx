import { useState, useEffect } from 'react';
import Card from '../../../components/ui/Card';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../../components/layout/PageLayout';
import { iconClass } from '../../../lib/icons';
import { useTranslation } from 'react-i18next';
import { Role } from '../../../types';
import { useDebouncedSearch } from '../../../hooks/useDebouncedSearch';
import SearchInput from '../../../components/ui/SearchInput';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';

// ── Permission definition (returned from Rust backend) ──
interface PermissionDef {
  key: string;
  label: string;
  icon: string;
}

// ── Helper: parse JSON permissions string → Set<string> ──
function parsePermissions(raw: string): Set<string> {
  try {
    const arr = JSON.parse(raw);
    return new Set<string>(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set<string>();
  }
}

// ── Helper: serialize Set<string> → JSON string ──
function serializePermissions(perms: Set<string>): string {
  return JSON.stringify([...perms].sort());
}

export default function Roles() {
  const { t } = useTranslation();
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Role | null>(null);
  const [formName, setFormName] = useState('');
  const [formPermissions, setFormPermissions] = useState<Set<string>>(new Set());
  const [customPermissions, setCustomPermissions] = useState('');

  // ── Permission catalog loaded from Rust backend ──
  const [permissionCatalog, setPermissionCatalog] = useState<PermissionDef[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogError, setCatalogError] = useState(false);

  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [sortKey, setSortKey] = useState<'newest' | 'name-asc' | 'name-desc'>('newest');

  useEffect(() => {
    loadRoles();
    loadPermissionCatalog();
  }, []);

  const loadPermissionCatalog = async () => {
    setCatalogLoading(true);
    setCatalogError(false);
    try {
      const catalog = await invoke<PermissionDef[]>('get_permission_catalog');
      setPermissionCatalog(catalog ?? []);
    } catch (error) {
      console.error('Error loading permission catalog from backend:', error);
      setCatalogError(true);
    } finally {
      setCatalogLoading(false);
    }
  };

  const loadRoles = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<Role[]>('get_roles');
      setRoles(data);
    } catch (error) {
      console.error('Error loading roles:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const openAddForm = () => {
    setEditing(null);
    setFormName('');
    setFormPermissions(new Set());
    setCustomPermissions('');
    setShowForm(true);
  };

  const openEditForm = (role: Role) => {
    setEditing(role);
    setFormName(role.name);
    const perms = parsePermissions(role.permissions);
    const knownKeys = new Set(permissionCatalog.map(p => p.key));
    const known = new Set([...perms].filter(p => knownKeys.has(p)));
    const custom = [...perms].filter(p => !knownKeys.has(p)).join(', ');
    setFormPermissions(known);
    setCustomPermissions(custom);
    setShowForm(true);
  };

  const togglePermission = (key: string) => {
    setFormPermissions(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const customList = customPermissions
      .split(',')
      .map(s => s.trim())
      .filter(Boolean);
    const allPerms = new Set([...formPermissions, ...customList]);
    const payload = {
      name: formName,
      permissions: serializePermissions(allPerms),
    };

    try {
      if (editing) {
        await invoke('update_role', { id: editing.id, update: payload });
      } else {
        await invoke('add_role', { role: payload });
      }
      setShowForm(false);
      setEditing(null);
      loadRoles({ quiet: true });
    } catch (error) {
      console.error('Error saving role:', error);
      loadRoles({ quiet: true });
    }
  };

  const [toDelete, setToDelete] = useState<Role | null>(null);

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await invoke('soft_delete_role', { id: toDelete.id });
      setToDelete(null);
      loadRoles({ quiet: true });
    } catch (error) {
      console.error('Error deleting role:', error);
      loadRoles({ quiet: true });
    }
  };

  const q = debouncedSearch.trim().toLowerCase();
  const filteredRoles = (() => {
    let result = q
      ? roles.filter(r =>
          r.name.toLowerCase().includes(q) ||
          (r.permissions || '').toLowerCase().includes(q)
        )
      : roles;
    const sorted = [...result];
    switch (sortKey) {
      case 'name-asc': sorted.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'name-desc': sorted.sort((a, b) => b.name.localeCompare(a.name)); break;
      case 'newest':
      default: sorted.sort((a, b) => b.id - a.id);
    }
    return sorted;
  })();

  const catalogToUse = permissionCatalog;

  return (
    <PageLayout title={t('roles.title')} background="bg-base-200/50">
      <div className="space-y-4">
        {/* ── Eyebrow tag ── */}
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-primary/10 text-primary">
            <span className="ri-shield-line ri-12px" />
            Access Control
          </span>
        </div>

        {/* ── Header ── */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-base-content">{t('roles.title')}</h1>
            <p className="text-sm text-base-content/50 mt-0.5">
              {roles.length} {t('roles.totalRoles') || 'roles'}
            </p>
          </div>
          <button
            onClick={openAddForm}
            className="btn btn-primary btn-sm gap-1 shrink-0 active:scale-[0.98] transition-transform"
          >
            <span className="ri-add-line ri-14px" /> {t('roles.addRole')}
          </button>
        </div>

        {/* ── Search + sort — compact bezel ── */}
        <Card padding="sm" variant="bezel">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder={t('roles.searchPlaceholder') || 'Search roles...'}
              ariaLabel={t('roles.searchPlaceholder') || 'Search roles'}
              testId="roles-search-input"
              loading={isFiltering}
              className="flex-1"
            />

            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as 'newest' | 'name-asc' | 'name-desc')}
              aria-label={t('roles.sortBy') || 'Sort by'}
              className="select h-8 text-xs sm:w-44"
            >
              <option value="newest">{t('roles.sortNewest') || 'Newest'}</option>
              <option value="name-asc">{t('roles.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('roles.sortNameDesc') || 'Name (Z→A)'}</option>
            </select>

            <span className="text-[10px] text-base-content/40 whitespace-nowrap px-2 tabular-nums">
              {filteredRoles.length} / {roles.length}
            </span>
          </div>
        </Card>

        {/* ── Add/Edit Form ── */}
        {showForm && (
          <form onSubmit={handleSubmit} className="bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-2xl p-5 space-y-4 shadow-lg overflow-hidden">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-semibold text-base-content flex items-center gap-2">
                <span className="ri-shield-line ri-16px text-primary" />
                {editing ? t('common.edit') : t('common.add')} Role
              </h3>
              <button type="button" onClick={() => setShowForm(false)} className="w-7 h-7 rounded-full bg-base-200 flex items-center justify-center hover:bg-base-300 transition-colors">
                <span className="ri-close-line ri-14px" />
              </button>
            </div>

            {/* Role Name */}
            <div className="space-y-1">
              <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                {t('roles.name')} <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={formName}
                onChange={e => setFormName(e.target.value)}
                placeholder="e.g. Manager, Cashier, Chef"
                required
                className="input input-compact w-full"
                autoFocus
              />
            </div>

            {/* Known Permissions — compact checkbox grid */}
            <div className="space-y-1">
              <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                Permissions
                <span className="text-base-content/40 font-normal ml-2">
                  {formPermissions.size} of {catalogToUse.length} selected
                </span>
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                {catalogLoading ? (
                  <div className="col-span-full flex items-center justify-center py-8">
                    <span className="loading loading-spinner loading-md text-primary" />
                  </div>
                ) : catalogError ? (
                  <div className="col-span-full flex flex-col items-center justify-center py-6 gap-2">
                    <span className="ri-shield-line ri-32px text-base-content/30" />
                    <p className="text-xs text-base-content/50 text-center">
                      Could not load permissions from backend. Use the custom permissions field below.
                    </p>
                  </div>
                ) : (
                  catalogToUse.map(p => {
                    const checked = formPermissions.has(p.key);
                    return (
                      <label
                        key={p.key}
                        className={`flex items-center gap-2 p-2 rounded-lg border cursor-pointer transition-all select-none ${
                          checked
                            ? 'border-primary bg-primary/10'
                            : 'border-base-300/50 hover:border-base-300 bg-base-100/50'
                        }`}
                      >
                        <input
                          type="checkbox"
                          className="checkbox checkbox-primary checkbox-sm"
                          checked={checked}
                          onChange={() => togglePermission(p.key)}
                        />
                        <span className={iconClass(p.icon, 'w-3.5 h-3.5 text-base-content/60 shrink-0')} />
                        <span className="text-[11px] font-medium text-base-content leading-tight">{p.label}</span>
                      </label>
                    );
                  })
                )}
              </div>
            </div>

            {/* Custom permissions (comma-separated) */}
            <div className="space-y-1">
              <label className="block text-[11px] font-medium text-base-content/70 uppercase tracking-wide">
                Custom Permissions
                <span className="text-base-content/40 font-normal ml-2">Comma-separated</span>
              </label>
              <input
                type="text"
                value={customPermissions}
                onChange={e => setCustomPermissions(e.target.value)}
                placeholder="e.g. manage:reports, view:audit"
                className="input input-compact w-full font-mono text-xs"
              />
              <p className="text-[10px] text-base-content/40">
                Add custom permission keys not listed above, separated by commas.
              </p>
            </div>

            {/* Buttons */}
            <div className="flex gap-2 justify-end pt-2 border-t border-base-300/30">
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost btn-sm">
                {t('common.cancel')}
              </button>
              <button type="submit" className="btn btn-primary btn-sm gap-1.5">
                <span className="ri-save-3-line ri-14px" />
                {editing ? t('common.update') : t('common.save')}
              </button>
            </div>
          </form>
        )}

        {/* ── Role Cards Grid — Double-Bezel ── */}
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <span className="loading loading-spinner loading-lg text-primary" />
          </div>
        ) : filteredRoles.length === 0 ? (
          <Card className="text-center py-12">
            <span className="ri-shield-line ri-48px mx-auto mb-3 text-base-content/30" />
            <p className="text-base-content/50">
              {debouncedSearch
                ? (t('common.noDataFound') || 'No matches found.')
                : (t('roles.noRoles'))}
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {filteredRoles.map((role, idx) => {
              const perms = parsePermissions(role.permissions);
              const knownCount = [...perms].filter(p => catalogToUse.some(c => c.key === p)).length;

              return (
                <div
                  key={role.id}
                  className={`
                    group relative
                    overflow-hidden
                    bg-base-200/40 dark:bg-white/5
                    border border-base-300/25 dark:border-white/10
                    rounded-[1.5rem]
                    p-1.5
                    shadow-[var(--shadow-bezel-outer)]
                    transition-all duration-500 ease-[var(--ease-fluid)]
                    hover:-translate-y-0.5 hover:shadow-[var(--shadow-bezel-hover)]
                    ${!role.is_active ? 'opacity-60' : ''}
                    animate-fade-up delay-${Math.min(idx * 75, 450)}
                  `}
                >
                  {/* Accent bar */}
                  <div
                    className="absolute top-0 bottom-0 inset-inline-start-0 w-1 rounded-l-[inherit]"
                    style={{ backgroundColor: role.is_active ? 'var(--color-primary)' : 'var(--color-base-300)' }}
                  />

                  {/* Inner core */}
                  <div className="bg-base-100 dark:bg-base-900 rounded-[1.125rem] p-4 shadow-[var(--shadow-bezel-inner)] h-full">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm shadow-sm ${
                          role.is_active
                            ? 'bg-primary/10 text-primary'
                            : 'bg-base-300/50 text-base-content/40'
                        }`}>
                          <span className="ri-shield-line ri-20px" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-base-content text-sm">{role.name}</h3>
                          <p className="text-[10px] text-base-content/50">
                            {role.is_active ? t('common.active') : t('common.inactive')}
                            {' · '}{knownCount} permissions
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => openEditForm(role)} className="w-7 h-7 rounded-lg text-base-content/40 hover:text-info hover:bg-info/10 flex items-center justify-center transition-all duration-200 active:scale-95">
                          <span className="ri-pencil-line ri-14px" />
                        </button>
                        <button onClick={() => setToDelete(role)} className="w-7 h-7 rounded-lg text-base-content/40 hover:text-error hover:bg-error/10 flex items-center justify-center transition-all duration-200 active:scale-95">
                          <span className="ri-delete-bin-line ri-14px" />
                        </button>
                      </div>
                    </div>

                    {/* Permission badges */}
                    {perms.size > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {catalogToUse.filter(p => perms.has(p.key)).map(p => (
                          <span key={p.key} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary">
                            <span className={iconClass(p.icon, 'w-3 h-3')} />
                            {p.label}
                          </span>
                        ))}
                        {[...perms].filter(p => !catalogToUse.some(c => c.key === p)).map(p => (
                          <span key={p} className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono bg-base-200 text-base-content/60">
                            {p}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[10px] text-base-content/30 italic">No permissions</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <ConfirmDialog
        isOpen={!!toDelete}
        onClose={() => setToDelete(null)}
        onConfirm={handleDelete}
        title={t('roles.deleteTitle', 'Delete role')}
        message={t('roles.deleteMessage', 'This will remove the role and its permissions')}
        itemName={toDelete?.name ?? ''}
        confirmLabel={t('common.delete')}
      />
    </PageLayout>
  );
}
