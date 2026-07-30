import { motion } from 'framer-motion';
import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Employee, NewEmployee, EmployeeType, NewEmployeeType } from '../../types';
import PageLayout from '../../components/layout/PageLayout';
import { SkeletonList, SkeletonTable } from '../../components/layout/Skeleton';
import { useTranslation } from 'react-i18next';
import Modal from '../../components/layout/Modal';
import ConfirmDialog from '../../components/display/ConfirmDialog';
import StatusToast from '../../components/data/StatusToast';
import Card from '../../components/layout/Card';

type Tab = 'employees' | 'types';

const EMPLOYEE_TYPE_COLORS: Record<string, string> = {
  'Manager': 'bg-purple-500',
  'Chef': 'bg-orange-500',
  'Waiter': 'bg-blue-500',
  'Cashier': 'bg-emerald-500',
  'Driver': 'bg-yellow-500',
  'Cleaner': 'bg-slate-500',
  'Other': 'bg-gray-500',
};

const getTypeColor = (typeName: string) => {
  return EMPLOYEE_TYPE_COLORS[typeName] || 'bg-gray-500';
};

const initialNewEmployee: NewEmployee = {
  name: '',
  phone: null,
  email: null,
  employee_type_id: 0,
  salary: 0,
};

export default function Employees() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('employees');
  const [isLoading, setIsLoading] = useState(true);

  const getTabItems = () => [
    { key: 'employees' as Tab, label: t('employees.employeeList'), icon: <span className="icon-[tabler--users]" /> },
    { key: 'types' as Tab, label: t('employees.employeeTypes'), icon: <span className="icon-[tabler--user-check]" /> },
  ];

  // Data states
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [employeeTypes, setEmployeeTypes] = useState<EmployeeType[]>([]);

  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<number | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('active');

  // Modal states - Employee
  const [showAddEmployee, setShowAddEmployee] = useState(false);
  const [showEditEmployee, setShowEditEmployee] = useState<Employee | null>(null);
  const [showDeleteEmployee, setShowDeleteEmployee] = useState<Employee | null>(null);

  // Modal states - Employee Type
  const [showAddType, setShowAddType] = useState(false);
  const [showEditType, setShowEditType] = useState<EmployeeType | null>(null);
  const [showDeleteType, setShowDeleteType] = useState<EmployeeType | null>(null);

  // Form states - Employee
  const [newEmployee, setNewEmployee] = useState<NewEmployee>({ ...initialNewEmployee });
  const [editEmployee, setEditEmployee] = useState<Employee | null>(null);

  // Form states - Employee Type
  const [newType, setNewType] = useState<NewEmployeeType>({ name: '', description: null });
  const [editType, setEditType] = useState<EmployeeType | null>(null);

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

  // ── Employee CRUD ──
  const handleAddEmployee = async () => {
    if (!newEmployee.name.trim() || newEmployee.employee_type_id === 0) return;
    try {
      await invoke('add_employee', { employee: newEmployee });
      setShowAddEmployee(false);
      setNewEmployee({ ...initialNewEmployee });
      loadData({ quiet: true });
      showStatus('success', 'Employee added successfully!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleUpdateEmployee = async () => {
    if (!editEmployee || !editEmployee.name.trim()) return;
    try {
      await invoke('update_employee', {
        id: editEmployee.id,
        update: {
          name: editEmployee.name,
          phone: editEmployee.phone || null,
          email: editEmployee.email || null,
          employee_type_id: editEmployee.employee_type_id,
          salary: editEmployee.salary,
        }
      });
      setShowEditEmployee(null);
      setEditEmployee(null);
      loadData({ quiet: true });
      showStatus('success', 'Employee updated!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleDeleteEmployee = async () => {
    if (!showDeleteEmployee) return;
    try {
      await invoke('soft_delete_employee', { id: showDeleteEmployee.id });
      setShowDeleteEmployee(null);
      loadData({ quiet: true });
      showStatus('success', 'Employee deactivated.');
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Employee Type CRUD ──
  const handleAddType = async () => {
    if (!newType.name.trim()) return;
    try {
      await invoke('add_employee_type', { employeeType: newType });
      setShowAddType(false);
      setNewType({ name: '', description: null });
      loadData({ quiet: true });
      showStatus('success', 'Employee type added!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleUpdateType = async () => {
    if (!editType || !editType.name.trim()) return;
    try {
      await invoke('update_employee_type', {
        id: editType.id,
        update: {
          name: editType.name,
          description: editType.description || null,
        }
      });
      setShowEditType(null);
      setEditType(null);
      loadData({ quiet: true });
      showStatus('success', 'Employee type updated!');
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
      title={<><span className="icon-[tabler--users] text-info" /> Employees</>}
      background="bg-linear-to-br from-slate-100 via-info/10 to-slate-100 dark:from-slate-900 dark:via-info/10 dark:to-slate-900"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <Card>
            <h2 className="text-base-content/60 text-sm">{t('employees.totalEmployees')}</h2>
            <p className="text-2xl font-bold text-base-content">{employees.filter(e => e.is_active).length}</p>
          </Card>
          <Card>
            <h2 className="text-base-content/60 text-sm">{t('employees.employeeTypes')}</h2>
            <p className="text-2xl font-bold text-info">{employeeTypes.filter(t => t.is_active).length}</p>
          </Card>
          <Card>
            <h2 className="text-base-content/60 text-sm">{t('employees.monthlySalary')}</h2>
            <p className="text-2xl font-bold text-success">{monthlySalaryTotal.toLocaleString()}</p>
          </Card>
          <Card>
            <h2 className="text-base-content/60 text-sm">{t('employees.avgSalary')}</h2>
            <p className="text-2xl font-bold text-blue-500">
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
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {/* Filters & Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 text-base-content/50" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder={t('employees.searchPlaceholder')}
                    className="input input-bordered w-48 pl-9"
                  />
                </div>
                <select
                  value={typeFilter ?? ''}
                  onChange={e => setTypeFilter(e.target.value ? Number(e.target.value) : null)}
                  className="select select-bordered"
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
              </div>
              <button
                onClick={() => setShowAddEmployee(true)}
                className="flex items-center gap-2 px-4 py-2 bg-info text-white rounded-xl font-semibold text-sm active:scale-[0.98] transition-all"
              >
                <span className="icon-[tabler--plus]" /> {t('employees.addEmployee')}
              </button>
            </div>

            {/* Employee Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
              {filteredEmployees.map(emp => (
                <motion.div
                  key={emp.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 border border-slate-200 dark:border-white/5
                    ${!emp.is_active ? 'opacity-60' : 'hover:border-info/70 dark:hover:border-info/30'} transition-all`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold
                        ${getTypeColor(getTypeName(emp.employee_type_id))}`}>
                        {emp.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="font-semibold text-base-content">{emp.name}</h3>
                        <span className="text-xs text-base-content/50">{getTypeName(emp.employee_type_id)}</span>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => { setShowEditEmployee(emp); setEditEmployee({ ...emp }); }}
                        className="text-blue-500 hover:text-blue-400 p-1.5 rounded-lg hover:bg-blue-500/10" title={t('common.edit')}>
                        <span className="icon-[tabler--pencil] w-4 h-4" />
                      </button>
                      {emp.is_active && (
                        <button onClick={() => setShowDeleteEmployee(emp)}
                          className="text-red-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10" title={t('common.deactivate')}>
                          <span className="icon-[tabler--trash] w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="space-y-1.5 text-sm">
                    <div className="flex items-center gap-2 text-base-content/60">
                      <span className="icon-[tabler--moneybag] text-success w-3.5 h-3.5" />
                      <span>{t('employees.salary')}: <strong className="text-base-content">{emp.salary.toLocaleString()}</strong></span>
                    </div>
                    {emp.phone && (
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="icon-[tabler--phone] text-blue-400 w-3.5 h-3.5" />
                        <span>{emp.phone}</span>
                      </div>
                    )}
                    {emp.email && (
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="icon-[tabler--mail] text-secondary/80 w-3.5 h-3.5" />
                        <span className="truncate">{emp.email}</span>
                      </div>
                    )}
                    {emp.joined_at && (
                      <div className="flex items-center gap-2 text-base-content/60">
                        <span className="icon-[tabler--calendar] text-info/80 w-3.5 h-3.5" />
                        <span>{t('employees.joined')} {emp.joined_at}</span>
                      </div>
                    )}
                  </div>

                  {!emp.is_active && (
                    <div className="mt-2 px-2 py-1 bg-red-100 dark:bg-red-900/20 rounded-lg text-xs text-red-500 font-medium text-center">
                      {t('employees.inactive')}
                    </div>
                  )}
                </motion.div>
              ))}
              {filteredEmployees.length === 0 && (
                <div className="col-span-full bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-8 text-center text-base-content/60">
                  {t('employees.noEmployees')}
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* ── TAB 2: EMPLOYEE TYPES ── */}
        {activeTab === 'types' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-base-content">{t('employees.employeeTypes')}</h2>
              <button
                onClick={() => setShowAddType(true)}
                className="flex items-center gap-2 px-4 py-2 bg-info text-white rounded-xl font-semibold text-sm active:scale-[0.98] transition-all"
              >
                <span className="icon-[tabler--plus]" /> {t('employees.addType')}
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
              {employeeTypes.map(et => {
                const count = employees.filter(e => e.employee_type_id === et.id).length;
                return (
                  <motion.div
                    key={et.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className={`bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 border border-slate-200 dark:border-white/5
                      ${!et.is_active ? 'opacity-60' : 'hover:border-info/70 dark:hover:border-info/30'} transition-all`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-lg
                          ${getTypeColor(et.name)}`}>
                          <span className="icon-[tabler--briefcase]" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-base-content">{et.name}</h3>
                          {et.description && (
                            <p className="text-xs text-base-content/50 mt-0.5">{et.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => { setShowEditType(et); setEditType({ ...et }); }}
                          className="text-blue-500 hover:text-blue-400 p-1.5 rounded-lg hover:bg-blue-500/10" title={t('common.edit')}>
                          <span className="icon-[tabler--pencil] w-4 h-4" />
                        </button>
                        {et.is_active && (
                          <button onClick={() => setShowDeleteType(et)}
                            className="text-red-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10" title={t('common.deactivate')}>
                            <span className="icon-[tabler--trash] w-4 h-4" />
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
                        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/20 text-red-500">
                          Inactive
                        </span>
                      )}
                    </div>
                  </motion.div>
                );
              })}
              {employeeTypes.length === 0 && (
                <div className="col-span-full bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-8 text-center text-base-content/60">
                  {t('employees.noTypes')}
                </div>
              )}
            </div>
          </motion.div>
        )}

      <Modal
        isOpen={showAddEmployee}
        onClose={() => setShowAddEmployee(false)}
        title={t('employees.addEmployeeTitle')}
        footer={<>
          <button onClick={() => setShowAddEmployee(false)} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleAddEmployee} disabled={!newEmployee.name.trim() || newEmployee.employee_type_id === 0}
            className="flex-1 py-2.5 rounded-lg bg-info text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <span className="icon-[tabler--device-floppy]" /> {t('employees.addEmployee')}
          </button>
        </>}
      >
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">{t('employees.fullName')} *</label>
          <input type="text" value={newEmployee.name} onChange={e => setNewEmployee(p => ({ ...p, name: e.target.value }))}
            placeholder={t('employees.namePlaceholder') || 'Enter employee name'}
            className="input input-bordered w-full" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.phone')}</label>
            <input type="tel" value={newEmployee.phone || ''} onChange={e => setNewEmployee(p => ({ ...p, phone: e.target.value || null }))}
              placeholder="03XX-XXXXXXX"
              className="input input-bordered w-full" />
          </div>
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.email')}</label>
            <input type="email" value={newEmployee.email || ''} onChange={e => setNewEmployee(p => ({ ...p, email: e.target.value || null }))}
              placeholder={t('employees.email')}
              className="input input-bordered w-full" />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.employeeType')} *</label>
            <select value={newEmployee.employee_type_id} onChange={e => setNewEmployee(p => ({ ...p, employee_type_id: Number(e.target.value) }))}
              className="select select-bordered w-full">
              <option value={0}>{t('employees.selectType')}</option>
              {employeeTypes.filter(t => t.is_active).map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.monthlySalary')} *</label>
            <input type="number" step="1000" min="0" value={newEmployee.salary} onChange={e => setNewEmployee(p => ({ ...p, salary: Number(e.target.value) }))}
              placeholder="0"
              className="input input-bordered w-full" />
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditEmployee && !!editEmployee}
        onClose={() => { setShowEditEmployee(null); setEditEmployee(null); }}
        title={t('employees.editEmployeeTitle')}
        footer={<>
          <button onClick={() => { setShowEditEmployee(null); setEditEmployee(null); }} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleUpdateEmployee} className="flex-1 py-2.5 rounded-lg bg-blue-500 text-white font-semibold flex items-center justify-center gap-2"><span className="icon-[tabler--device-floppy]" /> {t('common.update')}</button>
        </>}
      >
        {editEmployee && (<>
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.fullName')}</label>
            <input type="text" value={editEmployee.name} onChange={e => setEditEmployee(p => ({ ...p!, name: e.target.value }))}
              className="input input-bordered w-full" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-base-content/80 mb-1 text-sm">{t('employees.phone')}</label>
              <input type="tel" value={editEmployee.phone || ''} onChange={e => setEditEmployee(p => ({ ...p!, phone: e.target.value || undefined }))}
                className="input input-bordered w-full" />
            </div>
            <div>
              <label className="block text-base-content/80 mb-1 text-sm">{t('employees.email')}</label>
              <input type="email" value={editEmployee.email || ''} onChange={e => setEditEmployee(p => ({ ...p!, email: e.target.value || undefined }))}
                className="input input-bordered w-full" />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-base-content/80 mb-1 text-sm">{t('employees.employeeType')}</label>
              <select value={editEmployee.employee_type_id} onChange={e => setEditEmployee(p => ({ ...p!, employee_type_id: Number(e.target.value) }))}
                className="select select-bordered w-full">
                {employeeTypes.filter(t => t.is_active || t.id === editEmployee.employee_type_id).map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-base-content/80 mb-1 text-sm">{t('employees.monthlySalary')}</label>
              <input type="number" step="1000" value={editEmployee.salary} onChange={e => setEditEmployee(p => ({ ...p!, salary: Number(e.target.value) }))}
                className="input input-bordered w-full" />
            </div>
          </div>
        </>)}
      </Modal>

      <ConfirmDialog
        isOpen={!!showDeleteEmployee}
        onClose={() => setShowDeleteEmployee(null)}
        onConfirm={handleDeleteEmployee}
        title={t('employees.deactivateEmployeeTitle')}
        message="Are you sure you want to deactivate"
        itemName={showDeleteEmployee?.name || ''}
        description="They will no longer appear in active employee lists or be assignable to sales."
      />

      <Modal
        isOpen={showAddType}
        onClose={() => setShowAddType(false)}
        title={t('employees.addTypeTitle')}
        size="sm"
        footer={<>
          <button onClick={() => setShowAddType(false)} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleAddType} disabled={!newType.name.trim()}
            className="flex-1 py-2.5 rounded-lg bg-info text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <span className="icon-[tabler--device-floppy]" /> {t('employees.addType')}
          </button>
        </>}
      >
        <div>            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.typeName')} *</label>
          <input type="text" value={newType.name} onChange={e => setNewType(p => ({ ...p, name: e.target.value }))}
            placeholder={t('employees.typeNamePlaceholder')}
            className="input input-bordered w-full" />
        </div>
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">{t('employees.descriptionOptional')}</label>
          <textarea value={newType.description || ''} onChange={e => setNewType(p => ({ ...p, description: e.target.value || null }))}
            placeholder={t('employees.descPlaceholder')}
            rows={3}
            className="textarea textarea-bordered w-full resize-none" />
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditType && !!editType}
        onClose={() => { setShowEditType(null); setEditType(null); }}
        title={t('employees.editTypeTitle')}
        size="sm"
        footer={<>
          <button onClick={() => { setShowEditType(null); setEditType(null); }} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleUpdateType} className="flex-1 py-2.5 rounded-lg bg-blue-500 text-white font-semibold flex items-center justify-center gap-2"><span className="icon-[tabler--device-floppy]" /> {t('common.update')}</button>
        </>}
      >
        {editType && (<>
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.typeName')}</label>
            <input type="text" value={editType.name} onChange={e => setEditType(p => ({ ...p!, name: e.target.value }))}
              className="input input-bordered w-full" />
          </div>
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('employees.typeDescription')}</label>
            <textarea value={editType.description || ''}onChange={e => setEditType(p => ({ ...p!, description: e.target.value || undefined }))}
              rows={3}
              className="textarea textarea-bordered w-full resize-none" />
          </div>
        </>)}
      </Modal>

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
