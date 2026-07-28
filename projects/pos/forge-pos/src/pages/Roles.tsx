import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Card from '../components/Card';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import { Role } from '../types';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

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
      setPermissionCatalog(catalog);
    } catch (error) {
      console.error('Error loading permission catalog from backend:', error);
      setCatalogError(true);
      // No fallback — permission system is backend-driven; the UI will show
      // a hint to use the custom permissions field below
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
    // Separate known from custom
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
    // Build full permission set: known + custom
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

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('soft_delete_role', { id });
      loadRoles({ quiet: true });
    } catch (error) {
      console.error('Error deleting role:', error);
      loadRoles({ quiet: true });
    }
  };

  // Filtered + sorted roles
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
        {/* ── Header ── */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-base-content">{t('roles.title')}</h1>
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={openAddForm}
            className="btn btn-primary gap-2"
          >
            <span className="icon-[tabler--plus] w-4 h-4" /> {t('roles.addRole')}
          </motion.button>
        </div>

        {/* ── Search + sort ── */}
        <Card padding="sm">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            {/* Search */}
            <div className="relative flex-1">
              <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 text-base-content/40" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t('roles.searchPlaceholder') || 'Search roles...'}
                aria-label={t('roles.searchPlaceholder') || 'Search roles'}
                className="input input-bordered w-full pl-10 pr-9"
              />
              {isFiltering ? (
                <span className="loading loading-spinner loading-xs absolute right-3 top-1/2 -translate-y-1/2 text-primary" />
              ) : search ? (
                <button
                  onClick={() => setSearch('')}
                  aria-label={t('common.clear')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content"
                >
                  <span className="icon-[tabler--x] w-4 h-4" />
                </button>
              ) : null}
            </div>

            {/* Sort */}
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as 'newest' | 'name-asc' | 'name-desc')}
              aria-label={t('roles.sortBy') || 'Sort by'}
              className="select select-bordered sm:w-44"
            >
              <option value="newest">{t('roles.sortNewest') || 'Newest'}</option>
              <option value="name-asc">{t('roles.sortNameAsc') || 'Name (A→Z)'}</option>
              <option value="name-desc">{t('roles.sortNameDesc') || 'Name (Z→A)'}</option>
            </select>

            <span className="text-xs text-base-content/50 whitespace-nowrap px-2 tabular-nums">
              {filteredRoles.length} / {roles.length}
            </span>
          </div>
        </Card>

        {/* ── Add/Edit Form ── */}
        {showForm && (
          <Card padding="md">
            <form onSubmit={handleSubmit} className="space-y-5">
              <h3 className="text-lg font-semibold text-base-content flex items-center gap-2">
                <span className="icon-[tabler--shield] w-5 h-5 text-primary" />
                {editing ? t('common.edit') : t('common.add')} Role
              </h3>

              {/* Role Name */}
              <div>
                <label className="label">
                  <span className="label-text font-medium">{t('roles.name')}</span>
                </label>
                <input
                  type="text"
                  value={formName}
                  onChange={e => setFormName(e.target.value)}
                  placeholder="e.g. Manager, Cashier, Chef"
                  required
                  className="input input-bordered w-full"
                  autoFocus
                />
              </div>

              {/* Known Permissions — FlyonUI checkbox grid */}
              <div>
                <label className="label">
                  <span className="label-text font-medium">Permissions</span>
                  <span className="label-text-alt text-base-content/50">
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
                      <span className="icon-[tabler--shield-off] w-8 h-8 text-base-content/30" />
                      <p className="text-sm text-base-content/50 text-center">
                        Could not load permissions from backend. Use the custom permissions field below.
                      </p>
                    </div>
                  ) : (
                    catalogToUse.map(p => {
                      const checked = formPermissions.has(p.key);
                      return (
                        <label
                          key={p.key}
                          className={`flex items-center gap-2.5 p-2 rounded-lg border cursor-pointer transition-all select-none ${
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
                          <span className={`icon-[tabler--${p.icon}] w-3.5 h-3.5 text-base-content/60 shrink-0`} />
                          <span className="text-xs font-medium text-base-content leading-tight">{p.label}</span>
                        </label>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Custom permissions (comma-separated) */}
              <div>
                <label className="label">
                  <span className="label-text font-medium">Custom Permissions</span>
                  <span className="label-text-alt text-base-content/50">Comma-separated</span>
                </label>
                <input
                  type="text"
                  value={customPermissions}
                  onChange={e => setCustomPermissions(e.target.value)}
                  placeholder="e.g. manage:reports, view:audit"
                  className="input input-bordered w-full font-mono text-sm"
                />
                <p className="text-xs text-base-content/40 mt-1">
                  Add custom permission keys not listed above, separated by commas.
                </p>
              </div>

              {/* Buttons */}
              <div className="flex gap-2 pt-2">
                <button type="submit" className="btn btn-primary gap-2">
                  <span className="icon-[tabler--device-floppy] w-4 h-4" />
                  {editing ? t('common.update') : t('common.save')}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost gap-2">
                  <span className="icon-[tabler--x] w-4 h-4" />
                  {t('common.cancel')}
                </button>
              </div>
            </form>
          </Card>
        )}

        {/* ── Role Cards Grid ── */}
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <span className="loading loading-spinner loading-lg text-primary" />
          </div>
        ) : filteredRoles.length === 0 ? (
          <Card className="text-center py-12">
            <span className="icon-[tabler--shield-off] w-12 h-12 mx-auto mb-3 text-base-content/30" />
            <p className="text-base-content/50">
              {debouncedSearch
                ? (t('common.noDataFound') || 'No matches found.')
                : (t('roles.noRoles'))}
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredRoles.map(role => {
              const perms = parsePermissions(role.permissions);
              const knownCount = [...perms].filter(p => catalogToUse.some(c => c.key === p)).length;

              return (
                <Card key={role.id} padding="md" hover>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm shadow-sm
                        ${role.is_active
                          ? 'bg-primary/10 text-primary'
                          : 'bg-base-300/50 text-base-content/40'
                        }`}
                      >
                        <span className="icon-[tabler--shield] w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-base-content text-sm">{role.name}</h3>
                        <p className="text-xs text-base-content/50">
                          {role.is_active ? t('common.active') : t('common.inactive')}
                          {' · '}{knownCount} permissions
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => openEditForm(role)} className="btn btn-ghost btn-xs btn-square text-base-content/40 hover:text-info">
                        <span className="icon-[tabler--pencil] w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(role.id)} className="btn btn-ghost btn-xs btn-square text-base-content/40 hover:text-error">
                        <span className="icon-[tabler--trash] w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Permission badges */}
                  {perms.size > 0 ? (
                    <div className="flex flex-wrap gap-1.5">
                      {catalogToUse.filter(p => perms.has(p.key)).map(p => (
                        <span key={p.key} className="badge badge-soft badge-primary badge-sm gap-1">
                          <span className={`icon-[tabler--${p.icon}] w-3 h-3`} />
                          {p.label}
                        </span>
                      ))}
                      {[...perms].filter(p => !catalogToUse.some(c => c.key === p)).map(p => (
                        <span key={p} className="badge badge-soft badge-neutral badge-sm font-mono text-[10px]">
                          {p}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-base-content/30 italic">No permissions</p>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
