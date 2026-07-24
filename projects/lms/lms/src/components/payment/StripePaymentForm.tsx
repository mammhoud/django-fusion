'use client';

import { useState } from 'react';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { HiLockClosed, HiCheckCircle, HiXCircle } from 'react-icons/hi';

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''
);

interface StripeFormProps {
  clientSecret: string;
  onSuccess: () => void;
  onError: (error: string) => void;
}

function StripeCheckoutForm({ onSuccess, onError }: StripeFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setIsProcessing(true);
    setMessage('');

    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment/success`,
      },
      redirect: 'if_required',
    });

    if (error) {
      setMessage(error.message || 'Payment failed');
      onError(error.message || 'Payment failed');
    } else if (paymentIntent && paymentIntent.status === 'succeeded') {
      setMessage('Payment successful!');
      onSuccess();
    } else if (paymentIntent) {
      setMessage(`Payment status: ${paymentIntent.status}`);
      if (paymentIntent.status === 'requires_action') {
        // 3D Secure — Stripe handles this automatically
        return;
      }
      onSuccess();
    }

    setIsProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
        <PaymentElement
          options={{
            layout: 'tabs' as const,
          }}
        />
      </div>

      {message && (
        <div className={`flex items-center gap-2 px-4 py-3 rounded-xl text-sm ${
          message.includes('successful')
            ? 'bg-green-50 text-green-700'
            : message.includes('status')
            ? 'bg-blue-50 text-blue-700'
            : 'bg-red-50 text-red-700'
        }`}>
          {message.includes('successful') ? (
            <HiCheckCircle className="w-5 h-5 flex-shrink-0" />
          ) : message.includes('status') ? (
            <HiCheckCircle className="w-5 h-5 flex-shrink-0" />
          ) : (
            <HiXCircle className="w-5 h-5 flex-shrink-0" />
          )}
          {message}
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || isProcessing}
        className="btn-primary w-full flex items-center justify-center gap-2"
      >
        {isProcessing ? (
          <>
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Processing Payment...
          </>
        ) : (
          <>
            <HiLockClosed className="w-4 h-4" />
            Pay Now
          </>
        )}
      </button>
    </form>
  );
}

export default function StripePaymentForm(props: StripeFormProps) {
  if (!props.clientSecret) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-xl text-sm">
        Stripe is not configured. Please set NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY in your environment.
      </div>
    );
  }

  return (
    <Elements stripe={stripePromise} options={{ clientSecret: props.clientSecret }}>
      <StripeCheckoutForm {...props} />
    </Elements>
  );
}
