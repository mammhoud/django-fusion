'use client';

import { useState } from 'react';
import Link from 'next/link';
import { HiCurrencyDollar, HiCheck, HiX, HiFilter, HiRefresh, HiExclamation, HiChevronLeft } from 'react-icons/hi';
import ErrorState from '@/components/ui/ErrorState';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import {
  useGetWithdrawalsQuery,
  useApproveWithdrawalMutation,
  useRejectWithdrawalMutation,
} from '@/store/api/endpoints/withdrawals';

const STATUS_OPTIONS = ['all', 'pending', 'approved', 'rejected', 'completed', 'cancelled'] as const;
type StatusFilter = (typeof STATUS_OPTIONS)[number];

export default function AdminWithdrawalsPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [page, setPage] = useState(1);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [rejectingId, setRejectingId] = useState<number | null>(null);

  const { data: withdrawalsData, isLoading, refetch } = useGetWithdrawalsQuery(
    { page, status: statusFilter === 'all' ? undefined : statusFilter },
  );
  const [approveWithdrawal, { isLoading: isApproving }] = useApproveWithdrawalMutation();
  const [rejectWithdrawal, { isLoading: isRejecting }] = useRejectWithdrawalMutation();

  if (profileLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!profile || profile.role !== 'admin') {
    return <ErrorState fullPage message="This page is only available for administrators." />;
  }

  const withdrawals = withdrawalsData?.results ?? [];
  const totalCount = withdrawalsData?.count ?? 0;
  const totalPages = Math.ceil(totalCount / 20);

  const handleApprove = async (id: number) => {
    setErrorMsg('');
    setSuccessMsg('');
    try {
      await approveWithdrawal(id).unwrap();
      setSuccessMsg(`Withdrawal #${id} approved successfully.`);
      refetch();
    } catch (err: any) {
      setErrorMsg(err?.data?.message || 'Failed to approve withdrawal.');
    }
  };

  const handleReject = async (id: number) => {
    setErrorMsg('');
    setSuccessMsg('');
    try {
      await rejectWithdrawal({ id, reason: rejectReason || undefined }).unwrap();
      setSuccessMsg(`Withdrawal #${id} rejected.`);
      setRejectingId(null);
      setRejectReason('');
      refetch();
    } catch (err: any) {
      setErrorMsg(err?.data?.message || 'Failed to reject withdrawal.');
    }
  };

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-700',
      approved: 'bg-blue-100 text-blue-700',
      processing: 'bg-cyan-100 text-cyan-700',
      completed: 'bg-green-100 text-green-700',
      rejected: 'bg-red-100 text-red-700',
      cancelled: 'bg-gray-100 text-gray-600',
    };
    return map[status] ?? 'bg-gray-100 text-gray-600';
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-[rgb(var(--fu-primary))] mb-3 transition-colors"
        >
          <HiChevronLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Withdrawal Approvals</h1>
        <p className="text-sm text-gray-500 mt-1">
          Review and manage instructor withdrawal requests
        </p>
      </div>

      {/* Messages */}
      {errorMsg && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
          <HiExclamation className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{errorMsg}</p>
        </div>
      )}
      {successMsg && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-xl flex items-start gap-3">
          <HiCheck className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-green-700">{successMsg}</p>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-2 flex-wrap">
          <HiFilter className="w-4 h-4 text-gray-400" />
          {STATUS_OPTIONS.map((s) => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1); }}
              className={`px-3 py-1.5 text-sm rounded-lg transition-all font-medium capitalize ${
                statusFilter === s
                  ? 'bg-[rgb(var(--fu-primary))] text-white'
                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-[rgb(var(--fu-primary))] hover:bg-[rgb(var(--fu-primary))]/5 rounded-lg transition-colors"
        >
          <HiRefresh className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Withdrawals Table */}
      {isLoading ? (
        <LoadingSkeleton variant="list" count={5} />
      ) : withdrawals.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <HiCurrencyDollar className="w-16 h-16 mx-auto mb-4 text-gray-200" />
          <p className="text-lg font-medium text-gray-500">No withdrawals found</p>
          <p className="text-sm mt-1">
            {statusFilter === 'all'
              ? 'No withdrawal requests have been submitted yet.'
              : `No ${statusFilter} withdrawals to display.`}
          </p>
        </div>
      ) : (
        <>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm min-w-[600px]">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">ID</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Instructor</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Amount</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Method</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                  <th className="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {withdrawals.map((w) => (
                  <tr key={w.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-gray-500">#{w.id}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{w.instructor_name}</td>
                    <td className="px-4 py-3 text-right font-semibold text-gray-900">
                      ${(w.amount ?? 0).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-gray-500">{w.payment_method_display}</td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {w.created_at
                        ? new Date(w.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })
                        : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex text-xs px-2 py-0.5 rounded-full font-medium ${getStatusBadge(w.status)}`}
                      >
                        {w.status_display}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      {w.status === 'pending' && (
                        <div className="flex items-center justify-end gap-2">
                          {/* Approve */}
                          <button
                            onClick={() => handleApprove(w.id)}
                            disabled={isApproving}
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors disabled:opacity-50"
                            title="Approve withdrawal"
                          >
                            <HiCheck className="w-3.5 h-3.5" />
                            Approve
                          </button>
                          {/* Reject */}
                          {rejectingId === w.id ? (
                            <div className="flex items-center gap-1">
                              <input
                                type="text"
                                value={rejectReason}
                                onChange={(e) => setRejectReason(e.target.value)}
                                placeholder="Reason (optional)"
                                className="w-32 text-xs border border-gray-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-red-300 outline-none"
                                autoFocus
                              />
                              <button
                                onClick={() => handleReject(w.id)}
                                disabled={isRejecting}
                                className="px-2 py-1 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg disabled:opacity-50"
                              >
                                Confirm
                              </button>
                              <button
                                onClick={() => { setRejectingId(null); setRejectReason(''); }}
                                className="px-2 py-1 text-xs text-gray-500 hover:text-gray-700"
                              >
                                Cancel
                              </button>
                            </div>
                          ) : (
                            <button
                              onClick={() => { setRejectingId(w.id); setRejectReason(''); }}
                              disabled={isRejecting}
                              className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
                              title="Reject withdrawal"
                            >
                              <HiX className="w-3.5 h-3.5" />
                              Reject
                            </button>
                          )}
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                    p === page
                      ? 'bg-[rgb(var(--fu-primary))] text-white'
                      : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
