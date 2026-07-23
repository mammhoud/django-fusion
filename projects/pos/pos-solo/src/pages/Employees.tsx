import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { MdPeople, MdEdit, MdDelete, MdWork } from 'react-icons/md';
import { FaUsers, FaUserTag, FaMoneyBillWave, FaPlus, FaSave, FaSearch, FaPhone, FaEnvelope, FaCalendarAlt } from 'react-icons/fa';
import { useGetEmployeesQuery } from '../store/api/endpoints/core';
import {
  useAddEmployeeMutation,
  useUpdateEmployeeMutation,
  useSoftDeleteEmployeeMutation,
  useGetEmployeeTypesQuery,
  useAddEmployeeTypeMutation,
  useUpdateEmployeeTypeMutation,
  useSoftDeleteEmployeeTypeMutation,
} from '../store/api/endpoints/legacy';
import { Employee, NewEmployee, EmployeeType, NewEmployeeType } from '../types';
import PageLayout from '../components/PageLayout';
import { SkeletonList, SkeletonTable } from '../components/Skeleton';
import { useTranslation } from 'react-i18next';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import StatusToast from '../components/StatusToast';

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
    { key: 'employees' as Tab, label: t('employees.employeeList'), icon: <FaUsers /> },
    { key: 'types' as Tab, label: t('employees.employeeTypes'), icon: <FaUserTag /> },
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

  // ── RTK Query data fetching ──
  const { data: employeesData, isLoading: empsLoading } = useGetEmployeesQuery();
  const { data: employeeTypesData, isLoading: typesLoading } = useGetEmployeeTypesQuery({ includeInactive: true });

  useEffect(() => {
    if (!empsLoading && !typesLoading) {
      setEmployees((Array.isArray(employeesData) ? employeesData : []) as Employee[]);
      setEmployeeTypes((Array.isArray(employeeTypesData) ? employeeTypesData : []) as EmployeeType[]);
      setIsLoading(false);
    }
  }, [employeesData, employeeTypesData, empsLoading, typesLoading]);

  // ── Mutations ──
  const [addEmployee] = useAddEmployeeMutation();
  const [updateEmployee] = useUpdateEmployeeMutation();
  const [softDeleteEmployee] = useSoftDeleteEmployeeMutation();
  const [addEmployeeType] = useAddEmployeeTypeMutation();
  const [updateEmployeeType] = useUpdateEmployeeTypeMutation();
  const [softDeleteEmployeeType] = useSoftDeleteEmployeeTypeMutation();

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
      await addEmployee({ employee: newEmployee }).unwrap();
      setShowAddEmployee(false);
      setNewEmployee({ ...initialNewEmployee });
      showStatus('success', 'Employee added successfully!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleUpdateEmployee = async () => {
    if (!editEmployee || !editEmployee.name.trim()) return;
    try {
      await updateEmployee({
        id: editEmployee.id,
        update: {
          name: editEmployee.name,
          phone: editEmployee.phone || null,
          email: editEmployee.email || null,
          employee_type_id: editEmployee.employee_type_id,
          salary: editEmployee.salary,
        }
      }).unwrap();
      setShowEditEmployee(null);
      setEditEmployee(null);
      showStatus('success', 'Employee updated!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleDeleteEmployee = async () => {
    if (!showDeleteEmployee) return;
    try {
      await softDeleteEmployee({ id: showDeleteEmployee.id }).unwrap();
      setShowDeleteEmployee(null);
      showStatus('success', 'Employee deactivated.');
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Employee Type CRUD ──
  const handleAddType = async () => {
    if (!newType.name.trim()) return;
    try {
      await addEmployeeType({ employeeType: newType }).unwrap();
      setShowAddType(false);
      setNewType({ name: '', description: null });
      showStatus('success', 'Employee type added!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleUpdateType = async () => {
    if (!editType || !editType.name.trim()) return;
    try {
      await updateEmployeeType({
        id: editType.id,
        update: {
          name: editType.name,
          description: editType.description || null,
        }
      }).unwrap();
      setShowEditType(null);
      setEditType(null);
      showStatus('success', 'Employee type updated!');
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleDeleteType = async () => {
    if (!showDeleteType) return;
    try {
      await softDeleteEmployeeType({ id: showDeleteType.id }).unwrap();
      setShowDeleteType(null);
      showStatus('success', 'Employee type deactivated.');
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Loading State ──
  if (isLoading) {
    return (
      <PageLayout title={t('employees.title')} background="bg-slate-100 dark:bg-slate-900">
        <div className="space-y-6">
          <SkeletonList items={6} />
          <SkeletonTable rows={6} columns={5} />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={<><MdPeople className="text-indigo-500" /> Employees</>}
      background="bg-linear-to-br from-slate-100 via-indigo-100 to-slate-100 dark:from-slate-900 dark:via-indigo-950 dark:to-slate-900"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('employees.totalEmployees')}</h2>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{employees.filter(e => e.is_active).length}</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('employees.employeeTypes')}</h2>
            <p className="text-2xl font-bold text-indigo-500">{employeeTypes.filter(t => t.is_active).length}</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('employees.monthlySalary')}</h2>
            <p className="text-2xl font-bold text-emerald-500">{monthlySalaryTotal.toLocaleString()}</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('employees.avgSalary')}</h2>
            <p className="text-2xl font-bold text-blue-500">
              {employees.filter(e => e.is_active).length > 0
                ? Math.round(monthlySalaryTotal / employees.filter(e => e.is_active).length).toLocaleString()
                : 0}
            </p>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {getTabItems().map(tab => (
            <motion.button
              key={tab.key}
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-5 py-3 rounded-xl font-semibold text-sm transition-all duration-200 shrink-0 ${
                activeTab === tab.key
                  ? 'bg-indigo-500 text-white shadow-lg'
                  : 'bg-white/70 dark:bg-white/10 text-slate-700 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-800/30'
              }`}
            >
              {tab.icon} {tab.label}
            </motion.button>
          ))}
        </div>

        {/* ── TAB 1: EMPLOYEE LIST ── */}
        {activeTab === 'employees' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {/* Filters & Actions */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative">
                  <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder={t('employees.searchPlaceholder')}
                    className="pl-9 pr-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm w-48"
                  />
                </div>
                <select
                  value={typeFilter ?? ''}
                  onChange={e => setTypeFilter(e.target.value ? Number(e.target.value) : null)}
                  className="px-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm"
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
                          ? 'bg-indigo-500 text-white'
                          : 'bg-white/50 dark:bg-white/5 text-slate-700 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-800/30'
                      }`}
                    >
                      {s === 'all' ? t('employees.allTypesFilter') : s === 'active' ? t('employees.activeFilter') : t('employees.inactiveFilter')}
                    </button>
                  ))}
                </div>
              </div>
              <motion.button
                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={() => setShowAddEmployee(true)}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-xl font-semibold text-sm"
              >
                <FaPlus /> {t('employees.addEmployee')}
              </motion.button>
            </div>

            {/* Employee Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredEmployees.map(emp => (
                <motion.div
                  key={emp.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`card--glass rounded-xl p-4 border border-slate-200 dark:border-white/5
                    ${!emp.is_active ? 'opacity-60' : 'hover:border-indigo-300 dark:hover:border-indigo-500/30'} transition-all`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold
                        ${getTypeColor(getTypeName(emp.employee_type_id))}`}>
                        {emp.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 dark:text-white">{emp.name}</h3>
                        <span className="text-xs text-slate-500 dark:text-gray-400">{getTypeName(emp.employee_type_id)}</span>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => { setShowEditEmployee(emp); setEditEmployee({ ...emp }); }}
                        className="text-blue-500 hover:text-blue-400 p-1.5 rounded-lg hover:bg-blue-500/10" title={t('common.edit')}>
                        <MdEdit className="w-4 h-4" />
                      </button>
                      {emp.is_active && (
                        <button onClick={() => setShowDeleteEmployee(emp)}
                          className="text-red-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10" title={t('common.deactivate')}>
                          <MdDelete className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="space-y-1.5 text-sm">
                    <div className="flex items-center gap-2 text-slate-600 dark:text-gray-400">
                      <FaMoneyBillWave className="text-emerald-500 w-3.5 h-3.5" />
                      <span>{t('employees.salary')}: <strong className="text-slate-900 dark:text-white">{emp.salary.toLocaleString()}</strong></span>
                    </div>
                    {emp.phone && (
                      <div className="flex items-center gap-2 text-slate-600 dark:text-gray-400">
                        <FaPhone className="text-blue-400 w-3.5 h-3.5" />
                        <span>{emp.phone}</span>
                      </div>
                    )}
                    {emp.email && (
                      <div className="flex items-center gap-2 text-slate-600 dark:text-gray-400">
                        <FaEnvelope className="text-purple-400 w-3.5 h-3.5" />
                        <span className="truncate">{emp.email}</span>
                      </div>
                    )}
                    {emp.joined_at && (
                      <div className="flex items-center gap-2 text-slate-600 dark:text-gray-400">
                        <FaCalendarAlt className="text-indigo-400 w-3.5 h-3.5" />
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
                <div className="col-span-full card--glass rounded-xl p-8 text-center text-slate-600 dark:text-white/60">
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
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{t('employees.employeeTypes')}</h2>
              <motion.button
                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                onClick={() => setShowAddType(true)}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-xl font-semibold text-sm"
              >
                <FaPlus /> {t('employees.addType')}
              </motion.button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {employeeTypes.map(et => {
                const count = employees.filter(e => e.employee_type_id === et.id).length;
                return (
                  <motion.div
                    key={et.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className={`card--glass rounded-xl p-4 border border-slate-200 dark:border-white/5
                      ${!et.is_active ? 'opacity-60' : 'hover:border-indigo-300 dark:hover:border-indigo-500/30'} transition-all`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white text-lg
                          ${getTypeColor(et.name)}`}>
                          <MdWork />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-white">{et.name}</h3>
                          {et.description && (
                            <p className="text-xs text-slate-500 dark:text-gray-400 mt-0.5">{et.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={() => { setShowEditType(et); setEditType({ ...et }); }}
                          className="text-blue-500 hover:text-blue-400 p-1.5 rounded-lg hover:bg-blue-500/10" title={t('common.edit')}>
                          <MdEdit className="w-4 h-4" />
                        </button>
                        {et.is_active && (
                          <button onClick={() => setShowDeleteType(et)}
                            className="text-red-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10" title={t('common.deactivate')}>
                            <MdDelete className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="mt-3 flex items-center gap-2">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium
                        ${count > 0 ? 'bg-indigo-100 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400' : 'bg-slate-100 dark:bg-slate-700/30 text-slate-500 dark:text-gray-400'}`}>
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
                <div className="col-span-full card--glass rounded-xl p-8 text-center text-slate-600 dark:text-white/60">
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
          <button onClick={() => setShowAddEmployee(false)} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleAddEmployee} disabled={!newEmployee.name.trim() || newEmployee.employee_type_id === 0}
            className="flex-1 py-2.5 rounded-lg bg-indigo-500 text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <FaSave /> {t('employees.addEmployee')}
          </button>
        </>}
      >
        <div>
          <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.fullName')} *</label>
          <input type="text" value={newEmployee.name} onChange={e => setNewEmployee(p => ({ ...p, name: e.target.value }))}
            placeholder={t('employees.namePlaceholder') || 'Enter employee name'}
            className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.phone')}</label>
            <input type="tel" value={newEmployee.phone || ''} onChange={e => setNewEmployee(p => ({ ...p, phone: e.target.value || null }))}
              placeholder="03XX-XXXXXXX"
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
          </div>
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.email')}</label>
            <input type="email" value={newEmployee.email || ''} onChange={e => setNewEmployee(p => ({ ...p, email: e.target.value || null }))}
              placeholder={t('employees.email')}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.employeeType')} *</label>
            <select value={newEmployee.employee_type_id} onChange={e => setNewEmployee(p => ({ ...p, employee_type_id: Number(e.target.value) }))}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white">
              <option value={0}>{t('employees.selectType')}</option>
              {employeeTypes.filter(t => t.is_active).map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.monthlySalary')} *</label>
            <input type="number" step="1000" min="0" value={newEmployee.salary} onChange={e => setNewEmployee(p => ({ ...p, salary: Number(e.target.value) }))}
              placeholder="0"
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditEmployee && !!editEmployee}
        onClose={() => { setShowEditEmployee(null); setEditEmployee(null); }}
        title={t('employees.editEmployeeTitle')}
        footer={<>
          <button onClick={() => { setShowEditEmployee(null); setEditEmployee(null); }} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleUpdateEmployee} className="flex-1 py-2.5 rounded-lg bg-blue-500 text-white font-semibold flex items-center justify-center gap-2"><FaSave /> {t('common.update')}</button>
        </>}
      >
        {editEmployee && (<>
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.fullName')}</label>
            <input type="text" value={editEmployee.name} onChange={e => setEditEmployee(p => ({ ...p!, name: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.phone')}</label>
              <input type="tel" value={editEmployee.phone || ''} onChange={e => setEditEmployee(p => ({ ...p!, phone: e.target.value || undefined }))}
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
            </div>
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.email')}</label>
              <input type="email" value={editEmployee.email || ''} onChange={e => setEditEmployee(p => ({ ...p!, email: e.target.value || undefined }))}
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.employeeType')}</label>
              <select value={editEmployee.employee_type_id} onChange={e => setEditEmployee(p => ({ ...p!, employee_type_id: Number(e.target.value) }))}
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white">
                {employeeTypes.filter(t => t.is_active || t.id === editEmployee.employee_type_id).map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.monthlySalary')}</label>
              <input type="number" step="1000" value={editEmployee.salary} onChange={e => setEditEmployee(p => ({ ...p!, salary: Number(e.target.value) }))}
                className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
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
          <button onClick={() => setShowAddType(false)} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleAddType} disabled={!newType.name.trim()}
            className="flex-1 py-2.5 rounded-lg bg-indigo-500 text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <FaSave /> {t('employees.addType')}
          </button>
        </>}
      >
        <div>            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.typeName')} *</label>
          <input type="text" value={newType.name} onChange={e => setNewType(p => ({ ...p, name: e.target.value }))}
            placeholder={t('employees.typeNamePlaceholder')}
            className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
        </div>
        <div>
          <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.descriptionOptional')}</label>
          <textarea value={newType.description || ''} onChange={e => setNewType(p => ({ ...p, description: e.target.value || null }))}
            placeholder={t('employees.descPlaceholder')}
            rows={3}
            className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white resize-none" />
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditType && !!editType}
        onClose={() => { setShowEditType(null); setEditType(null); }}
        title={t('employees.editTypeTitle')}
        size="sm"
        footer={<>
          <button onClick={() => { setShowEditType(null); setEditType(null); }} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleUpdateType} className="flex-1 py-2.5 rounded-lg bg-blue-500 text-white font-semibold flex items-center justify-center gap-2"><FaSave /> {t('common.update')}</button>
        </>}
      >
        {editType && (<>
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.typeName')}</label>
            <input type="text" value={editType.name} onChange={e => setEditType(p => ({ ...p!, name: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
          </div>
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('employees.typeDescription')}</label>
            <textarea value={editType.description || ''}onChange={e => setEditType(p => ({ ...p!, description: e.target.value || undefined }))}
              rows={3}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white resize-none" />
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
