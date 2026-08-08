import { useTranslation } from 'react-i18next';
import { NewEmployeeType } from '../../types';

/**
 * Reusable employee-type form — shared by the Add and Edit employee-type
 * dialogs. Operates on a plain `NewEmployeeType` value object.
 */
export interface EmployeeTypeFormProps {
  value: NewEmployeeType;
  onChange: (next: NewEmployeeType) => void;
  disabled?: boolean;
}

export default function EmployeeTypeForm({
  value,
  onChange,
  disabled = false,
}: EmployeeTypeFormProps) {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-base-content/80 mb-1 text-sm">
          {t('employees.typeName')} *
        </label>
        <input
          type="text"
          value={value.name}
          disabled={disabled}
          onChange={e => onChange({ ...value, name: e.target.value })}
          placeholder={t('employees.typeNamePlaceholder')}
          className="input w-full"
        />
      </div>
      <div>
        <label className="block text-base-content/80 mb-1 text-sm">
          {t('employees.descriptionOptional')}
        </label>
        <textarea
          value={value.description || ''}
          disabled={disabled}
          onChange={e => onChange({ ...value, description: e.target.value || null })}
          placeholder={t('employees.descPlaceholder')}
          rows={3}
          className="textarea w-full resize-none"
        />
      </div>
    </div>
  );
}
