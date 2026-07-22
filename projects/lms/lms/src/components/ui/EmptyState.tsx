'use client';

import Link from 'next/link';
import { HiAcademicCap, HiBookOpen, HiShoppingCart, HiCalendar, HiUserGroup, HiChat, HiSearch, HiInbox } from 'react-icons/hi';
import type { IconType } from 'react-icons';

interface EmptyStateProps {
  icon?: 'courses' | 'blog' | 'shop' | 'events' | 'instructors' | 'messages' | 'search' | 'inbox' | 'generic';
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
  className?: string;
}

const iconMap: Record<string, IconType> = {
  courses: HiBookOpen,
  blog: HiChat,
  shop: HiShoppingCart,
  events: HiCalendar,
  instructors: HiUserGroup,
  messages: HiChat,
  search: HiSearch,
  inbox: HiInbox,
  generic: HiAcademicCap,
};

const defaultMessages: Record<string, { title: string; description: string }> = {
  courses: { title: 'No courses found', description: 'No courses match your current filters. Try adjusting your search criteria.' },
  blog: { title: 'No posts yet', description: 'There are no blog posts to display. Check back later for new content.' },
  shop: { title: 'No products found', description: 'The shop is currently empty. Check back later for new merchandise.' },
  events: { title: 'No events scheduled', description: 'There are no upcoming events at the moment. Stay tuned for future events.' },
  instructors: { title: 'No instructors found', description: 'No instructors match your search. Try a different search term.' },
  messages: { title: 'No messages', description: 'You have no messages in your inbox.' },
  search: { title: 'No results found', description: 'Try adjusting your search terms or filters.' },
  generic: { title: 'Nothing here yet', description: 'Content will appear here once available.' },
};

export default function EmptyState({
  icon = 'generic',
  title,
  description,
  actionLabel,
  actionHref,
  onAction,
  className = '',
}: EmptyStateProps) {
  const Icon = iconMap[icon] || HiAcademicCap;
  const defaults = defaultMessages[icon] || defaultMessages.generic;

  return (
    <div className={`text-center py-16 ${className}`}>
      <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-5">
        <Icon className="w-10 h-10 text-gray-400" />
      </div>
      <h3 className="text-xl font-semibold text-gray-700 mb-2">
        {title || defaults.title}
      </h3>
      <p className="text-gray-500 max-w-md mx-auto mb-6">
        {description || defaults.description}
      </p>
      {(actionLabel && actionHref) && (
        <Link href={actionHref as any} className="btn-primary inline-flex">
          {actionLabel}
        </Link>
      )}
      {(actionLabel && onAction && !actionHref) && (
        <button onClick={onAction} className="btn-primary">
          {actionLabel}
        </button>
      )}
    </div>
  );
}
