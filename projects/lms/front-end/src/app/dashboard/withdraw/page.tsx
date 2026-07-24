'use client';

import { useState } from 'react';
import { HiCash, HiCurrencyDollar, HiCheck, HiClock, HiDownload } from 'react-icons/hi';
import ErrorState from '@/components/ui/ErrorState';
import { useGetProfileQuery } from '@/store/api/endpoints/auth';

const mockPayouts = [
  { id: 'p1', amount: 2480.50, date: 'Jan 1, 2026', status: 'Completed', method: 'PayPal', reference: 'PAY-1234567890' },
  { id: 'p2', amount: 3120.75, date: 'Dec 1, 2025', status: 'Completed', method: 'Bank Transfer', reference: 'BANK-987654321' },
  { id: 'p3', amount: 1890.25, date: 'Nov 1, 2025', status: 'Completed', method: 'PayPal', reference: 'PAY-4567890123' },
  { id: 'p4', amount: 4250.00, date: 'Oct 1, 2025', status: 'Completed', method: 'Bank Transfer', reference: 'BANK-321098765' },
  { id: 'p5', amount: 1560.80, date: 'Pending', status: 'Pending', method: 'PayPal', reference: '' },
];

export default function DashboardWithdrawPage() {
  const { data: profile } = useGetProfileQuery();
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [selectedMethod, setSelectedMethod] = useState<'PayPal' | 'Bank Transfer'>('PayPal');

  if (profile?.role !== 'instructor') {
    return <ErrorState fullPage message="This page is only available for instructors." />;
  }

  const currentBalance = 5890.25;
  const pendingAmount = 1560.80;
  const totalEarned = mockPayouts.reduce((sum, p) => sum + (p.status === 'Completed' ? p.amount : 0), 0);

  const handleWithdraw = () => {
    alert(`Withdrawal of $${withdrawAmount} via ${selectedMethod} requested!`);
    setWithdrawAmount('');
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
            <div className="text-3xl font-bold">${currentBalance.toLocaleString()}</div>
            <p className="text-cyan-100 text-xs mt-2">Available for withdrawal</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <p className="text-gray-500 text-sm mb-1">Pending Payout</p>
            <div className="text-2xl font-bold text-gray-900">${pendingAmount.toLocaleString()}</div>
            <p className="text-gray-400 text-xs mt-2">Processing</p>
          </div>
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <p className="text-gray-500 text-sm mb-1">Total Earned</p>
            <div className="text-2xl font-bold text-gray-900">${(totalEarned + pendingAmount).toLocaleString()}</div>
            <p className="text-gray-400 text-xs mt-2">All time revenue</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Withdraw Form */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Request Withdrawal</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Amount ($)</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 font-medium">$</span>
                <input type="number" value={withdrawAmount} onChange={(e) => setWithdrawAmount(e.target.value)}
                  className="w-full pl-7 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[rgb(var(--ctc-primary))] focus:border-transparent outline-none"
                  placeholder="0.00" max={currentBalance} min={50} />
              </div>
              <p className="text-xs text-gray-400 mt-1">Minimum withdrawal: $50.00</p>
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Withdrawal Method</label>
              <div className="grid grid-cols-2 gap-3">
                <button onClick={() => setSelectedMethod('PayPal')}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMethod === 'PayPal' ? 'border-[rgb(var(--ctc-primary))] bg-[rgb(var(--ctc-primary))]/5' : 'border-gray-200 hover:border-gray-300'}`}>
                  <div className="text-lg mb-1">💳</div>
                  <div className="font-medium text-sm text-gray-900">PayPal</div>
                  <div className="text-xs text-gray-500">1-3 business days</div>
                </button>
                <button onClick={() => setSelectedMethod('Bank Transfer')}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMethod === 'Bank Transfer' ? 'border-[rgb(var(--ctc-primary))] bg-[rgb(var(--ctc-primary))]/5' : 'border-gray-200 hover:border-gray-300'}`}>
                  <div className="text-lg mb-1">🏦</div>
                  <div className="font-medium text-sm text-gray-900">Bank Transfer</div>
                  <div className="text-xs text-gray-500">3-5 business days</div>
                </button>
              </div>
            </div>
            <button onClick={handleWithdraw}
              disabled={!withdrawAmount || Number(withdrawAmount) < 50 || Number(withdrawAmount) > currentBalance}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
              <HiCash className="w-4 h-4" /> Withdraw ${withdrawAmount || '0.00'}
            </button>
          </section>

          {/* Payout History */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Payout History</h2>
              <button className="flex items-center gap-1 text-sm text-[rgb(var(--ctc-primary))] hover:text-[rgb(var(--ctc-primary-dark))]">
                <HiDownload className="w-4 h-4" /> Export
              </button>
            </div>
            <div className="space-y-3">
              {mockPayouts.map((payout) => (
                <div key={payout.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${payout.status === 'Completed' ? 'bg-green-100' : 'bg-yellow-100'}`}>
                      {payout.status === 'Completed' ? <HiCheck className="w-5 h-5 text-green-600" /> : <HiClock className="w-5 h-5 text-yellow-600" />}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 text-sm">${payout.amount.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">{payout.date} · {payout.method}</div>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${payout.status === 'Completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{payout.status}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
