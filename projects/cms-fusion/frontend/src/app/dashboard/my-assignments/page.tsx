'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  HiClipboardList, HiCheckCircle, HiClock, HiUpload, HiDocumentText, HiStar, HiX, HiPaperClip,
} from 'react-icons/hi';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import {
  useGetAssignmentsQuery,
  useGetMySubmissionsQuery,
  useSubmitAssignmentMutation,
  useUploadAssignmentFileMutation,
  type Assignment,
  type AssignmentSubmission,
} from '@/store/api/endpoints/assignments';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function MyAssignmentsPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const {
    data: assignmentsData,
    isLoading: assLoading,
    error: assError,
  } = useGetAssignmentsQuery();
  const {
    data: submissionsData,
    isLoading: subLoading,
    refetch: refetchSubs,
  } = useGetMySubmissionsQuery();
  const [submitAssignment, { isLoading: isSubmitting }] = useSubmitAssignmentMutation();

  const [uploadFile, { isLoading: isUploading }] = useUploadAssignmentFileMutation();

  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);
  const [textSubmission, setTextSubmission] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [uploadedFile, setUploadedFile] = useState<{ url: string; name: string } | null>(null);

  const assignments = assignmentsData?.results ?? [];
  const submissions = submissionsData?.results ?? [];

  // Map assignment ID to submission
  const submissionMap = new Map<number, AssignmentSubmission>();
  submissions.forEach((s) => submissionMap.set(s.assignment, s));

  const handleSubmit = async () => {
    if (!selectedAssignment) return;
    if (!textSubmission.trim()) {
      setSubmitError('Please enter your submission text.');
      return;
    }
    try {
      await submitAssignment({
        assignmentId: selectedAssignment.id,
        data: {
          text_submission: textSubmission.trim(),
          file_url: uploadedFile?.url || '',
          file_name: uploadedFile?.name || '',
        },
      }).unwrap();
      setTextSubmission('');
      setUploadedFile(null);
      setSelectedAssignment(null);
      setSubmitError('');
      refetchSubs();
    } catch (err: any) {
      setSubmitError(err?.data?.message || 'Failed to submit.');
    }
  };

  if (profileLoading) {
    return (
      <div className="min-h-[40vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!profile) {
    return <ErrorState fullPage message="Please sign in to view your assignments." />;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Assignments</h1>
        <p className="text-gray-500 mt-1">View and submit your course assignments</p>
      </div>

      {/* Loading */}
      {(assLoading || subLoading) && (
        <LoadingSkeleton variant="card" count={4} />
      )}

      {/* Error */}
      {assError && !assLoading && (
        <ErrorState message="Failed to load assignments." />
      )}

      {/* Assignment List */}
      {!assLoading && !assError && assignments.length === 0 && (
        <EmptyState icon="generic" title="No assignments yet"
          description="Your instructors haven't posted any assignments yet." />
      )}

      {!assLoading && !assError && assignments.length > 0 && (
        <div className="space-y-4">
          {assignments.map((a, idx) => {
            const sub = submissionMap.get(a.id);
            const isPastDue = a.due_date && new Date(a.due_date) < new Date();

            return (
              <motion.div key={a.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }} className="card p-5">
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    sub?.status === 'graded' ? 'bg-green-100' : sub ? 'bg-blue-100' : 'bg-gray-100'
                  }`}>
                    {sub?.status === 'graded' ? (
                      <HiCheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <HiClipboardList className={`w-5 h-5 ${sub ? 'text-blue-600' : 'text-gray-400'}`} />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900">{a.title}</h3>
                        <p className="text-xs text-gray-500 mt-0.5">{a.course_title}</p>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {sub?.status === 'graded' ? (
                          <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full font-medium">
                            {sub.score}/{a.max_score}
                          </span>
                        ) : sub ? (
                          <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium">
                            Submitted
                          </span>
                        ) : isPastDue ? (
                          <span className="bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded-full font-medium">
                            Past Due
                          </span>
                        ) : (
                          <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full font-medium">
                            Pending
                          </span>
                        )}
                      </div>
                    </div>

                    {a.description && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">{a.description}</p>
                    )}

                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-4 text-xs text-gray-400">
                        {a.due_date && (
                          <span className="flex items-center gap-1">
                            <HiClock className="w-3.5 h-3.5" />
                            Due {new Date(a.due_date).toLocaleDateString('en-US', {
                              year: 'numeric', month: 'short', day: 'numeric',
                            })}
                          </span>
                        )}
                        <span>{a.max_score} pts</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Grade & Feedback */}
                        {sub?.status === 'graded' && (
                          <button onClick={() => setSelectedAssignment(a)}
                            className="text-xs text-[rgb(var(--fu-primary))] hover:underline flex items-center gap-1">
                            <HiStar className="w-3.5 h-3.5" /> View Feedback
                          </button>
                        )}
                        {/* Submit button */}
                        {!sub && !isPastDue && (
                          <button onClick={() => { setSelectedAssignment(a); setTextSubmission(''); setSubmitError(''); setUploadedFile(null); }}
                            className="text-xs text-[rgb(var(--fu-primary))] hover:underline flex items-center gap-1">
                            <HiUpload className="w-3.5 h-3.5" /> Submit
                          </button>
                        )}
                        {/* Re-submit */}
                        {sub && sub.status !== 'graded' && (
                          <button onClick={() => { setSelectedAssignment(a); setTextSubmission(sub.text_submission); setSubmitError(''); setUploadedFile(null); }}
                            className="text-xs text-[rgb(var(--fu-primary))] hover:underline flex items-center gap-1">
                            <HiUpload className="w-3.5 h-3.5" /> Re-submit
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Submission / Feedback Modal */}
      {selectedAssignment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => setSelectedAssignment(null)}>
          <div className="bg-white rounded-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto shadow-2xl mx-4"
            onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">
                {selectedAssignment.title}
              </h2>
              <button onClick={() => setSelectedAssignment(null)}
                className="text-gray-400 hover:text-gray-600"><HiX className="w-5 h-5" /></button>
            </div>
            <div className="p-6">
              <p className="text-xs text-gray-500 mb-4">{selectedAssignment.course_title}</p>

              {/* Assignment details */}
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-1">Instructions</h3>
                <p className="text-sm text-gray-600 whitespace-pre-wrap">
                  {selectedAssignment.instructions || 'No specific instructions provided.'}
                </p>
              </div>

              {selectedAssignment.due_date && (
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                  <HiClock className="w-4 h-4" />
                  Due: {new Date(selectedAssignment.due_date).toLocaleDateString('en-US', {
                    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit',
                  })}
                </div>
              )}

              <div className="text-sm text-gray-500 mb-4">
                Max Score: <strong className="text-gray-900">{selectedAssignment.max_score} pts</strong>
              </div>

              {/* Show feedback if graded */}
              {(() => {
                const sub = submissionMap.get(selectedAssignment.id);
                if (sub?.status === 'graded') {
                  return (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <HiCheckCircle className="w-5 h-5 text-green-600" />
                        <span className="font-semibold text-green-800">
                          Grade: {sub.score}/{selectedAssignment.max_score}
                        </span>
                      </div>
                      {sub.feedback && (
                        <div>
                          <p className="text-xs font-medium text-green-800 mb-1">Feedback:</p>
                          <p className="text-sm text-green-700 whitespace-pre-wrap">{sub.feedback}</p>
                        </div>
                      )}
                      {sub.text_submission && (
                        <div className="mt-3">
                          <p className="text-xs font-medium text-gray-600 mb-1">Your submission:</p>
                          <div className="bg-white rounded-lg p-3 text-sm text-gray-700 whitespace-pre-wrap max-h-32 overflow-y-auto">
                            {sub.text_submission}
                          </div>
                        </div>
                      )}
                      {sub.file_url && (
                        <div className="mt-2">
                          <a href={sub.file_url} target="_blank" rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-sm text-[rgb(var(--fu-primary))] hover:underline bg-white rounded-lg px-3 py-2 border border-gray-200">
                            📎 {sub.file_name || 'Download Attachment'}
                          </a>
                        </div>
                      )}
                    </div>
                  );
                }
                return null;
              })()}

              {/* Submit form */}
              {submissionMap.get(selectedAssignment.id)?.status !== 'graded' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <HiDocumentText className="w-4 h-4 inline mr-1" />
                      Your Submission
                    </label>
                    <textarea value={textSubmission}
                      onChange={(e) => setTextSubmission(e.target.value)}
                      rows={6}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[rgb(var(--fu-primary))]/20 focus:border-[rgb(var(--fu-primary))] outline-none resize-none"
                      placeholder="Write or paste your assignment submission here..." />
                  </div>

                  {/* File Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <HiPaperClip className="w-4 h-4 inline mr-1" />
                      Attach a File
                      <span className="text-xs text-gray-400 ml-2">(optional — PDF, DOC, ZIP, images, code)</span>
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[rgb(var(--fu-primary))]/50 transition-colors">
                      {uploadedFile ? (
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-sm">
                            <HiPaperClip className="w-4 h-4 text-[rgb(var(--fu-primary))]" />
                            <span className="text-gray-700 truncate max-w-[200px]">{uploadedFile.name}</span>
                            <span className="text-xs text-green-600 font-medium">Uploaded ✓</span>
                          </div>
                          <button onClick={() => setUploadedFile(null)}
                            className="text-xs text-red-500 hover:text-red-700 hover:underline">Remove</button>
                        </div>
                      ) : (
                        <label className="flex items-center gap-2 cursor-pointer">
                          <HiUpload className="w-5 h-5 text-gray-400" />
                          <span className="text-sm text-gray-500">
                            {isUploading ? 'Uploading...' : 'Click to upload a file'}
                          </span>
                          <input
                            type="file"
                            className="hidden"
                            disabled={isUploading}
                            onChange={async (e) => {
                              const file = e.target.files?.[0];
                              if (!file) return;
                              try {
                                const result = await uploadFile(file).unwrap();
                                setUploadedFile({ url: result.file_url, name: result.file_name });
                              } catch (err: any) {
                                setSubmitError(err?.data?.message || 'Upload failed.');
                              }
                              // Reset the input so the same file can be re-selected
                              e.target.value = '';
                            }}
                          />
                        </label>
                      )}
                    </div>
                  </div>

                  {submitError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-3 py-2">
                      {submitError}
                    </div>
                  )}

                  <div className="flex items-center justify-end gap-3">
                    <button onClick={() => setSelectedAssignment(null)}
                      className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg">
                      Cancel
                    </button>
                    <button onClick={handleSubmit} disabled={isSubmitting || (!textSubmission.trim() && !uploadedFile)}
                      className="btn-primary flex items-center gap-2 text-sm">
                      {isSubmitting ? 'Submitting...' : 'Submit Assignment'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
