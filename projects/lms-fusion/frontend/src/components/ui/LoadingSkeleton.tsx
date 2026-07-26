'use client';

interface LoadingSkeletonProps {
  variant?: 'card' | 'list' | 'table' | 'detail' | 'profile' | 'text';
  count?: number;
  className?: string;
}

/**
 * Reusable loading skeleton for consistent loading states across all pages.
 *
 * Variants:
 *  - card:    Card grid skeleton (image + title + description)
 *  - list:    List item skeleton (icon/avatar + text)
 *  - table:   Table row skeleton
 *  - detail:  Detail page skeleton (title + content)
 *  - profile: Profile/avatar skeleton
 *  - text:    Simple text block skeleton
 */
export default function LoadingSkeleton({
  variant = 'card',
  count = 1,
  className = '',
}: LoadingSkeletonProps) {
  const items = Array.from({ length: count }, (_, i) => i);

  const renderItem = (key: number) => {
    switch (variant) {
      case 'card':
        return (
          <div key={key} className={`bg-white rounded-xl shadow-sm p-6 animate-pulse ${className}`}>
            <div className="bg-gray-200 h-40 rounded-lg mb-4" />
            <div className="bg-gray-200 h-4 w-3/4 rounded mb-2" />
            <div className="bg-gray-200 h-4 w-1/2 rounded mb-1" />
            <div className="bg-gray-200 h-4 w-2/3 rounded mb-4" />
            <div className="bg-gray-200 h-8 w-full rounded-lg" />
          </div>
        );

      case 'list':
        return (
          <div key={key} className={`bg-white rounded-xl shadow-sm p-5 animate-pulse flex items-center gap-4 ${className}`}>
            <div className="w-12 h-12 bg-gray-200 rounded-lg flex-shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="bg-gray-200 h-4 w-3/4 rounded" />
              <div className="bg-gray-200 h-3 w-1/2 rounded" />
            </div>
          </div>
        );

      case 'table':
        return (
          <tr key={key} className="animate-pulse">
            <td className="px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded" />
                <div className="bg-gray-200 h-4 w-40 rounded" />
              </div>
            </td>
            <td className="px-6 py-4"><div className="bg-gray-200 h-4 w-12 mx-auto rounded" /></td>
            <td className="px-6 py-4"><div className="bg-gray-200 h-4 w-12 mx-auto rounded" /></td>
            <td className="px-6 py-4"><div className="bg-gray-200 h-6 w-20 mx-auto rounded-full" /></td>
            <td className="px-6 py-4"><div className="bg-gray-200 h-4 w-24 ml-auto rounded" /></td>
          </tr>
        );

      case 'detail':
        return (
          <div key={key} className={`animate-pulse space-y-4 ${className}`}>
            <div className="bg-gray-200 h-8 w-1/2 rounded" />
            <div className="bg-gray-200 h-4 w-3/4 rounded" />
            <div className="bg-gray-200 h-64 rounded-xl" />
            <div className="space-y-3 mt-6">
              <div className="bg-gray-200 h-4 w-full rounded" />
              <div className="bg-gray-200 h-4 w-5/6 rounded" />
              <div className="bg-gray-200 h-4 w-2/3 rounded" />
              <div className="bg-gray-200 h-4 w-4/5 rounded" />
            </div>
          </div>
        );

      case 'profile':
        return (
          <div key={key} className={`animate-pulse flex items-center gap-4 ${className}`}>
            <div className="w-20 h-20 bg-gray-200 rounded-full" />
            <div className="space-y-2">
              <div className="bg-gray-200 h-5 w-32 rounded" />
              <div className="bg-gray-200 h-4 w-48 rounded" />
            </div>
          </div>
        );

      case 'text':
      default:
        return (
          <div key={key} className={`animate-pulse space-y-3 ${className}`}>
            <div className="bg-gray-200 h-4 w-full rounded" />
            <div className="bg-gray-200 h-4 w-5/6 rounded" />
            <div className="bg-gray-200 h-4 w-2/3 rounded" />
          </div>
        );
    }
  };

  if (variant === 'table') {
    return <>{items.map(renderItem)}</>;
  }

  return (
    <div className={variant === 'card' ? 'grid grid-cols-1 md:grid-cols-3 gap-6' : ''}>
      {items.map(renderItem)}
    </div>
  );
}
