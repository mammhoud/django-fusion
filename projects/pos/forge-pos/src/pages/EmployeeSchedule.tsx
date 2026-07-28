import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../components/PageLayout';
import Card from '../components/Card';
import { useTranslation } from 'react-i18next';
import { EmployeeSchedule as EmployeeScheduleType, Employee } from '../types';

export default function EmployeeSchedule() {
  const { t } = useTranslation();
  const [schedules, setSchedules] = useState<EmployeeScheduleType[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ employee_id: 0, shift_start: '', shift_end: '', status: 'scheduled', notes: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [schedulesData, employeesData] = await Promise.all([
        invoke<EmployeeScheduleType[]>('get_employee_schedules', { employeeId: null }),
        invoke<Employee[]>('get_employees', { includeInactive: false }),
      ]);
      setSchedules(schedulesData);
      setEmployees(employeesData);
    } catch (error) {
      console.error('Error loading schedules:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await invoke('add_employee_schedule', { schedule: form });
      setShowForm(false);
      setForm({ employee_id: 0, shift_start: '', shift_end: '', status: 'scheduled', notes: '' });
      await loadData();
    } catch (error) {
      console.error('Error saving schedule:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('delete_employee_schedule', { id });
      await loadData();
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const getEmployeeName = (id: number) => employees.find(e => e.id === id)?.name || t('common.unknown');

  return (
    <PageLayout title={t('schedule.title')}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-base-content">{t('schedule.title')}</h1>
          <motion.button whileHover={{ y: -2 }} whileTap={{ scale: 0.98 }} onClick={() => setShowForm(true)} className="btn btn-primary gap-2">
            <span className="icon-[tabler--plus]" /> {t('schedule.addShift')}
          </motion.button>
        </div>

        {showForm && (
          <Card spaceY="3">
            <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <select value={form.employee_id} onChange={e => setForm({ ...form, employee_id: Number(e.target.value) })} required className="select select-bordered w-full">
                <option value={0}>{t('schedule.selectEmployee')}</option>
                {employees.map(emp => <option key={emp.id} value={emp.id}>{emp.name}</option>)}
              </select>
              <input type="datetime-local" value={form.shift_start} onChange={e => setForm({ ...form, shift_start: e.target.value })} required className="input input-bordered w-full" />
              <input type="datetime-local" value={form.shift_end} onChange={e => setForm({ ...form, shift_end: e.target.value })} required className="input input-bordered w-full" />
              <input type="text" value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder={t('schedule.notes')} className="input input-bordered w-full" />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn btn-primary">{t('common.save')}</button>
              <button type="button" onClick={() => setShowForm(false)} className="btn btn-ghost">{t('common.cancel')}</button>
            </div>
            </form>
          </Card>
        )}

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : schedules.length === 0 ? (
          <div className="text-center py-12 text-slate-500">{t('schedule.noShifts')}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {schedules.map(schedule => (
              <Card key={schedule.id}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400">
                      <span className="icon-[tabler--calendar-clock] w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">{getEmployeeName(schedule.employee_id)}</h3>
                      <p className="text-sm text-slate-500 capitalize">{schedule.status}</p>
                    </div>
                  </div>
                  <button onClick={() => handleDelete(schedule.id)} className="p-2 text-slate-600 hover:text-red-600"><span className="icon-[tabler--trash]" /></button>
                </div>
                <div className="mt-3 text-sm text-base-content/60 space-y-1">
                  <p>{new Date(schedule.shift_start).toLocaleString()} - {new Date(schedule.shift_end).toLocaleTimeString()}</p>
                  {schedule.notes && <p>{schedule.notes}</p>}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  );
}

