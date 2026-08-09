import { ReactNode } from 'react';

interface SkeletonBaseProps {
  className?: string;
  children?: ReactNode;
}

function SkeletonBase({ className = '', children }: SkeletonBaseProps) {
  return (
    <div
      className={`animate-pulse bg-base-300/50 rounded ${className}`}
      aria-hidden="true"
    >
      {children}
    </div>
  );
}

interface SkeletonTextProps {
  lines?: number;
  className?: string;
  lineClassName?: string;
}

export function SkeletonText({ lines = 1, className = '', lineClassName = '' }: SkeletonTextProps) {
  return (
    <div className={`space-y-2 ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBase key={i} className={`h-4 w-full ${lineClassName}`} />
      ))}
    </div>
  );
}

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  className?: string;
}

export function SkeletonTable({ rows = 5, columns = 4, className = '' }: SkeletonTableProps) {
  const gridClass = `grid-cols-${columns}`;
  return (
    <div className={`w-full overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700/50 ${className}`} aria-hidden="true">
      {/* Header */}
      <div className={`grid ${gridClass} gap-3 p-4 bg-base-200/50 border-b border-slate-200 dark:border-slate-700/50`}>
        {Array.from({ length: columns }).map((_, i) => (
          <SkeletonBase key={`header-${i}`} className="h-4 w-3/4" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className={`grid ${gridClass} gap-3 p-4 border-b border-slate-100 dark:border-slate-700/30 last:border-b-0`}
        >
          {Array.from({ length: columns }).map((__, colIndex) => (
            <SkeletonBase key={`cell-${rowIndex}-${colIndex}`} className="h-4 w-full" />
          ))}
        </div>
      ))}
    </div>
  );
}

interface SkeletonListProps {
  items?: number;
  className?: string;
}

export function SkeletonList({ items = 5, className = '' }: SkeletonListProps) {
  return (
    <div className={`space-y-3 ${className}`} aria-hidden="true">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-base-200/50">
          <SkeletonBase className="w-10 h-10 rounded-lg shrink-0" />
          <div className="flex-1 space-y-2">
            <SkeletonBase className="h-4 w-1/3" />
            <SkeletonBase className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

interface SkeletonCardProps {
  count?: number;
  className?: string;
}

export function SkeletonCard({ count = 4, className = '' }: SkeletonCardProps) {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`} aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl p-4 bg-base-200/50 space-y-3">
          <SkeletonBase className="h-8 w-8 rounded-lg" />
          <SkeletonBase className="h-5 w-3/4" />
          <SkeletonBase className="h-8 w-1/2" />
        </div>
      ))}
    </div>
  );
}

export default SkeletonBase;
