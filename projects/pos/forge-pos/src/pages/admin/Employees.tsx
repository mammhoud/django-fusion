import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Employee, NewEmployee, EmployeeType, NewEmployeeType } from '../../types';
import PageLayout from '../../components/layout/PageLayout';
import { SkeletonList, SkeletonTable } from '../../components/ui/Skeleton';
import { useTranslation } from 'react-i18next';
import FormModal from '../../components/ui/FormModal';
import { Badge } from '@/components/ui/badge';
import EmployeeWizard from '../../components/forms/EmployeeWizard';
import EmployeeTypeForm from '../../components/forms/EmployeeTypeForm';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import StatusToast from '../../components/ui/StatusToast';
import Card from '../../components/ui/Card';

type Tab = 'employees' | 'types';

const EMPLOYEE_TYPE_COLORS: Record<string, string> = {
  // Categorical role colors — theme tokens (bg-X + text-X-content pairs) so
  // avatar chips keep distinct hues AND correct contrast in every theme variant.
  'Manager': 'bg-secondary text-secondary-content',
  'Chef': 'bg-warning text-warning-content',
  'Waiter': 'bg-info text-info-content',
  'Cashier': 'bg-success text-success-content',
  'Driver': 'bg-accent text-accent-content',
  'Cleaner': 'bg-neutral text-neutral-content',
  'Other': 'bg-base-300 text-base-content',
};

const getTypeColor = (typeName: string) => {
  return EMPLOYEE_TYPE_COLORS[typeName] || 'bg-neutral text-neutral-content';
};

const initialNewEmployee: NewEmployee = {
  name: '',
  phone: null,
  email: null,
  employee_type_id: 0,
  salary: 0,
  joined_at: null,
  address: null,
  date_of_birth: null,
  national_id: null,
  emergency_contact: null,
  pay_frequency: 'monthly',
  hourly_rate: 0,
  bank_name: null,
  bank_account: null,
  tax_number: null,
  notes: null,
};

export default function Employees() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('employees');
  const [isLoading, setIsLoading] = useState(true);

  const getTabItems = () => [
    { key: 'employees' as Tab, label: t('employees.employeeList'), icon: <span className="ri-group-line" /> },
    { key: 'types' as Tab, label: t('employees.employeeTypes'), icon: <span className="ri-user-follow-line" /> },
  ];

  // Data states
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [employeeTypes, setEmployeeTypes] = useState<EmployeeType[]>([]);

  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('active');
  // Grid / list view toggle
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Unified add/edit modal state — ONE modal per entity, switching between
  // the add and edit modes (same pattern as ProductManager). The form data
  // lives in a single `{ ... }Form` object shared by both modes.
  type EmployeeModalState = { mode: 'add' } | { mode: 'edit'; employee: Employee } | null;
  const [employeeModal, setEmployeeModal] = useState<EmployeeModalState>(null);
  const [employeeForm, setEmployeeForm] = useState<NewEmployee>({ ...initialNewEmployee });
  const [showDeleteEmployee, setShowDeleteEmployee] = useState<Employee | null>(null);

  type TypeModalState = { mode: 'add' } | { mode: 'edit'; type: EmployeeType } | null;
  const [typeModal, setTypeModal] = useState<TypeModalState>(null);
  const [typeForm, setTypeForm] = useState<NewEmployeeType>({ name: '', description: null });
  const [showDeleteType, setShowDeleteType] = useState<EmployeeType | null>(null);

  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const loadData = useCallback(async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [emps, types] = await Promise.all([
        invoke<Employee[]>('get_employees', { includeInactive: true }),
        invoke<EmployeeType[]>('get_employee_types', { includeInactive: true }),
      ]);
      setEmployees(emps);
      setEmployeeTypes(types);
    } catch (error) {
      console.error('Error loading employee data:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  // ── Real-time employee updates from other windows ──
  useEffect(() => {
    const unlisten = listen('employees-updated', () => {
      loadData({ quiet: true });
    });
    return () => { unlisten.then(fn => fn()); };
  }, []);

  const showStatus = (type: 'success' | 'error', msg: string) => {
    setToast({ type, message: msg });
    setTimeout(() => setToast(null), 3000);
  };

  const getTypeName = (typeId: number) => {
    return employeeTypes.find(t => t.id === typeId)?.name || `Type #${typeId}`;
  };

  // ── Filtered employees ──
  const filteredEmployees = employees.filter(emp => {
    if (statusFilter === 'active' && !emp.is_active) return false;
    if (statusFilter === 'inactive' && emp.is_active) return false;
    if (typeFilter && emp.employee_type_id !== typeFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!emp.name.toLowerCase().includes(q) &&
          !(emp.phone || '').includes(q) &&
          !(emp.email || '').toLowerCase().includes(q)) return false;
    }
    return true;
  });

  // ── Salary summary ──
  const monthlySalaryTotal = employees
    .filter(e => e.is_active)
    .reduce((sum, e) => sum + e.salary, 0);

  // ── Employee CRUD (unified add/edit modal) ──
  const openAddEmployee = () => {
    setEmployeeForm({ ...initialNewEmployee });
    setEmployeeModal({ mode: 'add' });
  };

  const openEditEmployee = (emp: Employee) => {
    setEmployeeForm({
      name: emp.name,
      phone: emp.phone ?? null,
      email: emp.email ?? null,
      employee_type_id: emp.employee_type_id,
      salary: emp.salary,
      joined_at: emp.joined_at ?? null,
      address: emp.address ?? null,
      date_of_birth: emp.date_of_birth ?? null,
      national_id: emp.national_id ?? null,
      emergency_contact: emp.emergency_contact ?? null,
      pay_frequency: emp.pay_frequency || 'monthly',
      hourly_rate: emp.hourly_rate ?? 0,
      bank_name: emp.bank_name ?? null,
      bank_account: emp.bank_account ?? null,
      tax_number: emp.tax_number ?? null,
      notes: emp.notes ?? null,
    });
    setEmployeeModal({ mode: 'edit', employee: emp });
  };

  const closeEmployeeModal = () => setEmployeeModal(null);

  const handleSaveEmployee = async () => {
    if (!employeeForm.name.trim() || (employeeModal?.mode === 'add' && employeeForm.employee_type_id === 0)) return;
    const editing = employeeModal?.mode === 'edit' ? employeeModal.employee : null;
    // Normalize optional fields — the wizard keeps them as `string | null`.
    const payload = {
      name: employeeForm.name.trim(),
      phone: employeeForm.phone || null,
      email: employeeForm.email || null,
      employee_type_id: employeeForm.employee_type_id,
      salary: employeeForm.salary,
      joined_at: employeeForm.joined_at || null,
      address: employeeForm.address || null,
      date_of_birth: employeeForm.date_of_birth || null,
      national_id: employeeForm.national_id || null,
      emergency_contact: employeeForm.emergency_contact || null,
      pay_frequency: employeeForm.pay_frequency || 'monthly',
      hourly_rate: employeeForm.hourly_rate ?? 0,
      bank_name: employeeForm.bank_name || null,
      bank_account: employeeForm.bank_account || null,
      tax_number: employeeForm.tax_number || null,
      notes: employeeForm.notes || null,
    };
    try {
      if (editing) {
        await invoke('update_employee', {
          id: editing.id,
          update: payload,
        });
        window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'update', id: editing.id } }));
        showStatus('success', t('employees.successUpdated') || 'Employee updated!');
      } else {
        await invoke('add_employee', { employee: payload });
        window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'add' } }));
        showStatus('success', t('employees.successAdded') || 'Employee added successfully!');
      }
      closeEmployeeModal();
      loadData({ quiet: true });
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleReactivateEmployee = async (emp: Employee) => {
    try {
      await invoke('update_employee', {
        id: emp.id,
        update: { is_active: true },
      });
      window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'reactivate', id: emp.id } }));
      loadData({ quiet: true });
      showStatus('success', t('employees.successReactivated') || 'Employee activated.');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleDeleteEmployee = async () => {
    if (!showDeleteEmployee) return;
    try {
      await invoke('soft_delete_employee', { id: showDeleteEmployee.id });
      window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'delete', id: showDeleteEmployee.id } }));
      setShowDeleteEmployee(null);
      loadData({ quiet: true });
      showStatus('success', 'Employee deactivated.');
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Employee Type CRUD (unified add/edit modal) ──
  const openAddType = () => {
    setTypeForm({ name: '', description: null });
    setTypeModal({ mode: 'add' });
  };

  const openEditType = (et: EmployeeType) => {
    setTypeForm({ name: et.name, description: et.description ?? null });
    setTypeModal({ mode: 'edit', type: et });
  };

  const closeTypeModal = () => setTypeModal(null);

  const handleSaveType = async () => {
    if (!typeForm.name.trim()) return;
    const editing = typeModal?.mode === 'edit' ? typeModal.type : null;
    try {
      if (editing) {
        await invoke('update_employee_type', {
          id: editing.id,
          update: {
            name: typeForm.name.trim(),
            description: typeForm.description || null,
          }
        });
        showStatus('success', 'Employee type updated!');
      } else {
        await invoke('add_employee_type', { employeeType: typeForm });
        showStatus('success', 'Employee type added!');
      }
      closeTypeModal();
      loadData({ quiet: true });
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleDeleteType = async () => {
    if (!showDeleteType) return;
    try {
      await invoke('soft_delete_employee_type', { id: showDeleteType.id });
      setShowDeleteType(null);
      loadData({ quiet: true });
      showStatus('success', 'Employee type deactivated.');
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Loading State ──
  if (isLoading) {
    return (
      <PageLayout title={t('employees.title')}>
        <div className="space-y-6">
          <SkeletonList items={6} />
          <SkeletonTable rows={6} columns={5} />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={<><span className="ri-group-line text-info" /> Employees</>}
      background="bg-linear-to-br from-base-200 via-info/10 to-base-200"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <Card>
            <h2 className="text-base-content/80 text-sm">{t('employees.totalEmployees')}</h2>
            <p className="text-2xl font-bold text-base-content">{employees.filter(e => e.is_active).length}</p>
          </Card>
          <Card>
            <h2 className="text-base-content/80 text-sm">{t('employees.employeeTypes')}</h2>
            <p className="text-2xl font-bold text-info">{employeeTypes.filter(t => t.is_active).length}</p>
          </Card>
          <Card>
            <h2 className="text-base-content/80 text-sm">{t('employees.monthlySalary')}</h2>
            <p className="text-2xl font-bold text-success">{monthlySalaryTotal.toLocaleString()}</p>
          </Card>
          <Card>
            <h2 className="text-base-content/80 text-sm">{t('employees.avgSalary')}</h2>
            <p className="text-2xl font-bold text-secondary">
              {employees.filter(e => e.is_active).length > 0
                ? Math.round(monthlySalaryTotal / employees.filter(e => e.is_active).length).toLocaleString()
                : 0}
            </p>
          </Card>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {getTabItems().map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm transition-all active:scale-[0.98] shrink-0 ${
                activeTab === tab.key
                  ? 'bg-info text-white shadow-lg'
                  : 'bg-base-100/70 text-base-content/80 hover:bg-info/10 dark:hover:bg-info/30'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* ── TAB 1: EMPLOYEE LIST ── */}
        {activeTab === 'employees' && (
          <div>
            {/* Filters & Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <span className="ri-search-line absolute left-3 top-1/2 -translate-y-1/2 text-base-content/50" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder={t('employees.searchPlaceholder')}
                    className="input w-48 pl-9"
                  />
                </div>
                <select
                  value={typeFilter ?? ''}
                  onChange={e => setTypeFilter(e.target.value ? Number(e.target.value) : null)}
                  className="select"
                >
                  <option value="">{t('employees.allTypes')}</option>
                  {employeeTypes.filter(t => t.is_active).map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
                <div className="flex rounded-lg overflow-hidden border border-slate-300 dark:border-gray-600">
                  {(['all', 'active', 'inactive'] as const).map(s => (
                    <button
                      key={s}
                      onClick={() => setStatusFilter(s)}
                      className={`px-3 py-1.5 text-xs font-medium ${
                        statusFilter === s
                          ? 'bg-info text-white'
                          : 'bg-base-100/50 text-base-content/80 hover:bg-info/10 dark:hover:bg-info/30'
                      }`}
                    >
                      {s === 'all' ? t('employees.allTypesFilter') : s === 'active' ? t('employees.activeFilter') : t('employees.inactiveFilter')}
                    </button>
                  ))}
                </div>
                {/* Grid / List view toggle */}
                <div className="flex rounded-lg overflow-hidden border border-slate-300 dark:border-gray-600">
                  <button
                    onClick={() => setViewMode('grid')}
                    title={t('employees.gridView') || 'Grid view'}
                    className={`px-3 py-1.5 text-xs font-medium ${
                      viewMode === 'grid'
                        ? 'bg-info text-white'
                        : 'bg-base-100/50 text-base-content/80 hover:bg-info/10 dark:hover:bg-info/30'
                    }`}
                  >
                    <span className="ri-layout-grid-line ri-14px" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    title={t('employees.listView') || 'List view'}
                    className={`px-3 py-1.5 text-xs font-medium ${
                      viewMode === 'list'
                        ? 'bg-info text-white'
                        : 'bg-base-100/50 text-base-content/80 hover:bg-info/10 dark:hover:bg-info/30'
                    }`}
                  >
                    <span className="ri-file-list-3-line ri-14px" />
                  </button>
                </div>
              </div>
              <button
                onClick={openAddEmployee}
                className="flex items-center gap-2 px-4 py-2 bg-info text-white rounded-xl font-semibold text-sm active:scale-[0.98] transition-all"
              >
                <span className="ri-add-line" /> {t('employees.addEmployee')}
              </button>
            </div>

            {viewMode === 'list' ? (
              /* ── Employee List (table) view ── */
              <div className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs uppercase tracking-wider text-base-content/50">
                      <th className="px-4 py-3 font-medium">{t('employees.name') || 'Name'}</th>
                      <th className="px-4 py-3 font-medium">{t('employees.type') || 'Type'}</th>
                      <th className="px-4 py-3 font-medium">{t('employees.phone')}</th>
                      <th className="px-4 py-3 font-medium">{t('employees.email')}</th>
                      <th className="px-4 py-3 font-medium text-right">{t('employees.salary')}</th>
                      <th className="px-4 py-3 font-medium">{t('employees.status') || 'Status'}</th>
                      <th className="px-4 py-3 font-medium text-right">{t('common.actions') || 'Actions'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredEmployees.map(emp => (
                      <tr
                        key={emp.id}
                        className={`border-b border-slate-100 dark:border-white/5 hover:bg-info/5 transition-colors ${!emp.is_active ? 'opacity-60' : ''}`}
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0
                              ${getTypeColor(getTypeName(emp.employee_type_id))}`}>
                              {emp.name.charAt(0).toUpperCase()}
                            </div>
                            <span className="font-medium text-base-content">{emp.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-base-content/70">{getTypeName(emp.employee_type_id)}</td>
                        <td className="px-4 py-3 text-base-content/70">{emp.phone || '-'}</td>
                        <td className="px-4 py-3 text-base-content/70">{emp.email || '-'}</td>
                        <td className="px-4 py-3 text-right tabular-nums text-base-content">{emp.salary.toLocaleString()}</td>
                        <td className="px-4 py-3">
                          {emp.is_active ? (
                            <Badge className="border-success/30 bg-success/15 text-success">
                              {t('common.active')}
                            </Badge>
                          ) : (
                            <Badge className="border-error/30 bg-error/15 text-error">
                              {t('common.inactive')}
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex justify-end gap-1">
                            <button onClick={() => openEditEmployee(emp)}
                              className="text-info hover:text-info/70 p-1.5 rounded-lg hover:bg-info/10" title={t('common.edit')}>
                              <span className="ri-pencil-line ri-16px" />
                            </button>
                            {emp.is_active ? (
                              <button onClick={() => setShowDeleteEmployee(emp)}
                                className="text-error hover:text-error/70 p-1.5 rounded-lg hover:bg-error/10" title={t('common.deactivate')}>
                                <span className="ri-delete-bin-line ri-16px" />
                              </button>
                            ) : (
                              <button onClick={() => handleReactivateEmployee(emp)}
                                className="text-success hover:text-success/70 p-1.5 rounded-lg hover:bg-success/10" title={t('employees.activate') || 'Activate'}>
                                <span className="ri-user-add-line ri-16px" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredEmployees.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-4 py-8 text-center text-base-content/60">
                          {t('employees.noEmployees')}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            ) : (
              /* ── Employee Grid (cards) view ── */
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
                {filteredEmployees.map(emp => (
                  <div
                    key={emp.id}
                    className={`bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 border border-slate-200 dark:border-white/5
                      ${!emp.is_active ? 'opacity-60' : 'hover:border-info/70 dark:hover:border-info/30'} transition-all`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold
                          ${getTypeColor(getTypeName(emp.employee_type_id))}`}>
                          {emp.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h3 className="font-semibold text-base-content">{emp.name}</h3>
                          <span className="text-xs text-base-content/50">{getTypeName(emp.employee_type_id)}</span>
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => openEditEmployee(emp)}
                          className="text-info hover:text-info/70 p-1.5 rounded-lg hover:bg-info/10" title={t('common.edit')}>
                          <span className="ri-pencil-line ri-16px" />
                        </button>
                        {emp.is_active ? (
                          <button onClick={() => setShowDeleteEmployee(emp)}
                            className="text-error hover:text-error/70 p-1.5 rounded-lg hover:bg-error/10" title={t('common.deactivate')}>
                            <span className="ri-delete-bin-line ri-16px" />
                          </button>
                        ) : (
                          <button onClick={() => handleReactivateEmployee(emp)}
                            className="text-success hover:text-success/70 p-1.5 rounded-lg hover:bg-success/10" title={t('employees.activate') || 'Activate'}>
                            <span className="ri-user-add-line ri-16px" />
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="space-y-1.5 text-sm">
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="ri-money-dollar-box-line text-success w-3.5 h-3.5" />
                        <span>{t('employees.salary')}: <strong className="text-base-content">{emp.salary.toLocaleString()}</strong></span>
                        <span className="ml-auto px-2 py-0.5 rounded-full bg-base-300/50 text-[10px] font-semibold uppercase tracking-wide">
                          {emp.pay_frequency === 'hourly' ? (t('employees.payFrequencyHourly') || 'Hourly') : (t('employees.payFrequencyMonthly') || 'Monthly')}
                        </span>
                      </div>
                      {emp.phone && (
                        <div className="flex items-center gap-2 text-base-content/60">
                          <span className="ri-phone-line text-info/70 w-3.5 h-3.5" />
                          <span>{emp.phone}</span>
                        </div>
                      )}
                      {emp.email && (
                        <div className="flex items-center gap-2 text-base-content/60">
                          <span className="ri-mail-line text-secondary/80 w-3.5 h-3.5" />
                          <span className="truncate">{emp.email}</span>
                        </div>
                      )}
                      {emp.joined_at && (
                        <div className="flex items-center gap-2 text-base-content/60">
                          <span className="ri-calendar-line text-info/80 w-3.5 h-3.5" />
                          <span>{t('employees.joined')} {emp.joined_at}</span>
                        </div>
                      )}
                      {emp.address && (
                        <div className="flex items-center gap-2 text-base-content/60">
                          <span className="ri-map-pin-line text-secondary/70 w-3.5 h-3.5" />
                          <span className="truncate">{emp.address}</span>
                        </div>
                      )}
                      {emp.bank_name && (
                        <div className="flex items-center gap-2 text-base-content/60">
                          <span className="ri-landmark-line text-primary/70 w-3.5 h-3.5" />
                          <span className="truncate">{emp.bank_name}{emp.bank_account ? ` · ${emp.bank_account}` : ''}</span>
                        </div>
                      )}
                    </div>

                    {!emp.is_active && (
                      <div className="mt-2 px-2 py-1 bg-error/20 rounded-lg text-xs text-error font-medium text-center">
                        {t('employees.inactive')}
                      </div>
                    )}
                  </div>
                ))}
                {filteredEmployees.length === 0 && (
                  <div className="col-span-full bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-8 text-center text-base-content/60">
                    {t('employees.noEmployees')}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── TAB 2: EMPLOYEE TYPES ── */}
        {activeTab === 'types' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-base-content">{t('employees.employeeTypes')}</h2>
              <button
                onClick={openAddType}
                className="flex items-center gap-2 px-4 py-2 bg-info text-white rounded-xl font-semibold text-sm active:scale-[0.98] transition-all"
              >
                <span className="ri-add-line" /> {t('employees.addType')}
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
              {employeeTypes.map(et => {
                const count = employees.filter(e => e.employee_type_id === et.id).length;
                return (
                  <div
                    key={et.id}
                    className={`bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 border border-slate-200 dark:border-white/5
                      ${!et.is_active ? 'opacity-60' : 'hover:border-info/70 dark:hover:border-info/30'} transition-all`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg
                          ${getTypeColor(et.name)}`}>
                          <span className="ri-briefcase-4-line" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-base-content">{et.name}</h3>
                          {et.description && (
                            <p className="text-xs text-base-content/50 mt-0.5">{et.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => openEditType(et)}
                          className="text-info hover:text-info/70 p-1.5 rounded-lg hover:bg-info/10" title={t('common.edit')}>
                          <span className="ri-pencil-line ri-16px" />
                        </button>
                        {et.is_active && (
                          <button onClick={() => setShowDeleteType(et)}
                            className="text-error hover:text-error/70 p-1.5 rounded-lg hover:bg-error/10" title={t('common.deactivate')}>
                            <span className="ri-delete-bin-line ri-16px" />
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="mt-3 flex items-center gap-2">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium
                        ${count > 0 ? 'bg-info/10 dark:bg-info/20 text-info dark:text-info/80' : 'bg-slate-100 dark:bg-slate-700/30 text-base-content/50'}`}>
                        {t('employees.employeeCount', { count })}
                      </span>
                      {!et.is_active && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-error/10 text-error">
                          Inactive
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
              {employeeTypes.length === 0 && (
                <div className="col-span-full bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-8 text-center text-base-content/60">
                  {t('employees.noTypes')}
                </div>
              )}
            </div>
          </div>
        )}

      {/* Unified Add/Edit Employee wizard — 4-step form (personal → contact → role → salary & payroll) */}
      <EmployeeWizard
        isOpen={!!employeeModal}
        onClose={closeEmployeeModal}
        value={employeeForm}
        onChange={setEmployeeForm}
        employeeTypes={employeeTypes}
        includeInactiveTypes={employeeModal?.mode === 'edit'}
        isEditing={employeeModal?.mode === 'edit'}
        submitLabel={employeeModal?.mode === 'edit' ? t('common.update') : t('employees.addEmployee')}
        cancelLabel={t('common.cancel')}
        onSubmit={handleSaveEmployee}
        contentTestId="employee-form-modal"
      />

      <ConfirmDialog
        isOpen={!!showDeleteEmployee}
        onClose={() => setShowDeleteEmployee(null)}
        onConfirm={handleDeleteEmployee}
        title={t('employees.deactivateEmployeeTitle')}
        message="Are you sure you want to deactivate"
        itemName={showDeleteEmployee?.name || ''}
        description="They will no longer appear in active employee lists or be assignable to sales."
      />

      {/* Unified Add/Edit Employee Type modal — reusable FormModal + EmployeeTypeForm */}
      <FormModal
        isOpen={!!typeModal}
        onClose={closeTypeModal}
        title={typeModal?.mode === 'edit' ? t('employees.editTypeTitle') : t('employees.addTypeTitle')}
        size="sm"
        submitLabel={typeModal?.mode === 'edit' ? t('common.update') : t('employees.addType')}
        cancelLabel={t('common.cancel')}
        submitDisabled={!typeForm.name.trim()}
        onSubmit={handleSaveType}
        submitClassName="btn-info"
        contentTestId="employee-type-form-modal"
      >
        <EmployeeTypeForm value={typeForm} onChange={setTypeForm} />
      </FormModal>

      <ConfirmDialog
        isOpen={!!showDeleteType}
        onClose={() => setShowDeleteType(null)}
        onConfirm={handleDeleteType}
        title={t('employees.deactivateTypeTitle')}
        message="Are you sure you want to deactivate"
        itemName={showDeleteType?.name || ''}
        description="Employees with this type will need to be reassigned to a different type."
      />

      <StatusToast type={toast?.type || 'success'} message={toast?.message || ''} visible={!!toast} onDismiss={() => setToast(null)} />
    </PageLayout>
  );
}
