import { type HTMLAttributes } from 'react';
import { Area, AreaChart, ResponsiveContainer } from 'recharts';

// ── Color mapping ──
// Maps legacy gradient color names to FlyonUI semantic color classes.
// StatCard accepts both gradient strings (backward-compat) and direct semantic names.

const GRADIENT_TO_SEMANTIC: Record<string, string> = {
  'from-teal-500 to-emerald-600': 'text-primary',
  'from-blue-500 to-indigo-600': 'text-info',
  'from-orange-500 to-amber-600': 'text-warning',
  'from-purple-500 to-violet-600': 'text-secondary',
  'from-slate-400 to-slate-500': 'text-neutral',
  'from-red-500 to-rose-600': 'text-error',
  'from-emerald-500 to-teal-600': 'text-success',
  'from-green-500 to-emerald-600': 'text-success',
  'from-indigo-500 to-purple-600': 'text-secondary',
  'from-blue-500 to-cyan-600': 'text-info',
};

/** Recognized FlyonUI semantic color tokens — used for sparkline + border CSS var resolution. */
const SEMANTIC_COLORS = new Set([
  'primary', 'secondary', 'accent', 'neutral',
  'info', 'success', 'warning', 'error',
]);

/** Resolve a color value to a semantic text-* class. */
function resolveColor(color?: string): string {
  if (!color) return 'text-primary';
  // Direct semantic class (already starts with text-)
  if (color.startsWith('text-')) return color;
  // Direct semantic name (e.g. 'primary', 'info', 'accent')
  if (!color.startsWith('from-')) return `text-${color}`;
  // Legacy gradient name
  return GRADIENT_TO_SEMANTIC[color] || 'text-primary';
}

// ── Discriminated union: when loading=true, title+value are optional ──
// This lets <StatCard loading /> work without placeholder props.
type StatCardBase = Omit<HTMLAttributes<HTMLDivElement>, 'title'> & {
  desc?: string;
  icon?: React.ReactNode;
  /** Color theme: gradient name, semantic name, or text class. Default: 'primary' */
  color?: string;
  /** Show a left border indicator via CSS variable border-l-4. */
  border?: boolean;
  /** Enable entrance animation. */
  animated?: boolean;
  /** Optional click handler — makes the card interactive with cursor-pointer and hover effects. */
  onClick?: () => void;
  /** Optional click handler for the desc/delta text. */
  onDescClick?: () => void;
  /** Optional sparkline data — renders a tiny Recharts AreaChart in the stat-figure area. */
  sparklineData?: { value: number }[];
  /** Compact mode — reduced padding and font sizes for denser grids. */
  compact?: boolean;
};

type StatCardLoading = StatCardBase & {
  loading: true;
  title?: string;
  value?: string | number;
};

type StatCardNormal = StatCardBase & {
  loading?: false;
  /** Stat label (shown in stat-title) */
  title: string;
  /** Primary value (shown in stat-value) */
  value: string | number;
};

export type StatCardProps = StatCardLoading | StatCardNormal;

/**
 * StatCard — FlyonUI `.stat` component wrapper.
 *
 * Renders a theme-adaptive KPI card with optional icon, descriptive label,
 * value, and delta text. All colors use the active FlyonUI theme's palette.
 *
 * Supports compact mode, skeleton loading, CSS-variable border-left,
 * and all FlyonUI semantic color tokens (primary, secondary, accent, neutral,
 * info, success, warning, error).
 *
 * @example
 * <StatCard
 *   title="Today Revenue"
 *   value="$1,245.00"
 *   icon={<span className="icon-[tabler--moneybag] w-6 h-6" />}
 *   color="primary"
 * />
 */
export default function StatCard(props: StatCardProps) {
  const { animated = true, compact = false, className = '' } = props;

  // ── Skeleton loading state — early return so rest of the function
  //     sees narrowed StatCardNormal with required title/value. ──
  if (props.loading) {
    const skeleton = (
      <div className={`stat bg-white/40 dark:bg-white/5 backdrop-blur-sm border border-white/20 animate-pulse ${compact ? 'p-3' : ''} ${className}`.trim()}>
        <div className={`stat-title ${compact ? 'mb-0.5' : ''}`}>
          <div className={`rounded bg-base-300/50 ${compact ? 'h-2 w-12' : 'h-3 w-16'}`} />
        </div>
        <div className="stat-value">
          <div className={`rounded bg-base-300/50 mt-1 ${compact ? 'h-5 w-14' : 'h-7 w-20'}`} />
        </div>
        <div className="stat-desc">
          <div className={`rounded bg-base-300/50 mt-1 ${compact ? 'h-2 w-16' : 'h-2.5 w-24'}`} />
        </div>
      </div>
    );

    if (animated) {
      return (
        <div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {skeleton}
        </div>
      );
    }
    return skeleton;
  }

  // After the loading early-return, TypeScript narrows to StatCardNormal.
  const { title, value, desc, icon, color, border, onClick, onDescClick, sparklineData } = props;

  const semanticColor = resolveColor(color);
  const sparkColor = semanticColor.replace('text-', '');
  const hasValidSparkColor = SEMANTIC_COLORS.has(sparkColor);

  const clickableClass = onClick ? ' cursor-pointer hover:bg-white/10 transition-colors duration-200' : '';

  // ── Border-left via CSS variable ──
  // Uses var(--color-*) so the border tracks the active FlyonUI theme palette.
  // borderColor sets all four sides so RTL rtl:border-r-[4px] inherits the correct color.
  const borderStyle: React.CSSProperties | undefined = border && hasValidSparkColor
    ? { borderLeftWidth: '4px', borderColor: `var(--color-${sparkColor})` }
    : border
      ? { borderLeftWidth: '4px', borderColor: 'var(--color-primary)' }
      : undefined;

  // RTL-aware border — swap left→right in RTL via className
  const borderClass = border ? ' rtl:border-l-0 rtl:border-r-[4px]' : '';

  // ── Compact classes ──
  const compactTitleClass = compact ? 'text-[11px] mb-0.5' : '';
  const compactValueClass = compact ? 'text-lg' : '';
  const compactDescClass = compact ? 'text-[10px]' : '';
  const compactPaddingClass = compact ? 'p-3' : '';

  const classes = [
    'stat',
    borderClass,
    clickableClass,
    compactPaddingClass,
    className,
  ].filter(Boolean).join(' ').trim();

  const content = (
    <>
      {(icon || sparklineData) && (
        <div className={`stat-figure ${semanticColor} ${compact ? 'top-2 right-2' : ''}`}>
          {icon}
          {sparklineData && sparklineData.length > 0 && hasValidSparkColor && (
            <div className={`${compact ? 'w-14 h-7 mt-0.5' : 'w-20 h-10 mt-1'}`}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sparklineData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                  <defs>
                    <linearGradient id={`spark-fill-${title.replace(/\s+/g, '-')}`} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={`var(--color-${sparkColor})`} stopOpacity={0.3} />
                      <stop offset="95%" stopColor={`var(--color-${sparkColor})`} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={`var(--color-${sparkColor})`}
                    strokeWidth={1.5}
                    fill={`url(#spark-fill-${title.replace(/\s+/g, '-')})`}
                    dot={false}
                    activeDot={false}
                    isAnimationActive={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
      <div className={`stat-title ${compactTitleClass}`.trim()}>{title}</div>
      <div className={`stat-value ${semanticColor} ${compactValueClass}`.trim()}>{value}</div>
      {desc && (
        <div
          className={`stat-desc ${semanticColor}/70 ${compactDescClass} ${onDescClick ? 'cursor-pointer hover:text-primary hover:underline transition-colors' : ''}`.trim()}
          onClick={(e) => {
            if (onDescClick) {
              e.stopPropagation();
              onDescClick();
            }
          }}
          role={onDescClick ? 'button' : undefined}
          tabIndex={onDescClick ? 0 : undefined}
          onKeyDown={(e) => {
            if (onDescClick && (e.key === 'Enter' || e.key === ' ')) {
              e.preventDefault();
              e.stopPropagation();
              onDescClick();
            }
          }}
        >
          {desc}
        </div>
      )}
    </>
  );

  if (animated) {
    return (
      <div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={classes}
        style={borderStyle}
        onClick={onClick}
      >
        {content}
      </div>
    );
  }

  return (
    <div className={classes} style={borderStyle} onClick={onClick}>
      {content}
    </div>
  );
}
