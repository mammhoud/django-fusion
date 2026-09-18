import { useState, useEffect, useCallback, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Employee, NewEmployee, EmployeeType, NewEmployeeType } from '../../../types';
import PageLayout from '../../../components/layout/PageLayout';
import { SkeletonList } from '../../../components/ui/Skeleton';
import { useTranslation } from 'react-i18next';
import FormModal from '../../../components/ui/FormModal';
import { Badge } from '@/components/ui/badge';
import EmployeeWizard from '../../../components/forms/EmployeeWizard';
import EmployeeDetail from '../../../components/forms/EmployeeDetail';
import EmployeeTypeForm from '../../../components/forms/EmployeeTypeForm';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';
import StatusToast from '../../../components/ui/StatusToast';
import { useStatusToast } from '../../../hooks/useStatusToast';
import { useStaggeredReveal } from '../../../hooks/useStaggeredReveal';
import Card from '../../../components/ui/Card';

type Tab = 'employees' | 'types';

const EMPLOYEE_TYPE_COLORS: Record<string, string> = {
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

  // Unified add/edit modal state
  type EmployeeModalState = { mode: 'add' } | { mode: 'edit'; employee: Employee } | null;
  const [employeeModal, setEmployeeModal] = useState<EmployeeModalState>(null);
  const [employeeForm, setEmployeeForm] = useState<NewEmployee>({ ...initialNewEmployee });
  const [showDeleteEmployee, setShowDeleteEmployee] = useState<Employee | null>(null);
  const [detailEmployee, setDetailEmployee] = useState<Employee | null>(null);

  type TypeModalState = { mode: 'add' } | { mode: 'edit'; type: EmployeeType } | null;
  const [typeModal, setTypeModal] = useState<TypeModalState>(null);
  const [typeForm, setTypeForm] = useState<NewEmployeeType>({ name: '', description: null });
  const [showDeleteType, setShowDeleteType] = useState<EmployeeType | null>(null);

  const { status, showSuccess, showError, dismiss } = useStatusToast();

  // Staggered reveal hook
  const { containerRef: employeeContainerRef, getItemProps: getEmployeeItemProps } = useStaggeredReveal({
    count: 20,
    staggerDelay: 75,
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
  });

  const { containerRef: typeContainerRef, getItemProps: getTypeItemProps } = useStaggeredReveal({
    count: 20,
    staggerDelay: 75,
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
  });

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
      showError(`Error loading employee data: ${error}`);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  }, [showError]);

  useEffect(() => { loadData(); }, [loadData]);

  // Real-time employee updates from other windows
  useEffect(() => {
    const unlisten = listen('employees-updated', () => {
      loadData({ quiet: true });
    });
    return () => { unlisten.then(fn => fn()); };
  }, [loadData]);

  const getTypeName = (typeId: number) => {
    return employeeTypes.find(t => t.id === typeId)?.name || `Type #${typeId}`;
  };

  // Filtered employees
  const filteredEmployees = useMemo(() => {
    const q = searchQuery.toLowerCase();
    return employees.filter(emp => {
      if (statusFilter === 'active' && !emp.is_active) return false;
      if (statusFilter === 'inactive' && emp.is_active) return false;
      if (typeFilter && emp.employee_type_id !== typeFilter) return false;
      if (q) {
        if (!emp.name.toLowerCase().includes(q) &&
            !(emp.phone || '').includes(q) &&
            !(emp.email || '').toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [employees, statusFilter, typeFilter, searchQuery]);

  // Employee CRUD
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
      salary: emp.salary ?? 0,
      joined_at: emp.joined_at ?? null,
      address: emp.address ?? null,
      date_of_birth: emp.date_of_birth ?? null,
      national_id: emp.national_id ?? null,
      emergency_contact: emp.emergency_contact ?? null,
      pay_frequency: emp.pay_frequency ?? 'monthly',
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
        showSuccess(t('employees.successUpdated') || 'Employee updated!');
      } else {
        await invoke('add_employee', { employee: payload });
        window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'add' } }));
        showSuccess(t('employees.successAdded') || 'Employee added successfully!');
      }
      closeEmployeeModal();
      loadData({ quiet: true });
    } catch (e) { showError(String(e)); }
  };

  const handleReactivateEmployee = async (emp: Employee) => {
    try {
      await invoke('update_employee', {
        id: emp.id,
        update: { is_active: true },
      });
      window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'reactivate', id: emp.id } }));
      loadData({ quiet: true });
      showSuccess(t('employees.successReactivated') || 'Employee activated.');
    } catch (e) { showError(String(e)); }
  };

  const handleDeleteEmployee = async () => {
    if (!showDeleteEmployee) return;
    try {
      await invoke('soft_delete_employee', { id: showDeleteEmployee.id });
      window.dispatchEvent(new CustomEvent('employee-updated', { detail: { action: 'delete', id: showDeleteEmployee.id } }));
      setShowDeleteEmployee(null);
      loadData({ quiet: true });
      showSuccess('Employee deactivated.');
    } catch (e) { showError(String(e)); }
  };

  // Employee Type CRUD
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
        showSuccess('Employee type updated!');
      } else {
        await invoke('add_employee_type', { employeeType: typeForm });
        showSuccess('Employee type added!');
      }
      closeTypeModal();
      loadData({ quiet: true });
    } catch (e) { showError(String(e)); }
  };

  const handleDeleteType = async () => {
    if (!showDeleteType) return;
    try {
      await invoke('soft_delete_employee_type', { id: showDeleteType.id });
      setShowDeleteType(null);
      loadData({ quiet: true });
      showSuccess('Employee type deactivated.');
    } catch (e) { showError(String(e)); }
  };

  // Loading State
  if (isLoading) {
    return (
      <PageLayout title={t('employees.title')}>
        <div className="space-y-6">
          <SkeletonList items={6} />
        </div>
      </PageLayout>
    );
  }

  // Summary counts and payroll indicators
  const activeEmployees = employees.filter(e => e.is_active).length;
  const activeTypes = employeeTypes.filter(t => t.is_active).length;
  const monthlyPayroll = employees
    .filter(e => e.is_active)
    .reduce((total, employee) => total + (
      employee.pay_frequency === 'hourly'
        ? (employee.hourly_rate ?? 0) * 160
        : employee.salary
    ), 0);
  const averagePayroll = activeEmployees > 0 ? monthlyPayroll / activeEmployees : 0;

  return (
    <PageLayout title={t('nav.employees', 'Employees')}>
      <div className="space-y-4">
        {/* ── Eyebrow tag — premium micro-label ── */}
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-info/10 text-info">
            <span className="ri-group-line ri-12px" />
            {t('employees.teamLabel', 'Team Management')}
          </span>
        </div>

        {/* ── Summary cards — Double-Bezel compact ── */}
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
          <Card padding="sm" variant="bezel">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-info/10 flex items-center justify-center text-info">
                <span className="ri-group-line ri-18px" />
              </div>
              <div>
                <p className="text-[11px] text-base-content/50 uppercase tracking-wide font-medium">
                  {t('employees.totalEmployees')}
                </p>
                <p className="text-2xl font-bold text-base-content tabular-nums">{activeEmployees}</p>
              </div>
            </div>
          </Card>
          <Card padding="sm" variant="bezel">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary/10 flex items-center justify-center text-secondary">
                <span className="ri-briefcase-4-line ri-18px" />
              </div>
              <div>
                <p className="text-[11px] text-base-content/50 uppercase tracking-wide font-medium">
                  {t('employees.employeeTypes')}
                </p>
                <p className="text-2xl font-bold text-secondary tabular-nums">{activeTypes}</p>
              </div>
            </div>
          </Card>
          <Card padding="sm" variant="bezel">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center text-success">
                <span className="ri-wallet-3-line ri-18px" />
              </div>
              <div>
                <p className="text-[11px] text-base-content/50 uppercase tracking-wide font-medium">
                  {t('employees.monthlySalary')}
                </p>
                <p className="text-xl font-bold text-success tabular-nums">{monthlyPayroll.toLocaleString()}</p>
              </div>
            </div>
          </Card>
          <Card padding="sm" variant="bezel">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-warning/10 flex items-center justify-center text-warning">
                <span className="ri-bar-chart-2-line ri-18px" />
              </div>
              <div>
                <p className="text-[11px] text-base-content/50 uppercase tracking-wide font-medium">
                  {t('employees.avgSalary')}
                </p>
                <p className="text-xl font-bold text-warning tabular-nums">{Math.round(averagePayroll).toLocaleString()}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* ── Tabs — compact pill style ── */}
        <div className="flex gap-1.5 overflow-x-auto">
          {getTabItems().map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl font-semibold text-xs transition-all duration-200 active:scale-[0.98] shrink-0 ${
                activeTab === tab.key
                  ? 'bg-info text-info-content shadow-lg'
                  : 'bg-base-100/70 text-base-content/70 hover:bg-info/10'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* ── TAB 1: EMPLOYEE LIST ── */}
        {activeTab === 'employees' && (
          <div className="space-y-3">
            {/* ── Title + search + filters — compact toolbar ── */}
            <div className="flex flex-wrap items-center gap-2">
              <div className="relative flex-1 max-w-48">
                <span className="ri-search-line absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-base-content/50" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder={t('employees.searchPlaceholder')}
                  className="input w-full h-8 text-xs pl-8"
                />
              </div>
              <select
                value={typeFilter ?? ''}
                onChange={e => setTypeFilter(e.target.value ? Number(e.target.value) : null)}
                className="select h-8 text-xs"
              >
                <option value="">{t('employees.allTypes')}</option>
                {employeeTypes.filter(t => t.is_active).map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
              <div className="flex rounded-lg overflow-hidden border border-base-300/50">
                {(['all', 'active', 'inactive'] as const).map(s => (
                  <button
                    key={s}
                    onClick={() => setStatusFilter(s)}
                    className={`px-2.5 py-1 text-[10px] font-medium transition-colors ${
                      statusFilter === s
                        ? 'bg-info text-info-content'
                        : 'text-base-content/60 hover:bg-info/10'
                    }`}
                  >
                    {s === 'all' ? t('employees.allTypesFilter') : s === 'active' ? t('employees.activeFilter') : t('employees.inactiveFilter')}
                  </button>
                ))}
              </div>
              <span className="text-[10px] text-base-content/40 whitespace-nowrap shrink-0">
                {filteredEmployees.length}/{employees.length}
              </span>
              <button
                onClick={openAddEmployee}
                className="btn btn-primary btn-sm gap-1 shrink-0 active:scale-[0.98] transition-transform"
              >
                <span className="ri-add-line ri-14px" />
                <span className="text-xs">{t('employees.addEmployee')}</span>
              </button>
            </div>

            {/* ── Employee Grid — Double-Bezel compact cards with staggered reveal ── */}
            <div ref={employeeContainerRef} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {filteredEmployees.map((emp, idx) => (
                <Card
                  key={emp.id}
                  padding="sm"
                  variant="bezel"
                  hover
                  {...getEmployeeItemProps(idx)}
                >
                  {/* ── Header zone — avatar + name + actions ── */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0
                        ${getTypeColor(getTypeName(emp.employee_type_id))}`}>
                        {emp.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <h3 className="font-semibold text-sm text-base-content truncate">{emp.name}</h3>
                        <span className="text-[10px] text-base-content/50">{getTypeName(emp.employee_type_id)}</span>
                      </div>
                    </div>
                    <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <button onClick={() => setDetailEmployee(emp)}
                        className="w-7 h-7 rounded-lg text-base-content/40 hover:text-secondary hover:bg-secondary/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                        title={t('employees.viewDetail') || 'View details'}>
                        <span className="ri-profile-line ri-14px" />
                      </button>
                      <button onClick={() => openEditEmployee(emp)}
                        className="w-7 h-7 rounded-lg text-base-content/40 hover:text-info hover:bg-info/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                        title={t('common.edit')}>
                        <span className="ri-pencil-line ri-14px" />
                      </button>
                      {emp.is_active ? (
                        <button onClick={() => setShowDeleteEmployee(emp)}
                          className="w-7 h-7 rounded-lg text-base-content/40 hover:text-error hover:bg-error/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                          title={t('common.deactivate')}>
                          <span className="ri-delete-bin-line ri-14px" />
                        </button>
                      ) : (
                        <button onClick={() => handleReactivateEmployee(emp)}
                          className="w-7 h-7 rounded-lg text-base-content/40 hover:text-success hover:bg-success/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                          title={t('employees.activate') || 'Activate'}>
                          <span className="ri-user-add-line ri-14px" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* ── Content zone — contact info ── */}
                  <div className="mt-2.5 space-y-1 text-[11px]">
                    {emp.phone && (
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="ri-phone-line text-info/70 w-3 h-3" />
                        <span>{emp.phone}</span>
                      </div>
                    )}
                    {emp.email && (
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="ri-mail-line text-secondary/80 w-3 h-3" />
                        <span className="truncate">{emp.email}</span>
                      </div>
                    )}
                    {emp.joined_at && (
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="ri-calendar-line text-info/80 w-3 h-3" />
                        <span>{t('employees.joined')} {emp.joined_at}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-base-content/60">
                      <span className="ri-wallet-3-line text-success/80 w-3 h-3" />
                      <span>{t('employees.salary')}: <strong className="text-base-content">{(emp.pay_frequency === 'hourly' ? (emp.hourly_rate ?? 0) * 160 : emp.salary).toLocaleString()}</strong></span>
                    </div>
                  </div>

                  {/* ── Footer zone — status badge ── */}
                  <div className="mt-2.5 pt-2 border-t border-base-300/30 flex items-center justify-between text-[10px]">
                    {emp.address && (
                      <div className="flex items-center gap-1 text-base-content/40 truncate max-w-[60%]">
                        <span className="ri-map-pin-line text-secondary/70 w-3 h-3" />
                        <span className="truncate">{emp.address}</span>
                      </div>
                    )}
                    <Badge
                      variant={emp.is_active ? 'success' : 'neutral'}
                      size="sm"
                      className="ml-auto"
                    >
                      {emp.is_active ? t('common.active') : t('common.inactive')}
                    </Badge>
                  </div>
                </Card>
              ))}
              {filteredEmployees.length === 0 && (
                <div className="col-span-full text-center py-16">
                  <div className="w-14 h-14 mx-auto mb-3 rounded-full bg-info/10 flex items-center justify-center text-info">
                    <span className="ri-group-line ri-24px" />
                  </div>
                  <p className="text-base-content/60 text-sm">
                    {searchQuery
                      ? (t('common.noDataFound') || 'No matches found.')
                      : t('employees.noEmployees')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── TAB 2: EMPLOYEE TYPES ── */}
        {activeTab === 'types' && (
          <div className="space-y-3">
            {/* ── Title + search + add — compact toolbar ── */}
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-lg font-bold text-base-content shrink-0">
                {t('employees.employeeTypes')}
              </h1>
              <span className="text-[10px] text-base-content/40 whitespace-nowrap shrink-0">
                {employeeTypes.filter(t => t.is_active).length}/{employeeTypes.length}
              </span>
              <button
                onClick={openAddType}
                className="btn btn-primary btn-sm gap-1 shrink-0 active:scale-[0.98] transition-transform ml-auto"
              >
                <span className="ri-add-line ri-14px" />
                <span className="text-xs">{t('employees.addType')}</span>
              </button>
            </div>

            {/* ── Type Grid — Double-Bezel compact cards with staggered reveal ── */}
            <div ref={typeContainerRef} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {employeeTypes.map((et, idx) => {
                const count = employees.filter(e => e.employee_type_id === et.id).length;
                return (
                  <Card
                    key={et.id}
                    padding="sm"
                    variant="bezel"
                    hover
                    {...getTypeItemProps(idx)}
                  >
                    {/* ── Header zone — icon + name + actions ── */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg shrink-0
                          ${getTypeColor(et.name)}`}>
                          <span className="ri-briefcase-4-line" />
                        </div>
                        <div className="min-w-0">
                          <h3 className="font-semibold text-sm text-base-content truncate">{et.name}</h3>
                          {et.description && (
                            <p className="text-[10px] text-base-content/50 line-clamp-1">{et.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <button onClick={() => openEditType(et)}
                          className="w-7 h-7 rounded-lg text-base-content/40 hover:text-info hover:bg-info/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                          title={t('common.edit')}>
                          <span className="ri-pencil-line ri-14px" />
                        </button>
                        {et.is_active && (
                          <button onClick={() => setShowDeleteType(et)}
                            className="w-7 h-7 rounded-lg text-base-content/40 hover:text-error hover:bg-error/10 flex items-center justify-center transition-all duration-200 active:scale-95"
                            title={t('common.deactivate')}>
                            <span className="ri-delete-bin-line ri-14px" />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* ── Footer zone — employee count + status ── */}
                    <div className="mt-2.5 pt-2 border-t border-base-300/30 flex items-center justify-between text-[10px]">
                      <span className={`inline-flex items-center gap-1 ${
                        count > 0 ? 'text-info' : 'text-base-content/40'
                      }`}>
                        <span className="ri-team-line ri-12px" />
                        {t('employees.employeeCount', { count })}
                      </span>
                      {!et.is_active && (
                        <Badge variant="neutral" size="sm">
                          Inactive
                        </Badge>
                      )}
                    </div>
                  </Card>
                );
              })}
              {employeeTypes.length === 0 && (
                <div className="col-span-full text-center py-16">
                  <div className="w-14 h-14 mx-auto mb-3 rounded-full bg-secondary/10 flex items-center justify-center text-secondary">
                    <span className="ri-briefcase-4-line ri-24px" />
                  </div>
                  <p className="text-base-content/60 text-sm">
                    {t('employees.noTypes')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── Add/Edit Employee wizard ── */}
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

      {/* ── Employee detail ── */}
      <EmployeeDetail
        employee={detailEmployee}
        employeeTypes={employeeTypes}
        onClose={() => setDetailEmployee(null)}
      />

      {/* ── Delete employee confirm ── */}
      <ConfirmDialog
        isOpen={!!showDeleteEmployee}
        onClose={() => setShowDeleteEmployee(null)}
        onConfirm={handleDeleteEmployee}
        title={t('employees.deactivateEmployeeTitle')}
        message="Are you sure you want to deactivate"
        itemName={showDeleteEmployee?.name || ''}
        description="They will no longer appear in active employee lists or be assignable to sales."
      />

      {/* ── Add/Edit Employee Type modal ── */}
      <FormModal
        isOpen={!!typeModal}
        onClose={closeTypeModal}
        title={typeModal?.mode === 'edit' ? t('employees.editTypeTitle') : t('employees.addTypeTitle')}
        size="sm"
        submitLabel={typeModal?.mode === 'edit' ? t('common.update') : t('employees.addType')}
        cancelLabel={t('common.cancel')}
        submitDisabled={!typeForm.name.trim()}
        onSubmit={handleSaveType}
        contentTestId="employee-type-form-modal"
      >
        <EmployeeTypeForm value={typeForm} onChange={setTypeForm} />
      </FormModal>

      {/* ── Delete type confirm ── */}
      <ConfirmDialog
        isOpen={!!showDeleteType}
        onClose={() => setShowDeleteType(null)}
        onConfirm={handleDeleteType}
        title={t('employees.deactivateTypeTitle')}
        message="Are you sure you want to deactivate"
        itemName={showDeleteType?.name || ''}
        description="Employees with this type will need to be reassigned to a different type."
      />

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}
