'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { HiArrowLeft, HiLockClosed } from 'react-icons/hi';
import { useCreateOrderMutation } from '@/store/api/endpoints/shop';

export default function CheckoutPage() {
  const router = useRouter();
  const [form, setForm] = useState({ shipping_address: '', payment_method: 'card' });
  const [createOrder, { isLoading, isSuccess }] = useCreateOrderMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createOrder(form).unwrap();
      setTimeout(() => router.push('/cart'), 2000);
    } catch { /* handled */ }
  };

  if (isSuccess) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <HiLockClosed className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Order Placed Successfully!</h2>
        <p className="text-gray-500">Thank you for your purchase. You&apos;ll receive a confirmation email shortly.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <Link href="/cart" className="inline-flex items-center gap-2 text-gray-500 hover:text-indigo-600 mb-8 transition-colors">
        <HiArrowLeft className="w-4 h-4" /> Back to Cart
      </Link>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

      <form onSubmit={handleSubmit} className="card p-8 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Shipping Address</label>
          <textarea rows={3} value={form.shipping_address} onChange={(e) => setForm({...form, shipping_address: e.target.value})}
            className="input-field" placeholder="Enter your full shipping address" required />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method</label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'card', label: 'Credit Card' },
              { value: 'paypal', label: 'PayPal' },
              { value: 'stripe', label: 'Stripe' },
            ].map((method) => (
              <button key={method.value} type="button" onClick={() => setForm({...form, payment_method: method.value})}
                className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                  form.payment_method === method.value ? 'border-indigo-600 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}>{method.label}</button>
            ))}
          </div>
        </div>
        <button type="submit" disabled={isLoading} className="btn-primary w-full flex items-center justify-center gap-2">
          {isLoading ? (
            <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Processing...</>
          ) : (
            <><HiLockClosed className="w-4 h-4" /> Place Order</>
          )}
        </button>
      </form>
    </div>
  );
}
