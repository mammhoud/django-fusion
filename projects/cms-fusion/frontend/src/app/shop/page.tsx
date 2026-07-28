'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { HiShoppingCart, HiStar, HiSearch } from 'react-icons/hi';
import { useGetProductsQuery } from '@/store/api/endpoints/shop';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

export default function ShopPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const { data, isLoading } = useGetProductsQuery({ page, search });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Merch Shop</h1>
          <p className="text-gray-500 mt-2">Branded merchandise and learning resources</p>
        </div>
        <Link href="/cart" className="flex items-center gap-2 bg-[rgb(var(--fu-primary))] text-white px-4 py-2 rounded-lg hover:bg-[rgb(var(--fu-primary-dark))] transition-colors">
          <HiShoppingCart className="w-5 h-5" />
          <span className="font-medium">Cart</span>
        </Link>
      </div>

      <div className="mb-8">
        <div className="relative max-w-md">
          <HiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input type="text" placeholder="Search products..." value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="input-field pl-10" />
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1,2,3,4].map(i => (
            <div key={i} className="card p-4 animate-pulse">
              <div className="bg-gray-200 h-32 rounded mb-4" />
              <div className="bg-gray-200 h-4 w-3/4 rounded mb-2" />
              <div className="bg-gray-200 h-4 w-1/2 rounded" />
            </div>
          ))}
        </div>
      ) : data && data.results.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {data?.results.map((product, idx) => (
              <motion.div key={product.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.03 }}
                className="card overflow-hidden group">
                <div className="bg-gradient-to-br card-gradient h-32 flex items-center justify-center">
                  <HiShoppingCart className="w-12 h-12 text-white/60" />
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 group-hover:text-[rgb(var(--fu-primary))] transition-colors line-clamp-1">{product.name}</h3>
                  <p className="text-sm text-gray-500 line-clamp-1 mt-1">{product.description}</p>
                  <div className="flex items-center justify-between mt-3">
                    <span className="font-bold text-[rgb(var(--fu-primary))] text-lg">
                      {product.discounted_price ? (
                        <><span className="line-through text-gray-400 text-sm mr-1">${product.price}</span>${product.discounted_price}</>
                      ) : `$${product.price}`}
                    </span>
                    {product.stock > 0 ? (
                      <span className="text-xs text-green-600 font-medium">In Stock</span>
                    ) : (
                      <span className="text-xs text-red-500 font-medium">Out of Stock</span>
                    )}
                  </div>
                  <Link href={`/shop-details/${product.id}`}
                    className="mt-3 w-full text-center text-sm text-[rgb(var(--fu-primary))] font-medium block hover:text-[rgb(var(--fu-primary-dark))] border border-[rgb(var(--fu-primary))] rounded-lg py-2 hover:bg-[rgb(var(--fu-primary))]/5 transition-colors">
                    View Details
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>

          {data && Math.ceil(data.count / 12) > 1 && (
            <div className="flex justify-center gap-2 mt-10">
              {Array.from({ length: Math.ceil(data.count / 12) }, (_, i) => i + 1).map(p => (
                <button key={p} onClick={() => setPage(p)}
                  className={`w-10 h-10 rounded-lg font-medium transition-colors ${p === page ? 'bg-[rgb(var(--fu-primary))] text-white' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'}`}>{p}</button>
              ))}
            </div>
          )}
        </>
      ) : (
        <EmptyState icon="shop" />
      )}
    </div>
  );
}
