import { useTranslation } from 'react-i18next';
import { NewEmployee, EmployeeType } from '../../types';
import { iconClass } from '../../lib/icons';

/**
 * Reusable employee form — the same field set used by both the Add and the
 * Edit employee dialogs. Works on a plain `NewEmployee` value object so the
 * page owns the state and decides how to persist it.
 *
 * Styled with the shared CRUD form conventions (`field` / `label-text` /
 * `helper-text` + leading icons) so it matches the other record forms
 * (products, categories, notes, …).
 */
export interface EmployeeFormProps {
  value: NewEmployee;
  onChange: (next: NewEmployee) => void;
  employeeTypes: EmployeeType[];
  /**
   * Keep the currently assigned (possibly inactive) type in the select.
   * Needed when editing so an employee's existing type stays selectable.
   */
  includeInactiveTypes?: boolean;
  disabled?: boolean;
}

export default function EmployeeForm({
  value,
  onChange,
  employeeTypes,
  includeInactiveTypes = false,
  disabled = false,
}: EmployeeFormProps) {
  const { t } = useTranslation();

  const visibleTypes = employeeTypes.filter(
    et => et.is_active || (includeInactiveTypes && et.id === value.employee_type_id),
  );

  return (
    <div className="space-y-4">
      <div className="field">
        <label className="label-text">
          <span className={iconClass('lucide:user', 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />
          {t('employees.fullName')} *
        </label>
        <input
          type="text"
          value={value.name}
          disabled={disabled}
          onChange={e => onChange({ ...value, name: e.target.value })}
          placeholder={t('employees.namePlaceholder') || 'Enter employee name'}
          className="input w-full h-9 text-sm"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="field">
          <label className="label-text">
            <span className={iconClass('lucide:phone', 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />
            {t('employees.phone')}
          </label>
          <input
            type="tel"
            value={value.phone || ''}
            disabled={disabled}
            onChange={e => onChange({ ...value, phone: e.target.value || null })}
            placeholder="03XX-XXXXXXX"
            className="input w-full h-9 text-sm"
          />
        </div>
        <div className="field">
          <label className="label-text">
            <span className={iconClass('lucide:mail', 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />
            {t('employees.email')}
          </label>
          <input
            type="email"
            value={value.email || ''}
            disabled={disabled}
            onChange={e => onChange({ ...value, email: e.target.value || null })}
            placeholder={t('employees.email')}
            className="input w-full h-9 text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="field">
          <label className="label-text">
            <span className={iconClass('lucide:briefcase', 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />
            {t('employees.employeeType')} *
          </label>
          <select
            value={value.employee_type_id}
            disabled={disabled}
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
            <span className={iconClass('lucide:wallet', 'w-3.5 h-3.5 inline-block mr-1.5 text-primary/70')} />
            {t('employees.monthlySalary')} *
          </label>
          <input
            type="number"
            step="1000"
            min="0"
            value={value.salary}
            disabled={disabled}
            onChange={e => onChange({ ...value, salary: Number(e.target.value) })}
            placeholder="0"
            className="input w-full h-9 text-sm"
          />
        </div>
      </div>
    </div>
  );
}
