import { useTranslation } from 'react-i18next';

interface BackButtonProps {
  onClick: () => void;
  disabled?: boolean;
  text?: string;
  /**
   * Breadcrumb trail — e.g. ['Home', 'Settings'] — rendered as a compact
   * "‹ Home / Settings" style navigation chain. When provided, replaces the
   * plain `text` label so the button reads as breadcrumbs back to where the
   * user navigated from.
   */
  breadcrumb?: string[];
  /** Hover tooltip text — e.g. "Back to the page you came from" */
  tooltip?: string;
}

export default function BackButton({
  onClick,
  disabled = false,
  text,
  breadcrumb,
  tooltip,
}: BackButtonProps) {
  const { t } = useTranslation();
  const displayText = text || t('common.back');
  const showBreadcrumb = !!breadcrumb && breadcrumb.length > 0;

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      data-tooltip={tooltip}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg min-w-[120px] justify-center
        bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 font-medium text-sm
        disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.96] transition-all`}
    >
      {disabled ? (
        <>
          <div className="w-4 h-4 border-2 border-slate-500 dark:border-slate-300 border-t-transparent rounded-full shrink-0 animate-spin" />
          <span>{t('common.loading')}</span>
        </>
      ) : showBreadcrumb ? (
        <>
          <span className="ri-arrow-left-line ri-16px rtl:scale-x-[-1] shrink-0" />
          <span className="flex items-center gap-1 text-xs truncate">
            {breadcrumb!.map((segment, i) => (
              <span key={i} className="flex items-center gap-1 min-w-0">
                {i > 0 && (
                  <span className="ri-arrow-right-s-line ri-12px text-base-content/40 rtl:rotate-180 shrink-0" />
                )}
                <span className={`truncate ${i === breadcrumb!.length - 1 ? 'font-semibold' : 'text-base-content/60'}`}>
                  {segment}
                </span>
              </span>
            ))}
          </span>
        </>
      ) : (
        <>
          <span className="ri-arrow-left-line ri-16px rtl:scale-x-[-1] shrink-0" />
          <span>{displayText}</span>
        </>
      )}
    </button>
  );
}
