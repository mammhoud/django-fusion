import { useEffect, useMemo, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../../components/layout/PageLayout';
import Card from '../../../components/ui/Card';
import StatusToast from '../../../components/ui/StatusToast';
import { useStatusToast } from '../../../hooks/useStatusToast';
import { useTranslation } from 'react-i18next';
import { EmployeeSchedule as EmployeeScheduleType, Employee } from '../../../types';

type ScheduleForm = {
  employee_id: number;
  shift_start: string;
  shift_end: string;
  status: string;
  notes: string;
};

const EMPTY_FORM: ScheduleForm = {
  employee_id: 0,
  shift_start: '',
  shift_end: '',
  status: 'scheduled',
  notes: '',
};

const STATUS_OPTIONS = ['scheduled', 'completed', 'cancelled', 'no_show'];

function toDateTimeLocal(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value.slice(0, 16);
  const offset = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function validateForm(form: ScheduleForm): string | null {
  if (!form.employee_id) return 'Select an employee.';
  if (!form.shift_start || !form.shift_end) return 'Start and end times are required.';
  if (new Date(form.shift_end).getTime() <= new Date(form.shift_start).getTime()) {
    return 'Shift end must be after shift start.';
  }
  return null;
}

export default function EmployeeSchedule() {
  const { t } = useTranslation();
  const [schedules, setSchedules] = useState<EmployeeScheduleType[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<EmployeeScheduleType | null>(null);
  const [form, setForm] = useState<ScheduleForm>(EMPTY_FORM);
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  useEffect(() => {
    void loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [schedulesData, employeesData] = await Promise.all([
        invoke<EmployeeScheduleType[]>('get_employee_schedules', { employeeId: null }),
        invoke<Employee[]>('get_employees', { includeInactive: false }),
      ]);
      setSchedules(schedulesData ?? []);
      setEmployees(employeesData ?? []);
    } catch (error) {
      console.error('Error loading schedules:', error);
      showError(`${t('common.error', 'Error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  const openAddForm = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  };

  const openEditForm = (schedule: EmployeeScheduleType) => {
    setEditing(schedule);
    setForm({
      employee_id: schedule.employee_id,
      shift_start: toDateTimeLocal(schedule.shift_start),
      shift_end: toDateTimeLocal(schedule.shift_end),
      status: schedule.status,
      notes: schedule.notes ?? '',
    });
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditing(null);
    setForm(EMPTY_FORM);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const validationError = validateForm(form);
    if (validationError) {
      showError(validationError);
      return;
    }

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
        showSuccess(t('schedule.updated', 'Shift updated.'));
      } else {
        await invoke('add_employee_schedule', {
          schedule: { ...form, notes: form.notes || null },
        });
        showSuccess(t('schedule.created', 'Shift created.'));
      }
      closeForm();
      await loadData();
    } catch (error) {
      console.error('Error saving schedule:', error);
      showError(`${t('common.error', 'Error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm(t('common.confirmDelete'))) return;
    try {
      await invoke('delete_employee_schedule', { id });
      showSuccess(t('common.deleted', 'Deleted.'));
      await loadData();
    } catch (error) {
      console.error('Error deleting schedule:', error);
      showError(`${t('common.error', 'Error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const getEmployeeName = (id: number) => employees.find(employee => employee.id === id)?.name || t('common.unknown', 'Unknown');
  const sortedSchedules = useMemo(
    () => [...schedules].sort((a, b) => new Date(a.shift_start).getTime() - new Date(b.shift_start).getTime()),
    [schedules],
  );

  return (
    <PageLayout title={t('schedule.title')}>
      <div className="space-y-4">
        <div className="flex justify-between items-center gap-3">
          <h1 className="text-2xl font-bold text-base-content">{t('schedule.title')}</h1>
          <button onClick={openAddForm} className="btn btn-primary gap-2 active:scale-[0.98] transition-all">
            <span className="ri-add-line" /> {t('schedule.addShift')}
          </button>
        </div>

        {showForm && (
          <Card spaceY="3">
            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-base-content">
                  {editing ? t('schedule.editShift', 'Edit Shift') : t('schedule.addShift')}
                </h2>
                <span className="text-xs text-base-content/50">{t('schedule.overlapHint', 'Overlapping shifts are rejected.')}</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <select
                  aria-label={t('schedule.selectEmployee')}
                  value={form.employee_id}
                  onChange={event => setForm({ ...form, employee_id: Number(event.target.value) })}
                  required
                  className="select w-full"
                >
                  <option value={0}>{t('schedule.selectEmployee')}</option>
                  {employees.map(employee => <option key={employee.id} value={employee.id}>{employee.name}</option>)}
                </select>
                <select
                  aria-label={t('schedule.status', 'Status')}
                  value={form.status}
                  onChange={event => setForm({ ...form, status: event.target.value })}
                  className="select w-full"
                >
                  {STATUS_OPTIONS.map(option => <option key={option} value={option}>{option.replace('_', ' ')}</option>)}
                </select>
                <input aria-label={t('schedule.start', 'Start')} type="datetime-local" value={form.shift_start} onChange={event => setForm({ ...form, shift_start: event.target.value })} required className="input w-full" />
                <input aria-label={t('schedule.end', 'End')} type="datetime-local" value={form.shift_end} onChange={event => setForm({ ...form, shift_end: event.target.value })} required className="input w-full" />
                <input aria-label={t('schedule.notes')} type="text" value={form.notes} onChange={event => setForm({ ...form, notes: event.target.value })} placeholder={t('schedule.notes')} className="input w-full sm:col-span-2" />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary">{editing ? t('common.update') : t('common.save')}</button>
                <button type="button" onClick={closeForm} className="btn btn-ghost">{t('common.cancel')}</button>
              </div>
            </form>
          </Card>
        )}

        {isLoading ? (
          <div className="text-center py-12 text-slate-500">{t('common.loading')}</div>
        ) : sortedSchedules.length === 0 ? (
          <div className="text-center py-12 text-slate-500">{t('schedule.noShifts')}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
            {sortedSchedules.map(schedule => (
              <Card key={schedule.id}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-secondary/10 dark:bg-secondary/20 flex items-center justify-center text-secondary dark:text-secondary/80">
                      <span className="ri-calendar-2-line ri-20px" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">{getEmployeeName(schedule.employee_id)}</h3>
                      <p className="text-sm text-slate-500 capitalize">{schedule.status.replace('_', ' ')}</p>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button aria-label={`${t('common.edit')} ${getEmployeeName(schedule.employee_id)}`} onClick={() => openEditForm(schedule)} className="p-2 text-slate-600 hover:text-info"><span className="ri-pencil-line" /></button>
                    <button aria-label={`${t('common.delete')} ${getEmployeeName(schedule.employee_id)}`} onClick={() => handleDelete(schedule.id)} className="p-2 text-slate-600 hover:text-red-600"><span className="ri-delete-bin-line" /></button>
                  </div>
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
      <StatusToast type={status?.type ?? 'success'} message={status?.message ?? ''} visible={!!status} onDismiss={dismiss} />
    </PageLayout>
  );
}

export { validateForm };
