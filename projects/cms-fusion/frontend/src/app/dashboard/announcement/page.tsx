'use client';

import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { HiSpeakerphone, HiPlus, HiTrash, HiPencil, HiCheck, HiX } from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import {
  useGetAnnouncementsQuery,
  useCreateAnnouncementMutation,
  useUpdateAnnouncementMutation,
  useDeleteAnnouncementMutation,
  type Announcement,
  type AnnouncementCreatePayload,
} from '@/store/api/endpoints/announcements';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function DashboardAnnouncementPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const {
    data: announcementsData,
    isLoading: annLoading,
    error: annError,
    refetch,
  } = useGetAnnouncementsQuery();
  const [createAnnouncement, { isLoading: isCreating }] = useCreateAnnouncementMutation();
  const [updateAnnouncement, { isLoading: isUpdating }] = useUpdateAnnouncementMutation();
  const [deleteAnnouncement, { isLoading: isDeleting }] = useDeleteAnnouncementMutation();

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<AnnouncementCreatePayload>({
    title: '',
    content: '',
    audience: 'all',
    link: '',
    link_label: '',
    publish_now: true,
  });
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [formError, setFormError] = useState('');

  const isInstructor = profile?.role === 'instructor';
  const announcements = announcementsData?.results ?? [];

  const resetForm = useCallback(() => {
    setForm({ title: '', content: '', audience: 'all', link: '', link_label: '', publish_now: true });
    setFormError('');
    setEditingId(null);
    setShowForm(false);
  }, []);

  const openEdit = useCallback((ann: Announcement) => {
    setForm({
      title: ann.title,
      content: ann.content,
      audience: ann.audience,
      link: ann.link,
      link_label: ann.link_label,
      publish_now: !ann.is_published,
    });
    setEditingId(ann.id);
    setShowForm(true);
    setFormError('');
  }, []);

  const handleSubmit = async () => {
    if (!form.title.trim() || !form.content.trim()) {
      setFormError('Title and content are required.');
      return;
    }
    try {
      if (editingId !== null) {
        await updateAnnouncement({ id: editingId, data: form }).unwrap();
      } else {
        await createAnnouncement(form).unwrap();
      }
      resetForm();
      refetch();
    } catch (err: any) {
      setFormError(err?.data?.message || 'Failed to save announcement.');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAnnouncement(id).unwrap();
      setDeleteConfirm(null);
      refetch();
    } catch (err: any) {
      // Silently fail
    }
  };

  if (profileLoading) {
    return (
      <div className="min-h-[40vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!isInstructor) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <ErrorState
          fullPage
          message="This page is only available for instructors."
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Announcements</h1>
          <p className="text-gray-500 mt-1">Communicate with your students</p>
        </div>
        {!showForm && (
          <button
            onClick={() => { resetForm(); setShowForm(true); }}
            className="btn-primary flex items-center gap-2"
          >
            <HiPlus className="w-4 h-4" /> New Announcement
          </button>
        )}
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {editingId ? 'Edit Announcement' : 'New Announcement'}
            </h2>
            <button onClick={resetForm} className="text-gray-400 hover:text-gray-600">
              <HiX className="w-5 h-5" />
            </button>
          </div>

          {formError && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2 mb-4">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                placeholder="e.g., New Course Coming Soon"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
              <textarea
                value={form.content}
                onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none resize-none"
                placeholder="Write your announcement..."
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Audience</label>
                <select
                  value={form.audience}
                  onChange={(e) => setForm((f) => ({ ...f, audience: e.target.value as any }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                >
                  <option value="all">All Users</option>
                  <option value="instructor">Instructors Only</option>
                  <option value="student">Students Only</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Link URL (optional)</label>
                <input
                  type="url"
                  value={form.link}
                  onChange={(e) => setForm((f) => ({ ...f, link: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Link Label</label>
                <input
                  type="text"
                  value={form.link_label}
                  onChange={(e) => setForm((f) => ({ ...f, link_label: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none"
                  placeholder="Learn More"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.publish_now}
                    onChange={(e) => setForm((f) => ({ ...f, publish_now: e.target.checked }))}
                    className="rounded border-gray-300 text-[rgb(var(--fu-primary))] focus:ring-[rgb(var(--fu-primary))]"
                  />
                  <span className="text-sm text-gray-700">Publish immediately</span>
                </label>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={resetForm}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={isCreating || isUpdating}
                className="btn-primary flex items-center gap-2 text-sm"
              >
                {(isCreating || isUpdating) ? (
                  <>Saving...</>
                ) : (
                  <>{editingId ? 'Update' : 'Publish'}</>
                )}
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading State */}
      {annLoading && (
        <div className="space-y-4">
          <LoadingSkeleton variant="card" count={3} />
        </div>
      )}

      {/* Error State */}
      {annError && !annLoading && (
        <ErrorState
          message="Failed to load announcements."
          onRetry={() => refetch()}
        />
      )}

      {/* Announcements List */}
      {!annLoading && !annError && (
        <div className="space-y-4">
          {announcements.length === 0 ? (
            isInstructor ? (
              <EmptyState
                icon="generic"
                title="No announcements yet"
                description="Create your first announcement to communicate with students."
                actionLabel="Create Announcement"
                onAction={() => { resetForm(); setShowForm(true); }}
              />
            ) : (
              <EmptyState
                icon="generic"
                title="No announcements"
                description="No announcements at this time."
              />
            )
          ) : (
            announcements.map((a, idx) => (
              <motion.div
                key={a.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="card p-5"
              >
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-[rgb(var(--fu-primary))]/10 rounded-full flex items-center justify-center flex-shrink-0">
                    <HiSpeakerphone className="w-5 h-5 text-[rgb(var(--fu-primary))]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {a.title}
                      </h3>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {a.is_published ? (
                          <span className="badge-primary text-xs">Published</span>
                        ) : (
                          <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full font-medium">
                            Draft
                          </span>
                        )}
                        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full capitalize">
                          {a.audience}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{a.content}</p>
                    <div className="flex items-center justify-between mt-3">
                      <p className="text-xs text-gray-400">
                        {a.published_at
                          ? new Date(a.published_at).toLocaleDateString('en-US', {
                              year: 'numeric', month: 'long', day: 'numeric',
                            })
                          : 'Not published'}
                      </p>
                      <div className="flex items-center gap-2">
                        {a.link && (
                          <a
                            href={a.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-[rgb(var(--fu-primary))] hover:underline"
                          >
                            {a.link_label || 'Learn More'}
                          </a>
                        )}
                        <button
                          onClick={() => openEdit(a)}
                          className="text-gray-400 hover:text-gray-600"
                          title="Edit"
                        >
                          <HiPencil className="w-4 h-4" />
                        </button>
                        {deleteConfirm === a.id ? (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleDelete(a.id)}
                              disabled={isDeleting}
                              className="text-red-500 hover:text-red-700"
                              title="Confirm delete"
                            >
                              <HiCheck className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => setDeleteConfirm(null)}
                              className="text-gray-400 hover:text-gray-600"
                              title="Cancel"
                            >
                              <HiX className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setDeleteConfirm(a.id)}
                            className="text-gray-400 hover:text-red-500"
                            title="Delete"
                          >
                            <HiTrash className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
