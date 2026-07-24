import { useState } from 'react';
import { motion } from 'framer-motion';
import { MdSchedule, MdAdd, MdDelete } from 'react-icons/md';
import PageLayout from '../components/PageLayout';
import { FusionPage } from '../components/FusionPage';
import { useTranslation } from 'react-i18next';
import { useGetEmployeeSchedulesQuery, useAddEmployeeScheduleMutation, useDeleteEmployeeScheduleMutation } from '../store/api/endpoints/payroll';
import { useGetEmployeesQuery } from '../store/api/endpoints/core';

export default function EmployeeSchedule() {
  const { t } = useTranslation();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ employee_id: 0, shift_start: '', shift_end: '', status: 'scheduled', notes: '' });

  const { data: schedules = [], isLoading, error } = useGetEmployeeSchedulesQuery({});
  const { data: employees = [] } = useGetEmployeesQuery();
  const [addEmployeeSchedule] = useAddEmployeeScheduleMutation();
  const [deleteEmployeeSchedule] = useDeleteEmployeeScheduleMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addEmployeeSchedule(form).unwrap();
      setShowForm(false);
      setForm({ employee_id: 0, shift_start: '', shift_end: '', status: 'scheduled', notes: '' });
    } catch (error) {
      console.error('Error saving schedule:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await deleteEmployeeSchedule(id).unwrap();
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const getEmployeeName = (id: number) => employees.find(e => e.id === id)?.name || t('common.unknown');

  return (
    <PageLayout title={t('schedule.title')} background="bg-slate-100 dark:bg-slate-900">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('schedule.title')}</h1>
          <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600">
            <MdAdd /> {t('schedule.addShift')}
          </motion.button>
        </div>

        {showForm && (
          <motion.form initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="card--glass rounded-xl p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select value={form.employee_id} onChange={e => setForm({ ...form, employee_id: Number(e.target.value) })} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white">
                <option value={0}>{t('schedule.selectEmployee')}</option>
                {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name}</option>)}
              </select>
              <input type="datetime-local" value={form.shift_start} onChange={e => setForm({ ...form, shift_start: e.target.value })} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
              <input type="datetime-local" value={form.shift_end} onChange={e => setForm({ ...form, shift_end: e.target.value })} required className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
              <input type="text" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder={t('schedule.notes')} className="px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
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
          data={schedules}
          isLoading={isLoading}
          error={error}
          skeletonVariant="card"
        >
          {(data, fallback) => {
            const items = (data ?? []) as typeof schedules;
            if (items.length === 0) {
              return (
                <div className="text-center py-12 text-slate-500">{t('schedule.noShifts')}</div>
              );
            }
            return (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {items.map(schedule => (
                  <motion.div key={schedule.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card--glass rounded-xl p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400">
                          <MdSchedule className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-white">{getEmployeeName(schedule.employee_id)}</h3>
                          <p className="text-sm text-slate-500 capitalize">{schedule.status}</p>
                        </div>
                      </div>
                      <button onClick={() => handleDelete(schedule.id)} className="p-2 text-slate-600 hover:text-red-600"><MdDelete /></button>
                    </div>
                    <div className="mt-3 text-sm text-slate-600 dark:text-gray-400 space-y-1">
                      <p>{new Date(schedule.shift_start).toLocaleString()} - {new Date(schedule.shift_end).toLocaleTimeString()}</p>
                      {schedule.notes && <p>{schedule.notes}</p>}
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
