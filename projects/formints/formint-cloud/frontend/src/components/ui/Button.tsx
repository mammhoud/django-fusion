import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';

/**
 * Shared Button — wraps FlyonUI's `.btn` primitives with consistent
 * icon↔label gap and opt-in margin utilities so action rows stop
 * hand-rolling `gap-2` / `ml-*` per page.
 *
 * ```tsx
 * <Button variant="primary" size="md" gap="md" onClick={save} iconStart={<span className="ri-save-line" />}>
 *   Save
 * </Button>
 * <Button variant="ghost" margin="start" onClick={cancel}>Cancel</Button>
 * ```
 */
export type ButtonVariant =
  | 'primary' | 'secondary' | 'accent' | 'neutral'
  | 'info' | 'success' | 'warning' | 'error'
  | 'ghost' | 'outline' | 'soft' | 'text';

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/** Icon↔label spacing scale (Tailwind gap utilities). */
export type ButtonGap = 'none' | 'xs' | 'sm' | 'md' | 'lg';

/** Margin placement — applies a margin on one side so buttons in a row
 *  don't need manual `ml-2` / `mr-2` per call site. */
export type ButtonMargin = 'none' | 'start' | 'end' | 'top' | 'bottom' | 'block';

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  accent: 'btn-accent',
  neutral: 'btn-neutral',
  info: 'btn-info',
  success: 'btn-success',
  warning: 'btn-warning',
  error: 'btn-error',
  ghost: 'btn-ghost',
  outline: 'btn-outline',
  soft: 'btn-soft',
  text: 'btn-text',
};

const SIZE_CLASS: Record<ButtonSize, string> = {
  xs: 'btn-xs',
  sm: 'btn-sm',
  md: '',
  lg: 'btn-lg',
  xl: 'btn-xl',
};

const GAP_CLASS: Record<ButtonGap, string> = {
  none: '',
  xs: 'gap-1',
  sm: 'gap-1.5',
  md: 'gap-2',
  lg: 'gap-3',
};

/** Logical start/end margins — flip automatically in RTL via rtl: variants. */
const MARGIN_CLASS: Record<ButtonMargin, string> = {
  none: '',
  start: 'ms-2 rtl:ms-0 rtl:me-2',
  end: 'me-2 rtl:me-0 rtl:ms-2',
  top: 'mt-2',
  bottom: 'mb-2',
  block: 'my-2',
};

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Spacing between icon(s) and label. Defaults to `md` (gap-2). */
  gap?: ButtonGap;
  /** Optional margin placement for action rows (RTL-aware). */
  margin?: ButtonMargin;
  /** Leading icon node. */
  iconStart?: ReactNode;
  /** Trailing icon node. */
  iconEnd?: ReactNode;
  /** Full-width (btn-block). */
  block?: boolean;
  /** Square / circle shape (icon-only buttons). */
  shape?: 'square' | 'circle';
  /** In-button spinner + disabled. */
  loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = 'primary',
    size = 'md',
    gap = 'md',
    margin = 'none',
    iconStart,
    iconEnd,
    block = false,
    shape,
    loading = false,
    className = '',
    children,
    disabled,
    type = 'button',
    ...rest
  },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      className={[
        'btn',
        VARIANT_CLASS[variant],
        SIZE_CLASS[size],
        GAP_CLASS[gap],
        MARGIN_CLASS[margin],
        block ? 'btn-block' : '',
        shape === 'square' ? 'btn-square' : '',
        shape === 'circle' ? 'btn-circle' : '',
        loading ? 'pointer-events-none opacity-80' : '',
        className,
      ].filter(Boolean).join(' ')}
      {...rest}
    >
      {loading ? <Spinner /> : iconStart}
      {children}
      {!loading && iconEnd}
    </button>
  );
});

function Spinner() {
  return (
    <span
      className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin shrink-0"
      aria-hidden="true"
    />
  );
}

export default Button;
