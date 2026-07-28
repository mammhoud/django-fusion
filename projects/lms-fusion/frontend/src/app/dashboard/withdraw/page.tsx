'use client';

import { useState } from 'react';
import { HiCash, HiCurrencyDollar, HiCheck, HiClock, HiDownload, HiXCircle, HiExclamation, HiRefresh } from 'react-icons/hi';
import ErrorState from '@/components/ui/ErrorState';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';
import {
  useGetWithdrawalSummaryQuery,
  useCreateWithdrawalMutation,
  useCancelWithdrawalMutation,
} from '@/store/api/endpoints/withdrawals';

export default function DashboardWithdrawPage() {
  const { data: profile, isLoading: profileLoading } = useGetProfileQuery();
  const { data: summaryData, isLoading: summaryLoading, refetch } = useGetWithdrawalSummaryQuery();
  const [createWithdrawal, { isLoading: isCreating }] = useCreateWithdrawalMutation();
  const [cancelWithdrawal] = useCancelWithdrawalMutation();

  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [selectedMethod, setSelectedMethod] = useState<'paypal' | 'bank_transfer'>('paypal');
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  if (profileLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <LoadingSkeleton variant="profile" />
      </div>
    );
  }

  if (!profile || profile.role !== 'instructor') {
    return <ErrorState fullPage message="This page is only available for instructors." />;
  }

  const summary = summaryData;
  const currentBalance = summary?.current_balance ?? 0;
  const pendingAmount = summary?.pending_amount ?? 0;
  const totalWithdrawn = summary?.total_withdrawn ?? 0;
  const totalEarned = summary?.total_earned ?? 0;
  const withdrawals = summary?.recent_withdrawals ?? [];

  const handleWithdraw = async () => {
    setErrorMsg('');
    setSuccessMsg('');
    const amount = Number(withdrawAmount);
    if (!amount || amount < 50) {
      setErrorMsg('Minimum withdrawal amount is $50.00');
      return;
    }
    if (amount > currentBalance) {
      setErrorMsg(`Insufficient balance. Available: $${currentBalance.toLocaleString()}`);
      return;
    }
    try {
      await createWithdrawal({
        amount,
        payment_method: selectedMethod,
        payment_details: {},
      }).unwrap();
      setSuccessMsg(`Withdrawal of $${amount.toLocaleString()} requested successfully!`);
      setWithdrawAmount('');
      refetch();
    } catch (err: any) {
      setErrorMsg(err?.data?.message || 'Failed to request withdrawal. Please try again.');
    }
  };

  const handleCancel = async (id: number) => {
    try {
      await cancelWithdrawal(id).unwrap();
      refetch();
    } catch (err: any) {
      setErrorMsg(err?.data?.message || 'Failed to cancel withdrawal.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'approved': return 'bg-blue-100 text-blue-700';
      case 'processing': return 'bg-cyan-100 text-cyan-700';
      case 'rejected': return 'bg-red-100 text-red-700';
      case 'cancelled': return 'bg-gray-100 text-gray-600';
      default: return 'bg-yellow-100 text-yellow-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <HiCheck className="w-5 h-5 text-green-600" />;
      case 'rejected':
      case 'cancelled': return <HiXCircle className="w-5 h-5 text-red-500" />;
      default: return <HiClock className="w-5 h-5 text-yellow-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Withdrawals & Payouts</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your earnings and withdrawal requests</p>
        </div>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="section-gradient">
            <p className="text-cyan-100 text-sm mb-1">Current Balance</p>
            <div className="text-3xl font-bold">
              {summaryLoading ? (
                <div className="h-8 w-24 bg-white/20 rounded animate-pulse" />
              ) : (
                `$${currentBalance.toLocaleString()}`
              )}
            </div>
            <p className="text-cyan-100 text-xs mt-2">Available for withdrawal</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <p className="text-gray-500 text-sm mb-1">Pending Payout</p>
            <div className="text-2xl font-bold text-gray-900">
              {summaryLoading ? (
                <div className="h-7 w-20 bg-gray-200 rounded animate-pulse" />
              ) : (
                `$${pendingAmount.toLocaleString()}`
              )}
            </div>
            <p className="text-gray-400 text-xs mt-2">{summary?.pending_count ?? 0} pending request{(summary?.pending_count ?? 0) !== 1 ? 's' : ''}</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <p className="text-gray-500 text-sm mb-1">Total Earned</p>
            <div className="text-2xl font-bold text-gray-900">
              {summaryLoading ? (
                <div className="h-7 w-20 bg-gray-200 rounded animate-pulse" />
              ) : (
                `$${totalEarned.toLocaleString()}`
              )}
            </div>
            <p className="text-gray-400 text-xs mt-2">All time revenue</p>
          </div>
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Withdraw Form */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Request Withdrawal</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Amount ($)</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-medium">$</span>
                <input
                  type="number"
                  value={withdrawAmount}
                  onChange={(e) => { setWithdrawAmount(e.target.value); setErrorMsg(''); }}
                  className="w-full pl-7 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[rgb(var(--fu-primary))] focus:border-transparent outline-none"
                  placeholder="0.00"
                  max={currentBalance || undefined}
                  min={50}
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">Minimum withdrawal: $50.00</p>
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Withdrawal Method</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setSelectedMethod('paypal')}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMethod === 'paypal' ? 'border-[rgb(var(--fu-primary))] bg-[rgb(var(--fu-primary))]/5' : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <div className="text-lg mb-1">💳</div>
                  <div className="font-medium text-sm text-gray-900">PayPal</div>
                  <div className="text-xs text-gray-500">1-3 business days</div>
                </button>
                <button
                  onClick={() => setSelectedMethod('bank_transfer')}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMethod === 'bank_transfer' ? 'border-[rgb(var(--fu-primary))] bg-[rgb(var(--fu-primary))]/5' : 'border-gray-200 hover:border-gray-300'}`}
                >
                  <div className="text-lg mb-1">🏦</div>
                  <div className="font-medium text-sm text-gray-900">Bank Transfer</div>
                  <div className="text-xs text-gray-500">3-5 business days</div>
                </button>
              </div>
            </div>
            <button
              onClick={handleWithdraw}
              disabled={isCreating || !withdrawAmount || Number(withdrawAmount) < 50 || Number(withdrawAmount) > currentBalance}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isCreating ? (
                <HiClock className="w-4 h-4 animate-spin" />
              ) : (
                <HiCash className="w-4 h-4" />
              )}
              {isCreating ? 'Processing...' : `Withdraw $${withdrawAmount || '0.00'}`}
            </button>
          </section>

          {/* Withdrawal History */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Withdrawal History
                {!summaryLoading && <span className="text-sm font-normal text-gray-400 ml-2">({withdrawals.length})</span>}
              </h2>
              <button
                onClick={() => refetch()}
                className="flex items-center gap-1 text-sm text-[rgb(var(--fu-primary))] hover:text-[rgb(var(--fu-primary-dark))]"
              >
                <HiRefresh className="w-4 h-4" /> Refresh
              </button>
            </div>
            {summaryLoading ? (
              <LoadingSkeleton variant="list" count={3} />
            ) : withdrawals.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <HiCurrencyDollar className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm font-medium text-gray-500">No withdrawals yet</p>
                <p className="text-xs mt-1">Your payout requests will appear here</p>
              </div>
            ) : (
              <div className="space-y-3">
                {withdrawals.map((payout) => (
                  <div key={payout.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        payout.status === 'completed' ? 'bg-green-100' : 
                        payout.status === 'rejected' || payout.status === 'cancelled' ? 'bg-red-100' :
                        payout.status === 'approved' ? 'bg-blue-100' :
                        'bg-yellow-100'
                      }`}>
                        {getStatusIcon(payout.status)}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900 text-sm">
                          ${(payout.amount ?? 0).toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500">
                          {payout.created_at
                            ? new Date(payout.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                            : ''}
                          {' · '}
                          {payout.payment_method_display}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(payout.status)}`}>
                        {payout.status_display}
                      </span>
                      {payout.can_cancel && (
                        <button
                          onClick={() => handleCancel(payout.id)}
                          className="text-xs text-red-500 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50 transition-colors"
                          title="Cancel this withdrawal request"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
