import { motion } from 'framer-motion';
import { useState, useEffect, memo } from 'react';
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
  { bg: 'bg-primary/10', border: 'border-primary/30', initial: 'text-primary', badge: 'bg-primary', icon: 'text-teal-400' },
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

const ProductCard = memo(function ProductCard({
  product,
  color,
  currency,
  children,
  className = '',
  isSelected = false,
  selectedClassName = 'bg-primary/10 dark:bg-primary/20 border-primary dark:border-primary shadow-lg shadow-primary/10',
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
      whileHover={{ y: -2, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`rounded-lg p-2 flex flex-col items-center text-center
        border backdrop-blur-sm hover:shadow-md transition-all duration-200 group relative
        ${baseClasses} ${className}`}
    >
      {/* Product Image — smaller, fixed size */}
      <div className={`w-12 h-12 mb-1.5 rounded-lg overflow-hidden
        flex items-center justify-center border ${isSelected ? 'border-primary/50 dark:border-primary/50' : color.border}
        bg-base-100/70 shadow-sm shrink-0`}>
        {product.image && !imageError ? (
          <img
            src={product.image}
            alt={product.name}
            onError={() => setImageError(true)}
            className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <span
              data-testid="product-initial"
              className={`text-lg font-extrabold ${isSelected ? 'text-primary dark:text-primary/80' : color.initial} select-none`}
            >
              {product.name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Product Info — compact */}
      <h3
        className="text-xs font-bold text-base-content leading-tight line-clamp-1 w-full"
        title={product.description || product.name}
      >
        {product.name}
      </h3>

      {/* Price row */}
      <div className={`font-semibold text-xs ${isSelected ? 'text-primary dark:text-primary/80' : color.initial}`}>
        {currency} {product.price.toFixed(2)}
      </div>

      {/* Unit label */}
      <span className={`text-[9px] ${isSelected ? 'text-primary/70 dark:text-primary/70' : (color.icon || color.initial)} opacity-50 uppercase tracking-wider`}>
        / {product.unit}
      </span>

      {/* Barcode badge — shown on hover */}
      {product.barcode && (
        <span
          title={`SKU: ${product.barcode}`}
          className="text-[8px] mt-0.5 px-1.5 py-[1px] rounded-full
            bg-base-content/10 text-base-content/40
            group-hover:opacity-100 opacity-0 transition-opacity duration-200
            font-mono tracking-wider truncate max-w-full"
        >
          {product.barcode}
        </span>
      )}

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
      className={`rounded-lg p-2 flex flex-col items-center text-center
        border border-slate-200 dark:border-slate-700/50 backdrop-blur-sm
        bg-base-200/50 animate-pulse min-h-[120px] ${className}`}
      aria-hidden="true"
    >
      <div className="w-12 h-12 mb-1.5 rounded-lg bg-base-300/50/50" />
      <div className="w-full flex flex-col items-center gap-1">
        <div className="w-3/4 h-3 rounded bg-base-300/50/50" />
        <div className="w-1/2 h-2 rounded bg-base-300/50/50" />
      </div>
    </div>
  );
}
