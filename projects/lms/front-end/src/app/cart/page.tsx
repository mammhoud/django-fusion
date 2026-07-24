'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiShoppingCart, HiTrash, HiMinus, HiPlus, HiArrowLeft } from 'react-icons/hi';
import { useGetCartQuery, useUpdateCartItemMutation, useRemoveFromCartMutation } from '@/store/api/endpoints/shop';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import EmptyState from '@/components/ui/EmptyState';

export default function CartPage() {
  const { data: cart, isLoading } = useGetCartQuery();
  const [updateItem] = useUpdateCartItemMutation();
  const [removeItem] = useRemoveFromCartMutation();

  const total = cart?.reduce((sum, item) => sum + item.subtotal, 0) ?? 0;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-500 mt-1">{cart?.length ?? 0} items in your cart</p>
        </div>
        <Link href="/shop" className="flex items-center gap-2 text-[rgb(var(--ctc-primary))] hover:text-[rgb(var(--ctc-primary-dark))] font-medium">
          <HiArrowLeft className="w-4 h-4" /> Continue Shopping
        </Link>
      </div>

      {isLoading ? (
        <LoadingSkeleton variant="list" count={2} />
      ) : !cart || cart.length === 0 ? (
        <EmptyState icon="shop" title="Your cart is empty" description="Browse our shop and add items to your cart" actionLabel="Browse Shop" actionHref="/shop" />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            {cart.map((item, idx) => (
              <motion.div key={item.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: idx * 0.05 }}
                className="card p-4 flex items-center gap-4">
                <div className="w-20 h-20 card-gradient rounded-lg flex items-center justify-center flex-shrink-0">
                  <HiShoppingCart className="w-8 h-8 text-white/60" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900">{item.product_name}</h3>
                  <p className="text-sm text-gray-500">${item.product_price} each</p>
                  <div className="flex items-center gap-2 mt-2">
                    <button onClick={() => item.quantity > 1 && updateItem({ item_id: item.id, quantity: item.quantity - 1 })}
                      className="w-8 h-8 rounded border border-gray-300 flex items-center justify-center text-gray-600 hover:bg-gray-50 transition-colors">
                      <HiMinus className="w-3 h-3" />
                    </button>
                    <span className="w-10 text-center font-medium">{item.quantity}</span>
                    <button onClick={() => updateItem({ item_id: item.id, quantity: item.quantity + 1 })}
                      className="w-8 h-8 rounded border border-gray-300 flex items-center justify-center text-gray-600 hover:bg-gray-50 transition-colors">
                      <HiPlus className="w-3 h-3" />
                    </button>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900">${item.subtotal}</div>
                  <button onClick={() => removeItem(item.id)}
                    className="text-red-500 hover:text-red-700 mt-1 transition-colors">
                    <HiTrash className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="card p-6 h-fit lg:sticky lg:top-24">
            <h3 className="font-semibold text-gray-900 mb-4">Order Summary</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-gray-500">
                <span>Subtotal</span><span>${total}</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>Shipping</span><span className="text-green-600">Free</span>
              </div>
              <hr className="my-2" />
              <div className="flex justify-between font-bold text-gray-900 text-lg">
                <span>Total</span><span>${total}</span>
              </div>
            </div>
            <Link href="/check-out" className="btn-primary w-full mt-6 text-center block">
              Proceed to Checkout
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
