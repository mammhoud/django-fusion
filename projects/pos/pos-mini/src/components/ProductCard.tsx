import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Product } from '../types';

export interface ProductCardColor {
  bg: string;
  border: string;
  initial: string;
  badge?: string;
  icon?: string;
}

export const PRODUCT_SKELETON_COUNT = 14;

export const PRODUCT_CARD_COLORS: ProductCardColor[] = [
  { bg: 'bg-rose-100/70 dark:bg-rose-900/20', border: 'border-rose-300 dark:border-rose-700/50', initial: 'text-rose-500 dark:text-rose-300', badge: 'bg-rose-500', icon: 'text-rose-400' },
  { bg: 'bg-sky-100/70 dark:bg-sky-900/20', border: 'border-sky-300 dark:border-sky-700/50', initial: 'text-sky-500 dark:text-sky-300', badge: 'bg-sky-500', icon: 'text-sky-400' },
  { bg: 'bg-amber-100/70 dark:bg-amber-900/20', border: 'border-amber-300 dark:border-amber-700/50', initial: 'text-amber-500 dark:text-amber-300', badge: 'bg-amber-500', icon: 'text-amber-400' },
  { bg: 'bg-emerald-100/70 dark:bg-emerald-900/20', border: 'border-emerald-300 dark:border-emerald-700/50', initial: 'text-emerald-500 dark:text-emerald-300', badge: 'bg-emerald-500', icon: 'text-emerald-400' },
  { bg: 'bg-violet-100/70 dark:bg-violet-900/20', border: 'border-violet-300 dark:border-violet-700/50', initial: 'text-violet-500 dark:text-violet-300', badge: 'bg-violet-500', icon: 'text-violet-400' },
  { bg: 'bg-orange-100/70 dark:bg-orange-900/20', border: 'border-orange-300 dark:border-orange-700/50', initial: 'text-orange-500 dark:text-orange-300', badge: 'bg-orange-500', icon: 'text-orange-400' },
  { bg: 'bg-teal-100/70 dark:bg-teal-900/20', border: 'border-teal-300 dark:border-teal-700/50', initial: 'text-teal-500 dark:text-teal-300', badge: 'bg-teal-500', icon: 'text-teal-400' },
  { bg: 'bg-indigo-100/70 dark:bg-indigo-900/20', border: 'border-indigo-300 dark:border-indigo-700/50', initial: 'text-indigo-500 dark:text-indigo-300', badge: 'bg-indigo-500', icon: 'text-indigo-400' },
  { bg: 'bg-pink-100/70 dark:bg-pink-900/20', border: 'border-pink-300 dark:border-pink-700/50', initial: 'text-pink-500 dark:text-pink-300', badge: 'bg-pink-500', icon: 'text-pink-400' },
  { bg: 'bg-lime-100/70 dark:bg-lime-900/20', border: 'border-lime-300 dark:border-lime-700/50', initial: 'text-lime-500 dark:text-lime-300', badge: 'bg-lime-500', icon: 'text-lime-400' },
];

interface ProductCardProps {
  product: Product;
  color: ProductCardColor;
  currency?: string;
  children?: React.ReactNode;
  className?: string;
  isSelected?: boolean;
  selectedClassName?: string;
  index?: number;
}

export default function ProductCard({
  product,
  color,
  currency,
  children,
  className = '',
  isSelected = false,
  selectedClassName = 'bg-teal-100 dark:bg-teal-500/20 border-teal-500 dark:border-teal-500 shadow-lg shadow-teal-500/10',
  index,
}: ProductCardProps) {
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    setImageError(false);
  }, [product.image]);

  const baseClasses = isSelected
    ? selectedClassName
    : `${color.bg} ${color.border}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: (index ?? 0) * 0.04 }}
      whileHover={{ y: -3, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      className={`rounded-xl p-3 sm:p-4 flex flex-col items-center text-center
        border-2 backdrop-blur-sm hover:shadow-lg transition-all duration-300 group relative
        ${baseClasses} ${className}`}
    >
      {/* Product Image */}
      <div className={`w-16 h-16 sm:w-20 sm:h-20 mb-3 rounded-xl overflow-hidden
        flex items-center justify-center border-2 ${isSelected ? 'border-teal-300 dark:border-teal-500/50' : color.border}
        bg-white/70 dark:bg-white/10 shadow-sm`}>
        {product.image && !imageError ? (
          <img
            src={product.image}
            alt={product.name}
            onError={() => setImageError(true)}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <span
              data-testid="product-initial"
              className={`text-2xl sm:text-3xl font-extrabold ${isSelected ? 'text-teal-600 dark:text-teal-400' : color.initial} select-none`}
            >
              {product.name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Product Info */}
      <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white mb-0.5 line-clamp-2 leading-tight">
        {product.name}
      </h3>
      <div className={`font-semibold text-sm sm:text-base mb-0.5 ${isSelected ? 'text-teal-600 dark:text-teal-400' : color.initial}`}>
        {currency} {product.price.toFixed(2)}
      </div>
      <span className={`text-[10px] sm:text-xs ${isSelected ? 'text-teal-500/70 dark:text-teal-300/70' : (color.icon || color.initial)} opacity-60 uppercase tracking-wider mb-2`}>
        / {product.unit}
      </span>

      {children}
    </motion.div>
  );
}

interface ProductCardSkeletonProps {
  className?: string;
}

export function ProductCardSkeleton({ className = '' }: ProductCardSkeletonProps) {
  return (
    <div
      data-testid="product-card-skeleton"
      className={`rounded-xl p-3 sm:p-4 flex flex-col items-center text-center justify-between
        border-2 border-slate-200 dark:border-slate-700/50 backdrop-blur-sm
        bg-slate-100/50 dark:bg-slate-800/30 animate-pulse min-h-[160px] sm:min-h-[180px] ${className}`}
      aria-hidden="true"
    >
      <div className="w-16 h-16 sm:w-20 sm:h-20 mb-3 rounded-xl bg-slate-200 dark:bg-slate-700/50" />
      <div className="w-full flex flex-col items-center gap-2">
        <div className="w-3/4 h-4 rounded bg-slate-200 dark:bg-slate-700/50" />
        <div className="w-1/2 h-3 rounded bg-slate-200 dark:bg-slate-700/50" />
      </div>
      <div className="w-8 h-8 rounded-lg bg-slate-200 dark:bg-slate-700/50 mt-2" />
    </div>
  );
}
