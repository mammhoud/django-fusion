import { useTranslation } from 'react-i18next';
import { NewEmployee, EmployeeType } from '../../types';

/**
 * Reusable employee form — the same field set used by both the Add and the
 * Edit employee dialogs. Works on a plain `NewEmployee` value object so the
 * page owns the state and decides how to persist it.
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
      <div>
        <label className="block text-base-content/80 mb-1 text-sm">
          {t('employees.fullName')} *
        </label>
        <input
          type="text"
          value={value.name}
          disabled={disabled}
          onChange={e => onChange({ ...value, name: e.target.value })}
          placeholder={t('employees.namePlaceholder') || 'Enter employee name'}
          className="input w-full"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">
            {t('employees.phone')}
          </label>
          <input
            type="tel"
            value={value.phone || ''}
            disabled={disabled}
            onChange={e => onChange({ ...value, phone: e.target.value || null })}
            placeholder="03XX-XXXXXXX"
            className="input w-full"
          />
        </div>
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">
            {t('employees.email')}
          </label>
          <input
            type="email"
            value={value.email || ''}
            disabled={disabled}
            onChange={e => onChange({ ...value, email: e.target.value || null })}
            placeholder={t('employees.email')}
            className="input w-full"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">
            {t('employees.employeeType')} *
          </label>
          <select
            value={value.employee_type_id}
            disabled={disabled}
            onChange={e => onChange({ ...value, employee_type_id: Number(e.target.value) })}
            className="select w-full"
          >
            <option value={0}>{t('employees.selectType')}</option>
            {visibleTypes.map(et => (
              <option key={et.id} value={et.id}>{et.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">
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
            className="input w-full"
          />
        </div>
      </div>
    </div>
  );
}
