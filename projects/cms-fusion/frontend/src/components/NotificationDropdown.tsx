'use client';

import Link from 'next/link';
import { HiCheck, HiCheckCircle, HiX } from 'react-icons/hi';
import {
  useGetNotificationsQuery,
  useMarkNotificationReadMutation,
  useMarkAllNotificationsReadMutation,
  type Notification,
} from '@/store/api/endpoints/notifications';

const TYPE_ICONS: Record<string, string> = {
  enrollment: '📝',
  course_update: '📢',
  assignment: '📋',
  grading: '✅',
  quiz: '📊',
  review: '⭐',
  announcement: '📣',
  system: '🔔',
};

interface NotificationDropdownProps {
  onClose: () => void;
}

export default function NotificationDropdown({ onClose }: NotificationDropdownProps) {
  const { data, isLoading } = useGetNotificationsQuery({ limit: 10 });
  const [markRead] = useMarkNotificationReadMutation();
  const [markAllRead] = useMarkAllNotificationsReadMutation();

  const notifications = data?.results ?? [];
  const hasUnread = notifications.some((n) => !n.is_read);

  const handleMarkAllRead = async () => {
    await markAllRead();
  };

  const handleItemClick = async (notification: Notification) => {
    if (!notification.is_read) {
      await markRead(notification.id);
    }
    onClose();
  };

  return (
    <div className="bg-white rounded-xl shadow-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
        <h3 className="font-semibold text-gray-900 text-sm">Notifications</h3>
        {hasUnread && (
          <button
            onClick={handleMarkAllRead}
            className="text-xs font-medium text-[rgb(var(--fu-primary))] hover:text-[rgb(var(--fu-primary-dark))] flex items-center gap-1 transition-colors"
          >
            <HiCheckCircle className="w-3.5 h-3.5" />
            Mark all read
          </button>
        )}
      </div>

      {/* Body */}
      <div className="max-h-[360px] overflow-y-auto">
        {isLoading ? (
          <div className="p-6 text-center text-sm text-gray-400">
            <div className="w-6 h-6 border-2 border-[rgb(var(--fu-primary))] border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading...
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-3xl mb-2">🔔</div>
            <p className="text-sm text-gray-500">No notifications yet</p>
            <p className="text-xs text-gray-400 mt-1">We&apos;ll notify you when something arrives</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {notifications.map((notification) => (
              <button
                key={notification.id}
                onClick={() => handleItemClick(notification)}
                className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors ${
                  !notification.is_read ? 'bg-[rgb(var(--fu-primary))]/[0.03]' : ''
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-lg flex-shrink-0 mt-0.5">
                    {TYPE_ICONS[notification.type] || '🔔'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p
                        className={`text-sm truncate ${
                          !notification.is_read
                            ? 'font-semibold text-gray-900'
                            : 'text-gray-700'
                        }`}
                      >
                        {notification.title}
                      </p>
                      {!notification.is_read && (
                        <span className="w-2 h-2 bg-[rgb(var(--fu-primary))] rounded-full flex-shrink-0" />
                      )}
                    </div>
                    {notification.message && (
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                        {notification.message}
                      </p>
                    )}
                    <p className="text-[10px] text-gray-400 mt-1">
                      {notification.time_ago}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <Link
        href={"/dashboard/notifications" as any}
        onClick={onClose}
        className="block px-4 py-3 text-center text-sm font-medium text-[rgb(var(--fu-primary))] hover:text-[rgb(var(--fu-primary-dark))] hover:bg-gray-50 border-t border-gray-100 transition-colors"
      >
        View all notifications
      </Link>
    </div>
  );
}
