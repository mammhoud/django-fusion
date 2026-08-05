import { useTranslation } from 'react-i18next';
import type { NoteStep } from '../../types';

interface PrepStepsEditorProps {
  value: NoteStep[];
  onChange: (steps: NoteStep[]) => void;
  /** Compact mode — for inline quick-add forms (smaller paddings/buttons). */
  compact?: boolean;
}

/**
 * Structured editor for "preparation" notes — a dynamic list of steps where
 * each step has a title + optional details. Used by the Notes page form and by
 * the quick-add note forms on KDS / Sale.
 */
export default function PrepStepsEditor({ value, onChange, compact = false }: PrepStepsEditorProps) {
  const { t } = useTranslation();

  const updateStep = (index: number, patch: Partial<NoteStep>) => {
    onChange(value.map((s, i) => (i === index ? { ...s, ...patch } : s)));
  };

  const addStep = () => {
    onChange([...value, { title: '', details: '' }]);
  };

  const removeStep = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const moveStep = (index: number, dir: -1 | 1) => {
    const target = index + dir;
    if (target < 0 || target >= value.length) return;
    const next = [...value];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-base-content/60 uppercase tracking-wider flex items-center gap-1.5">
          <span className="ri-check-double-line ri-14px" />
          {t('notes.stepsTitle') || 'Preparation Steps'}
        </span>
        <button
          type="button"
          onClick={addStep}
          className="btn btn-ghost btn-xs gap-1 text-primary hover:bg-primary/10"
        >
          <span className="ri-add-line ri-14px" />
          {t('notes.addStep') || 'Add step'}
        </button>
      </div>

      {value.length === 0 ? (
        <p className="text-xs text-base-content/40 italic py-2">
          {t('notes.noSteps') || 'No steps yet. Add the first preparation step.'}
        </p>
      ) : (
        <div className="space-y-2">
          {value.map((step, index) => (
            <div
              key={index}
              className="rounded-lg border border-base-300/40 bg-base-200/30 p-2.5 space-y-2 group/step"
            >
              <div className="flex items-center gap-1.5">
                <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-[10px] font-bold flex items-center justify-center shrink-0">
                  {index + 1}
                </span>
                <input
                  type="text"
                  value={step.title}
                  onChange={e => updateStep(index, { title: e.target.value })}
                  placeholder={t('notes.stepTitlePlaceholder') || `Step ${index + 1} title...`}
                  className="input w-full text-sm"
                  aria-label={`Step ${index + 1} title`}
                />
                <div className="flex items-center gap-0.5 shrink-0">
                  <button
                    type="button"
                    onClick={() => moveStep(index, -1)}
                    disabled={index === 0}
                    className="p-1 rounded-md text-base-content/40 hover:text-base-content hover:bg-base-300/40 disabled:opacity-25 transition-colors"
                    title="Move up"
                  >
                    <span className="ri-arrow-up-s-line ri-14px" />
                  </button>
                  <button
                    type="button"
                    onClick={() => moveStep(index, 1)}
                    disabled={index === value.length - 1}
                    className="p-1 rounded-md text-base-content/40 hover:text-base-content hover:bg-base-300/40 disabled:opacity-25 transition-colors"
                    title="Move down"
                  >
                    <span className="ri-arrow-down-s-line ri-14px" />
                  </button>
                  <button
                    type="button"
                    onClick={() => removeStep(index)}
                    className="p-1 rounded-md text-base-content/40 hover:text-error hover:bg-error/10 transition-colors"
                    title="Remove step"
                  >
                    <span className="ri-delete-bin-line ri-14px" />
                  </button>
                </div>
              </div>
              <textarea
                value={step.details || ''}
                onChange={e => updateStep(index, { details: e.target.value })}
                placeholder={t('notes.stepDetailsPlaceholder') || 'Details: time, temperature, technique...'}
                rows={compact ? 1 : 2}
                className="textarea w-full text-xs leading-relaxed resize-y min-h-[28px]"
                aria-label={`Step ${index + 1} details`}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
