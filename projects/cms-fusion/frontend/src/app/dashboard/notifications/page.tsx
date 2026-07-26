'use client';

import { useState, useEffect } from 'react';
import { HiBell, HiMail, HiClock, HiCheck } from 'react-icons/hi';
import {
  useGetNotificationPreferencesQuery,
  useUpdateNotificationPreferencesMutation,
  type NotificationPreference,
} from '@/store/api/endpoints/notifications';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

export default function NotificationsPage() {
  const { data: prefData, isLoading } = useGetNotificationPreferencesQuery();
  const [updatePrefs, { isLoading: isSaving }] = useUpdateNotificationPreferencesMutation();
  const [localPrefs, setLocalPrefs] = useState<NotificationPreference | null>(null);
  const [showSaved, setShowSaved] = useState(false);

  useEffect(() => {
    if (prefData?.data) {
      setLocalPrefs(prefData.data);
    }
  }, [prefData]);

  const togglePref = (key: keyof NotificationPreference) => {
    if (!localPrefs) return;
    const updated = { ...localPrefs, [key]: !localPrefs[key] };
    setLocalPrefs(updated);
  };

  const handleSave = async () => {
    if (!localPrefs) return;
    await updatePrefs(localPrefs);
    setShowSaved(true);
    setTimeout(() => setShowSaved(false), 3000);
  };

  if (isLoading || !localPrefs) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10">
        <LoadingSkeleton variant="detail" />
      </div>
    );
  }

  const channelToggles = [
    { key: 'in_app_notifications' as keyof NotificationPreference, icon: HiBell, label: 'In-App Notifications', desc: 'Show notifications in the bell menu' },
    { key: 'email_notifications' as keyof NotificationPreference, icon: HiMail, label: 'Email Notifications', desc: 'Send notification emails' },
  ];

  const typeToggles = [
    { key: 'enrollment_notifications' as keyof NotificationPreference, label: 'Enrollments', desc: 'When someone enrolls in your course' },
    { key: 'course_update_notifications' as keyof NotificationPreference, label: 'Course Updates', desc: 'When your course content changes' },
    { key: 'assignment_notifications' as keyof NotificationPreference, label: 'Assignments', desc: 'When assignments are created or due' },
    { key: 'grading_notifications' as keyof NotificationPreference, label: 'Grading', desc: 'When grades are posted' },
    { key: 'quiz_notifications' as keyof NotificationPreference, label: 'Quizzes', desc: 'When quiz results are available' },
    { key: 'review_notifications' as keyof NotificationPreference, label: 'Reviews', desc: 'When you receive a course review' },
    { key: 'announcement_notifications' as keyof NotificationPreference, label: 'Announcements', desc: 'When announcements are posted' },
    { key: 'system_notifications' as keyof NotificationPreference, label: 'System', desc: 'System updates and maintenance notices' },
  ];

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Notification Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Manage how and when you receive notifications</p>
      </div>

      {/* Saved indicator */}
      {showSaved && (
        <div className="mb-6 flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 px-4 py-3 rounded-lg">
          <HiCheck className="w-4 h-4" />
          Preferences saved successfully
        </div>
      )}

      {/* Channel preferences */}
      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
          <HiBell className="w-4 h-4 text-[rgb(var(--ctc-primary))]" />
          Channels
        </h2>
        <div className="space-y-3">
          {channelToggles.map(({ key, icon: Icon, label, desc }) => (
            <label key={key} className="card p-4 flex items-center justify-between cursor-pointer hover:shadow-sm transition-shadow">
              <div className="flex items-center gap-3">
                <Icon className="w-5 h-5 text-gray-400" />
                <div>
                  <div className="text-sm font-medium text-gray-900">{label}</div>
                  <div className="text-xs text-gray-500">{desc}</div>
                </div>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={!!localPrefs[key]}
                  onChange={() => togglePref(key)}
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-gray-200 peer-checked:bg-[rgb(var(--ctc-primary))] rounded-full peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
              </div>
            </label>
          ))}
        </div>
      </section>

      {/* Type preferences */}
      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
          <HiClock className="w-4 h-4 text-[rgb(var(--ctc-primary))]" />
          Notification Types
        </h2>
        <div className="space-y-2">
          {typeToggles.map(({ key, label, desc }) => (
            <label key={key} className="card p-4 flex items-center justify-between cursor-pointer hover:shadow-sm transition-shadow">
              <div>
                <div className="text-sm font-medium text-gray-900">{label}</div>
                <div className="text-xs text-gray-500">{desc}</div>
              </div>
              <div className="relative flex-shrink-0 ml-3">
                <input
                  type="checkbox"
                  checked={!!localPrefs[key]}
                  onChange={() => togglePref(key)}
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-gray-200 peer-checked:bg-[rgb(var(--ctc-primary))] rounded-full peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all" />
              </div>
            </label>
          ))}
        </div>
      </section>

      {/* Frequency */}
      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
          <HiClock className="w-4 h-4 text-[rgb(var(--ctc-primary))]" />
          Digest Frequency
        </h2>
        <div className="card p-4">
          <select
            value={localPrefs.digest_frequency}
            onChange={(e) => setLocalPrefs({ ...localPrefs, digest_frequency: e.target.value as NotificationPreference['digest_frequency'] })}
            className="input-field w-full"
          >
            <option value="immediate">Immediate — notify me right away</option>
            <option value="daily">Daily Digest — once per day</option>
            <option value="weekly">Weekly Digest — once per week</option>
            <option value="never">Never — no notification emails</option>
          </select>
        </div>
      </section>

      {/* Save */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary px-8 py-2.5 flex items-center gap-2"
        >
          {isSaving ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Saving...
            </>
          ) : (
            'Save Preferences'
          )}
        </button>
      </div>
    </div>
  );
}
