import { useEffect, useState } from 'react';
import Modal from '../ui/Modal';
import { useTranslation } from 'react-i18next';
import { NewEmployee, EmployeeType } from '../../types';
import { iconClass } from '../../lib/icons';

export interface EmployeeWizardProps {
  isOpen: boolean;
  value: NewEmployee;
  onChange: (next: NewEmployee) => void;
  employeeTypes: EmployeeType[];
  includeInactiveTypes?: boolean;
  isEditing: boolean;
  submitLabel: string;
  cancelLabel?: string;
  isSubmitting?: boolean;
  onClose: () => void;
  onSubmit: () => void;
  contentTestId?: string;
}

const STEPS = ['personal', 'contact', 'role'] as const;
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

  useEffect(() => {
    if (isOpen) setStep('personal');
  }, [isOpen]);

  const visibleTypes = employeeTypes.filter(
    (employeeType) => employeeType.is_active || (includeInactiveTypes && employeeType.id === value.employee_type_id),
  );

  const stepValid = (): boolean => {
    switch (step) {
      case 'personal': return value.name.trim().length > 0;
      case 'contact': return true;
      case 'role': return isEditing || value.employee_type_id > 0;
    }
  };

  const stepIndex = STEPS.indexOf(step);
  const isLastStep = step === 'role';
  const next = () => {
    if (step === 'personal') setStep('contact');
    else if (step === 'contact') setStep('role');
  };
  const back = () => {
    if (step === 'contact') setStep('personal');
    else if (step === 'role') setStep('contact');
  };
  const stepLabel = (currentStep: Step) => {
    switch (currentStep) {
      case 'personal': return t('employees.stepPersonal') || 'Personal';
      case 'contact': return t('employees.stepContact') || 'Contact';
      case 'role': return t('employees.stepRole') || 'Role';
    }
  };
  const fieldIcon = (icon: string) => <span className={iconClass(icon, 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />;
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
          <button onClick={onClose} disabled={isSubmitting} className="btn btn-ghost flex-1 disabled:opacity-50">
            {cancelLabel ?? t('common.cancel')}
          </button>
          {stepIndex > 0 && (
            <button onClick={back} disabled={isSubmitting} className="btn btn-ghost flex-1 disabled:opacity-50">
              <span className="ri-arrow-left-line ri-16px" /> {t('employees.back') || 'Back'}
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
                <><div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />{submitLabel}</>
              ) : (
                <><span className="ri-save-3-line ri-16px" />{submitLabel}</>
              )}
            </button>
          ) : (
            <button onClick={next} disabled={!stepValid() || isSubmitting} className="btn btn-primary flex-1 disabled:opacity-50">
              {t('employees.next') || 'Next'} <span className="ri-arrow-right-line ri-16px" />
            </button>
          )}
        </div>
      }
    >
      <div className="flex items-center gap-2 mb-5">
        {STEPS.map((currentStep, index) => (
          <div key={currentStep} className="flex items-center gap-2 flex-1 min-w-0">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
              index === stepIndex ? 'bg-primary/15 text-primary' : index < stepIndex ? 'bg-success/15 text-success' : 'bg-base-300/40 text-base-content/40'
            }`}>
              <span className="tabular-nums">{index + 1}</span>
              <span className="hidden sm:inline">{stepLabel(currentStep)}</span>
            </div>
            {index < STEPS.length - 1 && <div className={`h-px flex-1 ${index < stepIndex ? 'bg-success/40' : 'bg-base-300/60'}`} />}
          </div>
        ))}
      </div>

      {step === 'personal' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-personal`}>
          <div className="field">
            <label className="label-text">{fieldIcon('lucide:user')}{t('employees.fullName')} *</label>
            <input
              type="text"
              value={value.name}
              onChange={(event) => onChange({ ...value, name: event.target.value })}
              placeholder={t('employees.namePlaceholder') || 'Enter employee name'}
              className={inputCls}
              autoFocus
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">{fieldIcon('lucide:calendar')}{t('employees.dateOfBirth') || 'Date of birth'}</label>
              <input type="date" value={value.date_of_birth || ''} onChange={(event) => onChange({ ...value, date_of_birth: event.target.value || null })} className={inputCls} />
            </div>
            <div className="field">
              <label className="label-text">{fieldIcon('lucide:credit-card')}{t('employees.nationalId') || 'National ID'}</label>
              <input type="text" value={value.national_id || ''} onChange={(event) => onChange({ ...value, national_id: event.target.value || null })} placeholder="CNIC / SSN" className={inputCls} />
            </div>
          </div>
          <div className="field">
            <label className="label-text">{fieldIcon('lucide:phone-call')}{t('employees.emergencyContact') || 'Emergency contact'}</label>
            <input type="tel" value={value.emergency_contact || ''} onChange={(event) => onChange({ ...value, emergency_contact: event.target.value || null })} placeholder={t('employees.emergencyContactPlaceholder') || 'Name · phone'} className={inputCls} />
          </div>
        </div>
      )}

      {step === 'contact' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-contact`}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">{fieldIcon('lucide:phone')}{t('employees.phone')}</label>
              <input type="tel" value={value.phone || ''} onChange={(event) => onChange({ ...value, phone: event.target.value || null })} placeholder="03XX-XXXXXXX" className={inputCls} />
            </div>
            <div className="field">
              <label className="label-text">{fieldIcon('lucide:mail')}{t('employees.email')}</label>
              <input type="email" value={value.email || ''} onChange={(event) => onChange({ ...value, email: event.target.value || null })} placeholder={t('employees.email')} className={inputCls} />
            </div>
          </div>
          <div className="field">
            <label className="label-text">{fieldIcon('lucide:map-pin')}{t('employees.address') || 'Address'}</label>
            <textarea value={value.address || ''} onChange={(event) => onChange({ ...value, address: event.target.value || null })} placeholder={t('employees.addressPlaceholder') || 'Street, city'} rows={2} className="textarea w-full text-sm" />
          </div>
          <div className="field">
            <label className="label-text">{fieldIcon('lucide:sticky-note')}{t('employees.notes') || 'Notes'}</label>
            <textarea value={value.notes || ''} onChange={(event) => onChange({ ...value, notes: event.target.value || null })} placeholder={t('employees.notesPlaceholder') || 'Uniform size, allergies, preferences…'} rows={2} className="textarea w-full text-sm" />
          </div>
        </div>
      )}

      {step === 'role' && (
        <div className="space-y-4" data-testid={`${contentTestId}-step-role`}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className="label-text">{fieldIcon('lucide:briefcase')}{t('employees.employeeType')} *</label>
              <select value={value.employee_type_id} onChange={(event) => onChange({ ...value, employee_type_id: Number(event.target.value) })} className="select w-full h-9 text-sm">
                <option value={0}>{t('employees.selectType')}</option>
                {visibleTypes.map((employeeType) => <option key={employeeType.id} value={employeeType.id}>{employeeType.name}</option>)}
              </select>
            </div>
            <div className="field">
              <label className="label-text">{fieldIcon('lucide:calendar-plus')}{t('employees.joinedDate') || 'Joined date'}</label>
              <input type="date" value={value.joined_at || ''} onChange={(event) => onChange({ ...value, joined_at: event.target.value || null })} className={inputCls} />
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-xl bg-primary/5 border border-primary/15 px-3 py-2.5 text-xs text-base-content/70">
            <span className={iconClass('lucide:shield-check', 'w-4 h-4 text-primary shrink-0 mt-0.5')} />
            <span>{t('employees.roleHint') || 'The employee type is their role — manage detailed permissions in Roles.'}</span>
          </div>
        </div>
      )}
    </Modal>
  );
}
