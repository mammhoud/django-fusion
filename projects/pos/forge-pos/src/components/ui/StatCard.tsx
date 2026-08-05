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
  /** Show a start-edge accent bar via CSS variable (RTL-aware). */
  border?: boolean;
  /** Enable entrance animation. */
  animated?: boolean;
  /** Optional click handler — makes the card interactive with cursor-pointer and hover effects. */
  onClick?: () => void;
  /** Optional click handler for the desc/delta text. */
  onDescClick?: () => void;
  /** Optional sparkline data — renders a tiny Recharts AreaChart as an in-card bottom strip. */
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
 * StatCard — fit-design KPI card.
 *
 * Every element lives inside the card container:
 * - the icon renders in a rounded tinted badge pinned to the top-end corner (inside the card),
 * - the sparkline renders as a subtle full-width strip anchored to the card bottom,
 * - title / value / description truncate (ellipsis) instead of overflowing,
 * - the card root is overflow-hidden with a real card surface.
 *
 * Supports compact mode, skeleton loading, an RTL-aware start-edge accent bar,
 * and all FlyonUI semantic color tokens (primary, secondary, accent, neutral,
 * info, success, warning, error).
 *
 * @example
 * <StatCard
 *   title="Today Revenue"
 *   value="$1,245.00"
 *   icon={<span className="ri-money-dollar-box-line ri-24px" />}
 *   color="primary"
 *   compact
 * />
 */
export default function StatCard(props: StatCardProps) {
  const { animated = true, compact = false, className = '' } = props;

  // ── Card surface (shared by skeleton + content) ──
  const surfaceClass = 'bg-base-100/70 dark:bg-white/5 backdrop-blur-sm border border-base-300/40 dark:border-white/10 rounded-2xl shadow-sm';

  // ── Skeleton loading state — early return so the rest of the function
  //     sees narrowed StatCardNormal with required title/value. ──
  if (props.loading) {
    const skeleton = (
      <div
        className={`stat relative overflow-hidden ${surfaceClass} animate-pulse ${compact ? 'p-3' : 'p-4'} ${className}`.trim()}
      >
        <div className="stat-title">
          <div className={`rounded bg-base-300/50 ${compact ? 'h-2 w-14' : 'h-3 w-20'}`} />
        </div>
        <div className="stat-value">
          <div className={`rounded bg-base-300/50 mt-1.5 ${compact ? 'h-5 w-16' : 'h-8 w-28'}`} />
        </div>
        <div className="stat-desc">
          <div className={`rounded bg-base-300/50 mt-1.5 ${compact ? 'h-2 w-24' : 'h-2.5 w-36'}`} />
        </div>
      </div>
    );

    if (animated) {
      return <div>{skeleton}</div>;
    }
    return skeleton;
  }

  // After the loading early-return, TypeScript narrows to StatCardNormal.
  const { title, value, desc, icon, color, border, onClick, onDescClick, sparklineData } = props;

  const semanticColor = resolveColor(color);
  const sparkColor = semanticColor.replace('text-', '');
  const hasValidSparkColor = SEMANTIC_COLORS.has(sparkColor);
  const hasSparkline = !!sparklineData && sparklineData.length > 0 && hasValidSparkColor;

  const clickableClass = onClick
    ? ' cursor-pointer hover:bg-base-100 dark:hover:bg-white/10 transition-colors duration-200'
    : '';

  // ── Start-edge accent bar via CSS variable (RTL-aware by using inline-start). ──
  // borderInlineStartWidth/Color flip automatically in RTL — no rtl: class juggling needed.
  const borderStyle: React.CSSProperties | undefined = border
    ? {
        borderInlineStartWidth: '4px',
        borderInlineStartColor: `var(--color-${hasValidSparkColor ? sparkColor : 'primary'})`,
      }
    : undefined;

  // ── Compact vs default type scale ──
  const compactTitleClass = compact ? 'text-[11px]' : 'text-xs';
  const compactValueClass = compact ? 'text-lg' : 'text-2xl md:text-3xl';
  const compactDescClass = compact ? 'text-[10px]' : 'text-xs';
  // Reserve the bottom strip space so text never collides with the sparkline.
  const sparkPadClass = hasSparkline ? (compact ? 'pb-8' : 'pb-9') : '';

  const classes = [
    'stat',
    'relative overflow-hidden',
    surfaceClass,
    clickableClass,
    compact ? 'p-3' : 'p-4',
    sparkPadClass,
    className,
  ].filter(Boolean).join(' ').trim();

  // ── Icon badge — pinned inside the card top-end corner, tinted with the accent color ──
  const iconBadge = icon ? (
    <div
      aria-hidden="true"
      className="absolute top-2.5 end-2.5 z-10 w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm"
      style={
        hasValidSparkColor
          ? { backgroundColor: `color-mix(in oklab, var(--color-${sparkColor}) 14%, transparent)` }
          : undefined
      }
    >
      <span className={semanticColor}>{icon}</span>
    </div>
  ) : null;

  // ── Sparkline — subtle full-width strip anchored to the card bottom ──
  const sparkId = `spark-${sparkColor}-${title.replace(/[^a-zA-Z0-9]/g, '-')}`;
  const sparkline = hasSparkline ? (
    <div data-testid="stat-sparkline" className="absolute inset-x-0 bottom-0 h-8 opacity-70 pointer-events-none" aria-hidden="true">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={sparklineData ?? []} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={sparkId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={`var(--color-${sparkColor})`} stopOpacity={0.35} />
              <stop offset="95%" stopColor={`var(--color-${sparkColor})`} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="value"
            stroke={`var(--color-${sparkColor})`}
            strokeWidth={1.5}
            fill={`url(#${sparkId})`}
            dot={false}
            activeDot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  ) : null;

  const content = (
    <>
      {iconBadge}
      <div className={`stat-title ${compactTitleClass} ${icon ? 'pe-12' : ''} truncate min-w-0`}>{title}</div>
      <div className={`stat-value ${semanticColor} ${compactValueClass} truncate min-w-0 tabular-nums`}>{value}</div>
      {desc && (
        <div
          className={`stat-desc ${semanticColor}/70 ${compactDescClass} line-clamp-1 min-w-0 ${onDescClick ? 'cursor-pointer hover:text-primary hover:underline transition-colors' : ''}`.trim()}
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
      {sparkline}
    </>
  );

  return (
    <div className={classes} style={borderStyle} onClick={onClick}>
      {content}
    </div>
  );
}
