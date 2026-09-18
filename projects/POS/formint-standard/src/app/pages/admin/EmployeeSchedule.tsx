import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../../components/layout/PageLayout';
import Card from '../../../components/ui/Card';
import FormModal from '../../../components/ui/FormModal';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';
import { useTranslation } from 'react-i18next';
import { EmployeeSchedule as EmployeeScheduleType, Employee } from '../../../types';

const SCHEDULE_STATUSES = ['scheduled', 'in_progress', 'completed', 'cancelled'];

interface ScheduleForm {
  employee_id: number;
  shift_start: string;
  shift_end: string;
  status: string;
  notes: string;
}

const emptyForm: ScheduleForm = {
  employee_id: 0,
  shift_start: '',
  shift_end: '',
  status: 'scheduled',
  notes: '',
};

export default function EmployeeSchedule() {
  const { t } = useTranslation();
  const [schedules, setSchedules] = useState<EmployeeScheduleType[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<EmployeeScheduleType | null>(null);
  const [form, setForm] = useState<ScheduleForm>(emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toDelete, setToDelete] = useState<EmployeeScheduleType | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [schedulesData, employeesData] = await Promise.all([
        invoke<EmployeeScheduleType[]>('get_employee_schedules', { employeeId: null }),
        invoke<Employee[]>('get_employees', { includeInactive: false }),
      ]);
      setSchedules(schedulesData);
      setEmployees(employeesData);
    } catch (error) {
      console.error('Error loading schedules:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowForm(true);
  };

  const openEdit = (schedule: EmployeeScheduleType) => {
    setEditing(schedule);
    setForm({
      employee_id: schedule.employee_id,
      shift_start: schedule.shift_start,
      shift_end: schedule.shift_end,
      status: schedule.status,
      notes: schedule.notes || '',
    });
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditing(null);
    setForm(emptyForm);
  };

  const handleSubmit = async () => {
    if (!form.employee_id || !form.shift_start || !form.shift_end) return;
    setIsSubmitting(true);
    try {
      if (editing) {
        await invoke('update_employee_schedule', {
          id: editing.id,
          update: {
            employee_id: form.employee_id,
            shift_start: form.shift_start,
            shift_end: form.shift_end,
            status: form.status,
            notes: form.notes || null,
          },
        });
      } else {
        await invoke('add_employee_schedule', {
          schedule: {
            employee_id: form.employee_id,
            shift_start: form.shift_start,
            shift_end: form.shift_end,
            status: form.status,
            notes: form.notes || null,
          },
        });
      }
      closeForm();
      await loadData({ quiet: true });
    } catch (error) {
      console.error('Error saving schedule:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await invoke('delete_employee_schedule', { id: toDelete.id });
      setToDelete(null);
      await loadData({ quiet: true });
    } catch (error) {
      console.error('Error deleting schedule:', error);
    }
  };

  const getEmployeeName = (id: number) =>
    employees.find((e) => e.id === id)?.name || t('common.unknown');

  return (
    <PageLayout title={t('schedule.title')}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-base-content">{t('schedule.title')}</h1>
          <button
            onClick={openAdd}
            className="btn btn-primary gap-2 active:scale-[0.98] transition-transform"
          >
            <span className="ri-add-line" /> {t('schedule.addShift')}
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : schedules.length === 0 ? (
          <div className="text-center py-12 text-slate-500">{t('schedule.noShifts')}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {schedules.map((schedule) => (
              <Card key={schedule.id}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-secondary/10 dark:bg-secondary/20 flex items-center justify-center text-secondary dark:text-secondary/80">
                      <span className="ri-calendar-2-line ri-20px" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">
                        {getEmployeeName(schedule.employee_id)}
                      </h3>
                      <p className="text-sm text-slate-500 capitalize">{schedule.status}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={() => openEdit(schedule)}
                      className="p-2 text-slate-600 hover:text-primary transition-colors"
                    >
                      <span className="ri-pencil-line" />
                    </button>
                    <button
                      onClick={() => setToDelete(schedule)}
                      className="p-2 text-slate-600 hover:text-red-600 transition-colors"
                    >
                      <span className="ri-delete-bin-line" />
                    </button>
                  </div>
                </div>
                <div className="mt-3 text-sm text-base-content/60 space-y-1">
                  <p>
                    {new Date(schedule.shift_start).toLocaleString()} -{' '}
                    {new Date(schedule.shift_end).toLocaleTimeString()}
                  </p>
                  {schedule.notes && <p>{schedule.notes}</p>}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <FormModal
        isOpen={showForm}
        onClose={closeForm}
        title={editing ? t('schedule.editShift', 'Edit shift') : t('schedule.addShift')}
        submitLabel={editing ? t('common.update') : t('common.save')}
        submitDisabled={!form.employee_id || !form.shift_start || !form.shift_end}
        isSubmitting={isSubmitting}
        onSubmit={handleSubmit}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="field sm:col-span-2">
            <label className="label text-xs">{t('schedule.selectEmployee')}</label>
            <select
              value={form.employee_id}
              onChange={(e) => setForm({ ...form, employee_id: Number(e.target.value) })}
              className="select w-full"
            >
              <option value={0}>{t('schedule.selectEmployee')}</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label text-xs">{t('schedule.shiftStart', 'Shift start')}</label>
            <input
              type="datetime-local"
              value={form.shift_start}
              onChange={(e) => setForm({ ...form, shift_start: e.target.value })}
              className="input w-full"
            />
          </div>
          <div className="field">
            <label className="label text-xs">{t('schedule.shiftEnd', 'Shift end')}</label>
            <input
              type="datetime-local"
              value={form.shift_end}
              onChange={(e) => setForm({ ...form, shift_end: e.target.value })}
              className="input w-full"
            />
          </div>
          <div className="field">
            <label className="label text-xs">{t('schedule.status', 'Status')}</label>
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
              className="select w-full"
            >
              {SCHEDULE_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label className="label text-xs">{t('schedule.notes')}</label>
            <input
              type="text"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder={t('schedule.notes')}
              className="input w-full"
            />
          </div>
        </div>
      </FormModal>

      <ConfirmDialog
        isOpen={!!toDelete}
        onClose={() => setToDelete(null)}
        onConfirm={handleDelete}
        title={t('schedule.deleteShift', 'Delete shift')}
        message={t('schedule.deleteShiftMessage', 'This will permanently remove the shift for')}
        itemName={toDelete ? getEmployeeName(toDelete.employee_id) : ''}
        confirmLabel={t('common.delete')}
      />
    </PageLayout>
  );
}
