import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import Modal from '../ui/Modal';
import { Badge } from '../ui/badge';
import { Employee, EmployeeType, UserAction } from '../../types';

interface EmployeeDetailProps {
  employee: Employee | null;
  employeeTypes: EmployeeType[];
  onClose: () => void;
}

/** Pretty-print an ISO/naive UTC timestamp as a local date + time. */
function formatTimestamp(value: string | null | undefined): string {
  if (!value) return '—';
  const normalized = value.replace(' ', 'T');
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function Field({ icon, label, value }: { icon: string; label: string; value?: string | null }) {
  return (
    <div className="flex items-start gap-2.5 min-w-0">
      <span className={`${icon} text-base-content/50 mt-0.5 shrink-0`} />
      <div className="min-w-0">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-base-content/40">{label}</p>
        <p className="text-sm text-base-content truncate">{value || '—'}</p>
      </div>
    </div>
  );
}

const ACTION_ICONS: Record<string, string> = {
  add_employee: 'ri-user-add-line text-success',
  update_employee: 'ri-pencil-line text-info',
  deactivate_employee: 'ri-delete-bin-line text-error',
  reactivate_employee: 'ri-user-follow-line text-success',
};

export default function EmployeeDetail({ employee, employeeTypes, onClose }: EmployeeDetailProps) {
  const { t } = useTranslation();
  const [audit, setAudit] = useState<UserAction[]>([]);
  const [loading, setLoading] = useState(false);

  const loadDetail = useCallback(async (emp: Employee) => {
    setLoading(true);
    try {
      const auditRows = await invoke<UserAction[]>('get_user_actions_for_entity', {
        entityType: 'employee',
        entityId: emp.id,
        limit: 50,
      });
      setAudit(auditRows);
    } catch (e) {
      console.error('Error loading employee detail:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (employee) {
      setAudit([]);
      loadDetail(employee);
    }
  }, [employee, loadDetail]);

  const typeName = employee
    ? employeeTypes.find((type) => type.id === employee.employee_type_id)?.name || `Type #${employee.employee_type_id}`
    : '';

  return (
    <Modal
      isOpen={!!employee}
      onClose={onClose}
      size="xl"
      scroll
      title={employee?.name || ''}
      headerIcon={<span className="ri-profile-line text-info" />}
      subtitle={typeName || undefined}
      footer={
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 rounded-xl bg-base-300/60 text-base-content font-semibold text-sm hover:bg-base-300 active:scale-[0.98] transition-all"
        >
          {t('common.close') || 'Close'}
        </button>
      }
      contentTestId="employee-detail-modal"
    >
      {employee && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-3">
            <Badge className={employee.is_active
              ? 'border-success/30 bg-success/15 text-success'
              : 'border-error/30 bg-error/15 text-error'}>
              {employee.is_active ? t('common.active') : t('common.inactive')}
            </Badge>
            <Badge className="border-info/30 bg-info/15 text-info">{typeName}</Badge>
            {employee.joined_at && (
              <span className="text-sm text-base-content/60">
                {t('employees.joined') || 'Joined'} {employee.joined_at}
              </span>
            )}
          </div>

          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold text-base-content mb-3">
              <span className="ri-user-3-line text-info" /> {t('employees.stepPersonal') || 'Personal'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl p-4">
              <Field icon="ri-phone-line" label={t('employees.phone') || 'Phone'} value={employee.phone} />
              <Field icon="ri-mail-line" label={t('employees.email') || 'Email'} value={employee.email} />
              <Field icon="ri-calendar-line" label={t('employees.joinedDate') || 'Joined date'} value={employee.joined_at} />
              <Field icon="ri-cake-2-line" label={t('employees.dateOfBirth') || 'Date of birth'} value={employee.date_of_birth} />
              <Field icon="ri-fingerprint-line" label={t('employees.nationalId') || 'National ID'} value={employee.national_id} />
              <Field icon="ri-lifebuoy-line" label={t('employees.emergencyContact') || 'Emergency contact'} value={employee.emergency_contact} />
              <Field icon="ri-map-pin-line" label={t('employees.address') || 'Address'} value={employee.address} />
              {employee.notes && (
                <div className="sm:col-span-2">
                  <Field icon="ri-sticky-note-line" label={t('employees.notes') || 'Notes'} value={employee.notes} />
                </div>
              )}
            </div>
          </section>

          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold text-base-content mb-3">
              <span className="ri-file-shield-2-line text-primary" /> {t('employees.auditTrail') || 'Audit trail'}
            </h3>
            {loading ? (
              <p className="text-sm text-base-content/50 py-4">{t('common.loading') || 'Loading…'}</p>
            ) : audit.length === 0 ? (
              <p className="text-sm text-base-content/50 py-4 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl px-4">
                {t('employees.noAudit') || 'No recorded actions for this employee.'}
              </p>
            ) : (
              <ol className="space-y-2">
                {audit.map((action) => {
                  const icon = ACTION_ICONS[action.action] || 'ri-file-list-3-line text-base-content/50';
                  let detailsLabel = action.details || '';
                  try {
                    const parsed = JSON.parse(action.details || '{}');
                    if (parsed && Object.keys(parsed).length > 0) {
                      detailsLabel = Object.entries(parsed)
                        .map(([key, value]) => `${key}: ${String(value)}`)
                        .join(' · ');
                    }
                  } catch {
                    // Keep the raw details string when it is not JSON.
                  }
                  return (
                    <li key={action.id} className="flex items-start gap-3 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3">
                      <span className={`${icon} mt-0.5 shrink-0`} />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-base-content">{action.action.replace(/_/g, ' ')}</p>
                        {detailsLabel && <p className="text-xs text-base-content/50 truncate">{detailsLabel}</p>}
                      </div>
                      <span className="text-xs text-base-content/40 whitespace-nowrap tabular-nums">{formatTimestamp(action.created_at)}</span>
                    </li>
                  );
                })}
              </ol>
            )}
          </section>
        </div>
      )}
    </Modal>
  );
}
