import { motion } from 'framer-motion';
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
};

/** Resolve a color value to a semantic text-* class. */
function resolveColor(color?: string): string {
  if (!color) return 'text-primary';
  // Direct semantic class (already starts with text-)
  if (color.startsWith('text-')) return color;
  // Direct semantic name (e.g. 'primary', 'info')
  if (!color.startsWith('from-')) return `text-${color}`;
  // Legacy gradient name
  return GRADIENT_TO_SEMANTIC[color] || 'text-primary';
}

export interface StatCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  /** Stat label (shown in stat-title) */
  title: string;
  /** Primary value (shown in stat-value) */
  value: string | number;
  /** Optional description / delta (shown in stat-desc) */
  desc?: string;
  /** Optional icon node (shown in stat-figure) */
  icon?: React.ReactNode;
  /** Color theme: gradient name ('from-teal-500...'), semantic name ('primary'), or text class ('text-info'). Default: 'primary' */
  color?: string;
  /** Show a left border indicator via border-l-4 */
  border?: boolean;
  /** Enable entrance animation (motion.div) */
  animated?: boolean;
  /** Optional click handler — makes the card interactive with cursor-pointer and hover effects */
  onClick?: () => void;
  /** Optional click handler for the desc/delta text — makes it clickable separately from the card */
  onDescClick?: () => void;
  /** Optional sparkline data — renders a tiny Recharts AreaChart in the stat-figure area */
  sparklineData?: { value: number }[];
}

/**
 * StatCard — FlyonUI `.stat` component wrapper.
 *
 * Renders a theme-adaptive KPI card with optional icon, descriptive label,
 * value, and delta text. All colors use the active FlyonUI theme's palette.
 *
 * @example
 * <StatCard
 *   title="Today Revenue"
 *   value="$1,245.00"
 *   icon={<span className="icon-[tabler--moneybag] w-6 h-6" />}
 *   color="from-teal-500 to-emerald-600"
 * />
 */
export default function StatCard({
  title,
  value,
  desc,
  icon,
  color,
  border,
  animated = true,
  onClick,
  onDescClick,
  sparklineData,
  className = ''
}: StatCardProps) {
  const semanticColor = resolveColor(color);
  const borderClass = border ? ` border-l-4 border-${semanticColor.replace('text-', '')} rtl:border-l-0 rtl:border-r-4` : '';
  const clickableClass = onClick ? ' cursor-pointer hover:bg-white/10 transition-colors duration-200' : '';
  const classes = `stat${borderClass}${clickableClass} ${className}`.trim();

  const sparkColor = semanticColor.replace('text-', '');
  // Only render sparkline when color resolves to a known FlyonUI CSS variable
  const SEMANTIC_COLORS = new Set(['primary', 'secondary', 'info', 'success', 'warning', 'error', 'neutral']);
  const hasValidSparkColor = SEMANTIC_COLORS.has(sparkColor);

  const content = (
    <>
      {(icon || sparklineData) && (
        <div className={`stat-figure ${semanticColor}`}>
          {icon}
          {sparklineData && sparklineData.length > 0 && hasValidSparkColor && (
            <div className="w-20 h-10 mt-1">
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
      <div className="stat-title">{title}</div>
      <div className={`stat-value ${semanticColor}`}>{value}</div>
      {desc && (
        <div
          className={`stat-desc ${onDescClick ? 'cursor-pointer hover:text-primary hover:underline transition-colors' : ''}`}
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
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={classes}
        onClick={onClick}
      >
        {content}
      </motion.div>
    );
  }

  return (
    <div className={classes} onClick={onClick}>
      {content}
    </div>
  );
}
