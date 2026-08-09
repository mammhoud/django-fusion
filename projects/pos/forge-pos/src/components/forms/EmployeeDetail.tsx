import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import Modal from '../ui/Modal';
import { Badge } from '../ui/badge';
import { Employee, EmployeeType, Payroll, UserAction } from '../../types';

interface EmployeeDetailProps {
  employee: Employee | null;
  employeeTypes: EmployeeType[];
  onClose: () => void;
}

/** Pretty-print an ISO/naive UTC timestamp as a local date + time. */
function formatTimestamp(value: string | null | undefined): string {
  if (!value) return '—';
  // Diesel NaiveDateTime serializes as "2026-11-15T10:30:00" — treat as local.
  const date = new Date(value.endsWith('Z') ? value : `${value.replace(' ', 'T')}Z`);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

/** Row helper for the profile grid. */
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
  generate_payrolls: 'ri-money-cny-circle-line text-secondary',
  add_payroll: 'ri-money-dollar-box-line text-success',
  update_payroll: 'ri-refresh-line text-info',
  delete_payroll: 'ri-delete-bin-line text-error',
};

export default function EmployeeDetail({ employee, employeeTypes, onClose }: EmployeeDetailProps) {
  const { t } = useTranslation();
  const [payrolls, setPayrolls] = useState<Payroll[]>([]);
  const [audit, setAudit] = useState<UserAction[]>([]);
  const [loading, setLoading] = useState(false);

  const loadDetail = useCallback(async (emp: Employee) => {
    setLoading(true);
    try {
      const [payrollRows, auditRows] = await Promise.all([
        invoke<Payroll[]>('get_payrolls', { employeeId: emp.id }),
        invoke<UserAction[]>('get_user_actions_for_entity', {
          entityType: 'employee',
          entityId: emp.id,
          limit: 50,
        }),
      ]);
      setPayrolls(payrollRows);
      setAudit(auditRows);
    } catch (e) {
      console.error('Error loading employee detail:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  // Reload whenever a (possibly different) employee is opened.
  useEffect(() => {
    if (employee) {
      setPayrolls([]);
      setAudit([]);
      loadDetail(employee);
    }
  }, [employee, loadDetail]);

  const typeName = employee
    ? employeeTypes.find((t2) => t2.id === employee.employee_type_id)?.name || `Type #${employee.employee_type_id}`
    : '';

  const totalPaid = payrolls
    .filter((p) => p.status === 'paid')
    .reduce((sum, p) => sum + p.total_pay, 0);
  const pendingTotal = payrolls
    .filter((p) => p.status === 'pending')
    .reduce((sum, p) => sum + p.total_pay, 0);

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
          {/* ── Header strip: status + key numbers ── */}
          <div className="flex flex-wrap items-center gap-3">
            <Badge className={employee.is_active
              ? 'border-success/30 bg-success/15 text-success'
              : 'border-error/30 bg-error/15 text-error'}>
              {employee.is_active ? t('common.active') : t('common.inactive')}
            </Badge>
            <Badge className="border-info/30 bg-info/15 text-info">
              {employee.pay_frequency === 'hourly'
                ? t('employees.payFrequencyHourly') || 'Hourly'
                : t('employees.payFrequencyMonthly') || 'Monthly'}
            </Badge>
            <span className="text-sm text-base-content/60 tabular-nums">
              {t('employees.salary')}:{' '}
              <strong className="text-base-content">
                {employee.pay_frequency === 'hourly'
                  ? `${employee.hourly_rate?.toLocaleString?.() ?? employee.hourly_rate}/h`
                  : employee.salary.toLocaleString()}
              </strong>
            </span>
          </div>

          {/* ── Personal ── */}
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
            </div>
          </section>

          {/* ── Payroll & bank ── */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold text-base-content mb-3">
              <span className="ri-money-dollar-box-line text-success" /> {t('employees.salaryPayroll') || 'Salary & payroll'}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl p-4">
              <Field icon="ri-money-dollar-circle-line" label={t('employees.salary') || 'Salary'} value={employee.salary?.toLocaleString?.() ?? String(employee.salary)} />
              {employee.pay_frequency === 'hourly' && (
                <Field icon="ri-timer-line" label={t('employees.hourlyRate') || 'Hourly rate'} value={employee.hourly_rate?.toLocaleString?.() ?? String(employee.hourly_rate)} />
              )}
              <Field icon="ri-landmark-line" label={t('employees.bankName') || 'Bank name'} value={employee.bank_name} />
              <Field icon="ri-bank-card-line" label={t('employees.bankAccount') || 'Bank account'} value={employee.bank_account} />
              <Field icon="ri-file-list-3-line" label={t('employees.taxNumber') || 'Tax number'} value={employee.tax_number} />
              {employee.notes && (
                <div className="sm:col-span-2">
                  <Field icon="ri-sticky-note-line" label={t('employees.notes') || 'Notes'} value={employee.notes} />
                </div>
              )}
            </div>
          </section>

          {/* ── Payroll history ── */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold text-base-content mb-3">
              <span className="ri-history-line text-secondary" /> {t('employees.payrollHistory') || 'Payroll history'}
            </h3>
            {loading ? (
              <p className="text-sm text-base-content/50 py-4">Loading…</p>
            ) : payrolls.length === 0 ? (
              <p className="text-sm text-base-content/50 py-4 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl px-4">
                {t('payroll.noPayrolls') || 'No payroll records.'}
              </p>
            ) : (
              <>
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-base-content/40">{t('employees.paidTotal') || 'Paid'}</p>
                    <p className="text-lg font-bold text-success tabular-nums">{totalPaid.toLocaleString()}</p>
                  </div>
                  <div className="bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl p-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wider text-base-content/40">{t('employees.pendingTotal') || 'Pending'}</p>
                    <p className="text-lg font-bold text-secondary tabular-nums">{pendingTotal.toLocaleString()}</p>
                  </div>
                </div>
                <div className="overflow-x-auto bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs uppercase tracking-wider text-base-content/50">
                        <th className="px-4 py-2.5 font-medium">{t('payroll.periodStart') || 'Period'}</th>
                        <th className="px-4 py-2.5 font-medium text-right">{t('payroll.regularHours') || 'Regular hrs'}</th>
                        <th className="px-4 py-2.5 font-medium text-right">{t('payroll.overtimeHours') || 'Overtime'}</th>
                        <th className="px-4 py-2.5 font-medium text-right">{t('payroll.totalPay') || 'Total pay'}</th>
                        <th className="px-4 py-2.5 font-medium">{t('common.status') || 'Status'}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payrolls.map((p) => (
                        <tr key={p.id} className="border-b border-slate-100 dark:border-white/5 last:border-0">
                          <td className="px-4 py-2.5 text-base-content">
                            {p.period_start} → {p.period_end}
                          </td>
                          <td className="px-4 py-2.5 text-right tabular-nums text-base-content/70">{p.regular_hours}</td>
                          <td className="px-4 py-2.5 text-right tabular-nums text-base-content/70">{p.overtime_hours}</td>
                          <td className="px-4 py-2.5 text-right tabular-nums font-semibold text-base-content">{p.total_pay.toLocaleString()}</td>
                          <td className="px-4 py-2.5">
                            {p.status === 'paid' ? (
                              <Badge className="border-success/30 bg-success/15 text-success">{t('common.paid') || 'Paid'}</Badge>
                            ) : (
                              <Badge className="border-warning/30 bg-warning/15 text-warning">{t('common.pending') || 'Pending'}</Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </section>

          {/* ── Audit trail ── */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-semibold text-base-content mb-3">
              <span className="ri-file-shield-2-line text-primary" /> {t('employees.auditTrail') || 'Audit trail'}
            </h3>
            {loading ? (
              <p className="text-sm text-base-content/50 py-4">Loading…</p>
            ) : audit.length === 0 ? (
              <p className="text-sm text-base-content/50 py-4 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl px-4">
                {t('employees.noAudit') || 'No recorded actions for this employee.'}
              </p>
            ) : (
              <ol className="space-y-2">
                {audit.map((a) => {
                  const iconClass = ACTION_ICONS[a.action] || 'ri-file-list-3-line text-base-content/50';
                  let detailsLabel = a.details || '';
                  try {
                    const parsed = JSON.parse(a.details || '{}');
                    if (parsed && Object.keys(parsed).length > 0) {
                      detailsLabel = Object.entries(parsed)
                        .map(([k, v]) => `${k}: ${String(v)}`)
                        .join(' · ');
                    }
                  } catch {
                    /* keep raw details string */
                  }
                  return (
                    <li
                      key={a.id}
                      className="flex items-start gap-3 bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl px-4 py-3"
                    >
                      <span className={`${iconClass} mt-0.5 shrink-0`} />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-base-content">
                          {a.action.replace(/_/g, ' ')}
                        </p>
                        {detailsLabel && (
                          <p className="text-xs text-base-content/50 truncate">{detailsLabel}</p>
                        )}
                      </div>
                      <span className="text-xs text-base-content/40 whitespace-nowrap tabular-nums">
                        {formatTimestamp(a.created_at)}
                      </span>
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
