import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import { Payroll as PayrollType, Employee } from '../../types';
import { useCurrency } from '../../contexts/CurrencyContext';

export default function Payroll() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
  const [payrolls, setPayrolls] = useState<PayrollType[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ employee_id: 0, period_start: '', period_end: '', regular_hours: 0, overtime_hours: 0, total_pay: 0, status: 'pending' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [payrollsData, employeesData] = await Promise.all([
        invoke<PayrollType[]>('get_payrolls', { employeeId: null }),
        invoke<Employee[]>('get_employees', { includeInactive: false }),
      ]);
      setPayrolls(payrollsData);
      setEmployees(employeesData);
    } catch (error) {
      console.error('Error loading payrolls:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await invoke('add_payroll', { payroll: form });
      setShowForm(false);
      setForm({ employee_id: 0, period_start: '', period_end: '', regular_hours: 0, overtime_hours: 0, total_pay: 0, status: 'pending' });
      await loadData();
    } catch (error) {
      console.error('Error saving payroll:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('delete_payroll', { id });
      await loadData();
    } catch (error) {
      console.error('Error deleting payroll:', error);
    }
  };

  const getEmployeeName = (id: number) => employees.find(e => e.id === id)?.name || t('common.unknown');

  return (
    <PageLayout title={t('payroll.title')}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-base-content">{t('payroll.title')}</h1>
          <button onClick={() => setShowForm(true)} className="btn btn-primary gap-2 active:scale-[0.98] transition-all">
            <span className="ri-add-line" /> {t('payroll.addPayroll')}
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select value={form.employee_id} onChange={e => setForm({ ...form, employee_id: Number(e.target.value) })} required className="select w-full">
                <option value={0}>{t('payroll.selectEmployee')}</option>
                {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name}</option>)}
              </select>
              <input type="date" value={form.period_start} onChange={e => setForm({ ...form, period_start: e.target.value })} required className="input w-full" />
              <input type="date" value={form.period_end} onChange={e => setForm({ ...form, period_end: e.target.value })} required className="input w-full" />
              <input type="number" step="0.1" value={form.regular_hours} onChange={e => setForm({ ...form, regular_hours: Number(e.target.value) })} placeholder={t('payroll.regularHours')} className="input w-full" />
              <input type="number" step="0.1" value={form.overtime_hours} onChange={e => setForm({ ...form, overtime_hours: Number(e.target.value) })} placeholder={t('payroll.overtimeHours')} className="input w-full" />
              <input type="number" step="0.01" value={form.total_pay} onChange={e => setForm({ ...form, total_pay: Number(e.target.value) })} placeholder={t('payroll.totalPay')} required className="input w-full" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">{t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost">{t('common.cancel')}</button>
            </div>
          </form>
        )}

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : payrolls.length === 0 ? (
          <div className="text-center py-12 text-slate-500">{t('payroll.noPayrolls')}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {payrolls.map(payroll => (
              <div key={payroll.id} className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center text-success">
                      <span className="ri-money-dollar-box-line ri-20px" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">{getEmployeeName(payroll.employee_id)}</h3>
                      <p className="text-sm text-slate-500 capitalize">{payroll.status}</p>
                    </div>
                  </div>
                  <button onClick={() => handleDelete(payroll.id)} className="p-2 text-slate-600 hover:text-red-600"><span className="ri-delete-bin-line" /></button>
                </div>
                <div className="mt-3 text-sm text-base-content/60 space-y-1">
                  <p>{payroll.period_start} - {payroll.period_end}</p>
                  <p>{t('payroll.regularHours')}: {payroll.regular_hours}</p>
                  <p>{t('payroll.overtimeHours')}: {payroll.overtime_hours}</p>
                  <p className="font-semibold text-emerald-600">{t('payroll.totalPay')}: {formatPrice(payroll.total_pay)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}
