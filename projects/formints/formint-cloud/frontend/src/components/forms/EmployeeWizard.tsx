import { useEffect, useState } from 'react';
import Modal from '../ui/Modal';
import { useTranslation } from 'react-i18next';
import { NewEmployee, EmployeeType } from '../../types';
import { iconClass } from '../../lib/icons';

/**
 * Multi-step wizard for adding/editing employees.
 *
 * 4 steps, each with its own validation:
 *   1 · Personal — name, date of birth, national ID, emergency contact
 *   2 · Contact — phone, email, address, notes
 *   3 · Role & employment — employee type (the role), joined date
 *   4 · Salary & payroll — salary, pay frequency, bank details, tax number
 *
 * Works on a plain `NewEmployee` value object so the page owns persistence.
 * Uses the shared `Modal` frame + `.field`/`label-text` conventions so it
 * matches the other record forms.
 */
export interface EmployeeWizardProps {
  isOpen: boolean;
  value: NewEmployee;
  onChange: (next: NewEmployee) => void;
  employeeTypes: EmployeeType[];
  /** Keep the currently assigned (possibly inactive) type selectable when editing. */
  includeInactiveTypes?: boolean;
  /** Editing mode relaxes the employee-type requirement (deleted types stay editable). */
  isEditing: boolean;
  submitLabel: string;
  cancelLabel?: string;
  isSubmitting?: boolean;
  onClose: () => void;
  onSubmit: () => void;
  contentTestId?: string;
}

const STEPS = ['personal', 'contact', 'role', 'salary'] as const;
type Step = (typeof STEPS)[number];

export default function EmployeeWizard({
  isOpen,
  value,
  onChange,
  employeeTypes,
  includeInactiveTypes = false,
  isEditing,
  submitLabel,
  cancelLabel,
  isSubmitting = false,
  onClose,
  onSubmit,
  contentTestId,
}: EmployeeWizardProps) {
  const { t } = useTranslation();
  const [step, setStep] = useState<Step>('personal');

  // Reset to the first step whenever the modal opens.
  useEffect(() => {
    if (isOpen) setStep('personal');
  }, [isOpen]);

  const visibleTypes = employeeTypes.filter(
    et => et.is_active || (includeInactiveTypes && et.id === value.employee_type_id),
  );

  // ── Per-step validation ──
  const stepValid = (): boolean => {
    switch (step) {
      case 'personal':
        return value.name.trim().length > 0;
      case 'contact':
        return true;
      case 'role':
        // Type is only required when adding — an existing employee whose type
        // was deleted (employee_type_id 0) must stay editable.
        return isEditing || value.employee_type_id > 0;
      case 'salary':
        return (value.pay_frequency || 'monthly') === 'hourly'
          ? Number.isFinite(value.hourly_rate) && (value.hourly_rate ?? 0) > 0
          : Number.isFinite(value.salary) && value.salary > 0;
    }
  };

  const stepIndex = STEPS.indexOf(step);
  const isLastStep = step === 'salary';

  const next = () => {
    if (step === 'personal') setStep('contact');
    else if (step === 'contact') setStep('role');
    else if (step === 'role') setStep('salary');
  };

  const back = () => {
    if (step === 'contact') setStep('personal');
    else if (step === 'role') setStep('contact');
    else if (step === 'salary') setStep('role');
  };

  const stepLabel = (s: Step) => {
    switch (s) {
      case 'personal': return t('employees.stepPersonal') || 'Personal';
      case 'contact': return t('employees.stepContact') || 'Contact';
      case 'role': return t('employees.stepRole') || 'Role';
      case 'salary': return t('employees.stepSalary') || 'Salary & payroll';
    }
  };

  const fieldIcon = (icon: string) => (
    <span className={iconClass(icon, 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />
  );

  const inputCls = 'input w-full h-9 text-sm';

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? t('employees.editEmployeeTitle') : t('employees.addEmployeeTitle')}
      size="lg"
      contentTestId={contentTestId}
      footer={
        <div className="flex gap-2 w-full">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="btn btn-ghost flex-1 disabled:opacity-50"
          >
            {cancelLabel ?? t('common.cancel')}
          </button>
          {stepIndex > 0 && (
            <button
              onClick={back}
              disabled={isSubmitting}
              className="btn btn-ghost flex-1 disabled:opacity-50"
            >
              <span className="ri-arrow-left-line ri-16px" />
              {t('employees.back') || 'Back'}
            </button>
          )}
          {isLastStep ? (
            <button
              onClick={onSubmit}
              disabled={!stepValid() || isSubmitting}
              data-testid={contentTestId ? `${contentTestId}-submit` : undefined}
              className="btn btn-primary flex-1 disabled:opacity-50 gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  {submitLabel}
                </>
              ) : (
                <>
                  <span className="ri-save-3-line ri-16px" />
                  {submitLabel}
                </>
              )}
            </button>
          ) : (
            <button
              onClick={next}
              disabled={!stepValid() || isSubmitting}
              className="btn btn-primary flex-1 disabled:opacity-50"
            >
              {t('employees.next') || 'Next'}
              <span className="ri-arrow-right-line ri-16px" />
            </button>
          )}
        </div>
      }
    >
      {/* ── Progress steps ── */}
      <div className="flex items-center gap-2 mb-5">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center gap-2 flex-1 min-w-0">
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all
                ${i === stepIndex
                  ? 'bg-primary/15 text-primary'
                  : i < stepIndex
                    ? 'bg-success/15 text-success'
                    : 'bg-base-300/40 text-base-content/40'}`}
            >
              <span className="tabular-nums">{i + 1}</span>
              <span className="hidden sm:inline">{stepLabel(s)}</span>
            </div>
            {i < STEPS.length - 1 && <div className={`h-px flex-1 ${i < stepIndex ? 'bg-success/40' : 'bg-base-300/60'}`} />}
          </div>
        ))}
      </div>

      {/* ── Step 1 · Personal ── */}
      {step === 'personal' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-personal`}>
          <div className="field">
            <label className="label-text">
              {fieldIcon('lucide:user')}
              {t('employees.fullName')} *
            </label>
            <input
              type="text"
              value={value.name}
              onChange={e => onChange({ ...value, name: e.target.value })}
              placeholder={t('employees.namePlaceholder') || 'Enter employee name'}
              className={inputCls}
              autoFocus
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:calendar')}
                {t('employees.dateOfBirth') || 'Date of birth'}
              </label>
              <input
                type="date"
                value={value.date_of_birth || ''}
                onChange={e => onChange({ ...value, date_of_birth: e.target.value || null })}
                className={inputCls}
              />
            </div>
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:credit-card')}
                {t('employees.nationalId') || 'National ID'}
              </label>
              <input
                type="text"
                value={value.national_id || ''}
                onChange={e => onChange({ ...value, national_id: e.target.value || null })}
                placeholder="CNIC / SSN"
                className={inputCls}
              />
            </div>
          </div>
          <div className="field">
            <label className="label-text">
              {fieldIcon('lucide:phone-call')}
              {t('employees.emergencyContact') || 'Emergency contact'}
            </label>
            <input
              type="tel"
              value={value.emergency_contact || ''}
              onChange={e => onChange({ ...value, emergency_contact: e.target.value || null })}
              placeholder={t('employees.emergencyContactPlaceholder') || 'Name · phone'}
              className={inputCls}
            />
          </div>
        </div>
      )}

      {/* ── Step 2 · Contact ── */}
      {step === 'contact' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-contact`}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:phone')}
                {t('employees.phone')}
              </label>
              <input
                type="tel"
                value={value.phone || ''}
                onChange={e => onChange({ ...value, phone: e.target.value || null })}
                placeholder="03XX-XXXXXXX"
                className={inputCls}
              />
            </div>
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:mail')}
                {t('employees.email')}
              </label>
              <input
                type="email"
                value={value.email || ''}
                onChange={e => onChange({ ...value, email: e.target.value || null })}
                placeholder={t('employees.email')}
                className={inputCls}
              />
            </div>
          </div>
          <div className="field">
            <label className="label-text">
              {fieldIcon('lucide:map-pin')}
              {t('employees.address') || 'Address'}
            </label>
            <textarea
              value={value.address || ''}
              onChange={e => onChange({ ...value, address: e.target.value || null })}
              placeholder={t('employees.addressPlaceholder') || 'Street, city'}
              rows={2}
              className="textarea w-full text-sm"
            />
          </div>
          <div className="field">
            <label className="label-text">
              {fieldIcon('lucide:sticky-note')}
              {t('employees.notes') || 'Notes'}
            </label>
            <textarea
              value={value.notes || ''}
              onChange={e => onChange({ ...value, notes: e.target.value || null })}
              placeholder={t('employees.notesPlaceholder') || 'Uniform size, allergies, preferences…'}
              rows={2}
              className="textarea w-full text-sm"
            />
          </div>
        </div>
      )}

      {/* ── Step 3 · Role & employment ── */}
      {step === 'role' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-role`}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:briefcase')}
                {t('employees.employeeType')} *
              </label>
              <select
                value={value.employee_type_id}
                onChange={e => onChange({ ...value, employee_type_id: Number(e.target.value) })}
                className="select w-full h-9 text-sm"
              >
                <option value={0}>{t('employees.selectType')}</option>
                {visibleTypes.map(et => (
                  <option key={et.id} value={et.id}>{et.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:calendar-plus')}
                {t('employees.joinedDate') || 'Joined date'}
              </label>
              <input
                type="date"
                value={value.joined_at || ''}
                onChange={e => onChange({ ...value, joined_at: e.target.value || null })}
                className={inputCls}
              />
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-xl bg-primary/5 border border-primary/15 px-3 py-2.5 text-xs text-base-content/70">
            <span className={iconClass('lucide:shield-check', 'w-4 h-4 text-primary shrink-0 mt-0.5')} />
            <span>{t('employees.roleHint') || 'The employee type is their role — manage detailed permissions in Roles.'}</span>
          </div>
        </div>
      )}

      {/* ── Step 4 · Salary & payroll ── */}
      {step === 'salary' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-salary`}>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:wallet')}
                {t('employees.monthlySalary')} *
              </label>
              <input
                type="number"
                step="1000"
                min="0"
                value={value.salary}
                onChange={e => onChange({ ...value, salary: Number(e.target.value) })}
                placeholder="0"
                className={inputCls}
              />
            </div>
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:repeat')}
                {t('employees.payFrequency') || 'Pay frequency'}
              </label>
              <select
                value={value.pay_frequency || 'monthly'}
                onChange={e => onChange({ ...value, pay_frequency: e.target.value })}
                className="select w-full h-9 text-sm"
              >
                <option value="monthly">{t('employees.payFrequencyMonthly') || 'Monthly'}</option>
                <option value="hourly">{t('employees.payFrequencyHourly') || 'Hourly'}</option>
              </select>
            </div>
            {(value.pay_frequency || 'monthly') === 'hourly' && (
              <div className="field">
                <label className="label-text">
                  {fieldIcon('lucide:clock')}
                  {t('employees.hourlyRate') || 'Hourly rate'} *
                </label>
                <input
                  type="number"
                  step="50"
                  min="0"
                  value={value.hourly_rate ?? 0}
                  onChange={e => onChange({ ...value, hourly_rate: Number(e.target.value) })}
                  placeholder="0"
                  className={inputCls}
                />
              </div>
            )}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:landmark')}
                {t('employees.bankName') || 'Bank name'}
              </label>
              <input
                type="text"
                value={value.bank_name || ''}
                onChange={e => onChange({ ...value, bank_name: e.target.value || null })}
                placeholder={t('employees.bankNamePlaceholder') || 'e.g. HBL'}
                className={inputCls}
              />
            </div>
            <div className="field">
              <label className="label-text">
                {fieldIcon('lucide:credit-card')}
                {t('employees.bankAccount') || 'Bank account'}
              </label>
              <input
                type="text"
                value={value.bank_account || ''}
                onChange={e => onChange({ ...value, bank_account: e.target.value || null })}
                placeholder="IBAN / account no."
                className={inputCls}
              />
            </div>
          </div>
          <div className="field">
            <label className="label-text">
              {fieldIcon('lucide:hash')}
              {t('employees.taxNumber') || 'Tax number'}
            </label>
            <input
              type="text"
              value={value.tax_number || ''}
              onChange={e => onChange({ ...value, tax_number: e.target.value || null })}
              placeholder="NTN / tax ID"
              className={inputCls}
            />
          </div>
          {/* Payroll preview */}
          <div className="rounded-xl bg-base-200/60 border border-base-300/50 px-3.5 py-3 flex items-center justify-between">
            <span className="text-xs font-semibold text-base-content/70">
              {t('employees.payrollPreview') || 'Payroll preview'}
            </span>
            <span className="text-sm font-bold text-primary tabular-nums">
              {(value.pay_frequency || 'monthly') === 'hourly'
                ? `${(value.hourly_rate ?? 0) * 160} / ${t('employees.perMonth') || 'mo'}`
                : `${value.salary} / ${t('employees.perMonth') || 'mo'}`}
            </span>
          </div>
        </div>
      )}
    </Modal>
  );
}
