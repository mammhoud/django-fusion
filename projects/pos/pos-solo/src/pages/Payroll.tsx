import { useState } from 'react';
import { motion } from 'framer-motion';
import { MdAttachMoney, MdAdd, MdDelete } from 'react-icons/md';
import PageLayout from '../components/PageLayout';
import { FusionPage } from '../components/FusionPage';
import { useTranslation } from 'react-i18next';
import { useGetPayrollRecordsQuery, useAddPayrollMutation, useDeletePayrollMutation } from '../store/api/endpoints/payroll';
import { useGetEmployeesQuery } from '../store/api/endpoints/core';

export default function Payroll() {
  const { t } = useTranslation();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ employee_id: 0, period_start: '', period_end: '', regular_hours: 0, overtime_hours: 0, total_pay: 0, status: 'pending' });

  const { data: payrolls = [], isLoading, error } = useGetPayrollRecordsQuery();
  const { data: employees = [] } = useGetEmployeesQuery();
  const [addPayroll] = useAddPayrollMutation();
  const [deletePayroll] = useDeletePayrollMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addPayroll(form).unwrap();
      setShowForm(false);
      setForm({ employee_id: 0, period_start: '', period_end: '', regular_hours: 0, overtime_hours: 0, total_pay: 0, status: 'pending' });
    } catch (error) {
      console.error('Error saving payroll:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await deletePayroll(id).unwrap();
    } catch (error) {
      console.error('Error deleting payroll:', error);
    }
  };

  const getEmployeeName = (id: number) => employees.find(e => e.id === id)?.name || t('common.unknown');

  return (
    <PageLayout title={t('payroll.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('payroll.title')}</h1>
          <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">
            <MdAdd /> {t('payroll.addPayroll')}
          </motion.button>
        </div>

        {showForm && (
          <motion.form initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="card--glass rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select value={form.employee_id} onChange={e => setForm({ ...form, employee_id: Number(e.target.value) })} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white">
                <option value={0}>{t('payroll.selectEmployee')}</option>
                {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name}</option>)}
              </select>
              <input type="date" value={form.period_start} onChange={e => setForm({ ...form, period_start: e.target.value })} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
              <input type="date" value={form.period_end} onChange={e => setForm({ ...form, period_end: e.target.value })} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
              <input type="number" step="0.1" value={form.regular_hours} onChange={e => setForm({ ...form, regular_hours: Number(e.target.value) })} placeholder={t('payroll.regularHours')} className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
              <input type="number" step="0.1" value={form.overtime_hours} onChange={e => setForm({ ...form, overtime_hours: Number(e.target.value) })} placeholder={t('payroll.overtimeHours')} className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
              <input type="number" step="0.01" value={form.total_pay} onChange={e => setForm({ ...form, total_pay: Number(e.target.value) })} placeholder={t('payroll.totalPay')} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">{t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 bg-slate-300 dark:bg-slate-700 rounded-lg">{t('common.cancel')}</button>
            </div>
          </motion.form>
        )}

        {/* Data rendering wrapped with FusionPage for fragment-rendering support */}
        <FusionPage
          standalone
          data={payrolls}
          isLoading={isLoading}
          error={error}
          skeletonVariant="card"
        >
          {(data, fallback) => {
            const items = (data ?? []) as typeof payrolls;
            if (items.length === 0) {
              return (
                <div className="text-center py-12 text-slate-500">{t('payroll.noPayrolls')}</div>
              );
            }
            return (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {items.map(payroll => (
                  <motion.div key={payroll.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card--glass rounded-xl p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                          <MdAttachMoney className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-white">{getEmployeeName(payroll.employee_id)}</h3>
                          <p className="text-sm text-slate-500 capitalize">{payroll.status}</p>
                        </div>
                      </div>
                      <button onClick={() => handleDelete(payroll.id)} className="p-2 text-slate-600 hover:text-red-600"><MdDelete /></button>
                    </div>
                    <div className="mt-3 text-sm text-slate-600 dark:text-gray-400 space-y-1">
                      <p>{payroll.period_start} - {payroll.period_end}</p>
                      <p>{t('payroll.regularHours')}: {payroll.regular_hours}</p>
                      <p>{t('payroll.overtimeHours')}: {payroll.overtime_hours}</p>
                      <p className="font-semibold text-emerald-600">{t('payroll.totalPay')}: {(payroll.total_pay ?? 0).toFixed(2)}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            );
          }}
        </FusionPage>
      </div>
    </PageLayout>
  );
}
