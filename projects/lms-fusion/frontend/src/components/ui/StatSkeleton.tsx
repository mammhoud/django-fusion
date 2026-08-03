'use client';

export interface StatSkeletonProps {
  /** Pulse size — md (h-7 w-16, default) or lg (h-9 w-16). */
  size?: 'md' | 'lg';
  /** Center horizontally with mx-auto (for centered card layouts). */
  center?: boolean;
  className?: string;
}

const SIZES = {
  md: 'h-7 w-16',
  lg: 'h-9 w-16',
} as const;

/**
 * Small pulse placeholder for stat values while their API data is loading.
 *
 * Usage:
 *   <StatSkeleton />                          // inline stat value (dashboards)
 *   <StatSkeleton size="lg" center />         // centered hero stat (about-us)
 */
export default function StatSkeleton({
  size = 'md',
  center = false,
  className = '',
}: StatSkeletonProps) {
  return (
    <span
      className={`${center ? 'block mx-auto' : 'inline-block align-middle'} bg-gray-200 rounded animate-pulse ${SIZES[size]} ${className}`}
      aria-busy="true"
    />
  );
}
