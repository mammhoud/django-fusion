import { useState, useEffect, memo } from 'react';
import { Product } from '../../types';

export interface ProductCardColor {
  bg: string;
  border: string;
  initial: string;
  badge?: string;
  icon?: string;
}

export const PRODUCT_SKELETON_COUNT = 14;

export const PRODUCT_CARD_COLORS: ProductCardColor[] = [
  { bg: 'bg-primary/10 dark:bg-primary/15', border: 'border-primary/30 dark:border-primary/40', initial: 'text-primary dark:text-primary/80', badge: 'bg-primary', icon: 'text-primary/60' },
  { bg: 'bg-secondary/10 dark:bg-secondary/15', border: 'border-secondary/30 dark:border-secondary/40', initial: 'text-secondary dark:text-secondary/80', badge: 'bg-secondary', icon: 'text-secondary/60' },
  { bg: 'bg-accent/10 dark:bg-accent/15', border: 'border-accent/30 dark:border-accent/40', initial: 'text-accent dark:text-accent/80', badge: 'bg-accent', icon: 'text-accent/60' },
  { bg: 'bg-info/10 dark:bg-info/15', border: 'border-info/30 dark:border-info/40', initial: 'text-info dark:text-info/80', badge: 'bg-info', icon: 'text-info/60' },
  { bg: 'bg-success/10 dark:bg-success/15', border: 'border-success/30 dark:border-success/40', initial: 'text-success dark:text-success/80', badge: 'bg-success', icon: 'text-success/60' },
  { bg: 'bg-warning/10 dark:bg-warning/15', border: 'border-warning/30 dark:border-warning/40', initial: 'text-warning dark:text-warning/80', badge: 'bg-warning', icon: 'text-warning/60' },
  { bg: 'bg-error/10 dark:bg-error/15', border: 'border-error/30 dark:border-error/40', initial: 'text-error dark:text-error/80', badge: 'bg-error', icon: 'text-error/60' },
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
    <div
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
      <div className={`w-12 h-12 mb-1.5 rounded-full overflow-hidden
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
      <div className={`font-semibold text-sm tabular-nums ${isSelected ? 'text-primary dark:text-primary/80' : color.initial}`}>
        {currency} {product.price.toFixed(2)}
      </div>

      {/* Unit label */}
      <span className={`text-[10px] tabular-nums ${isSelected ? 'text-primary/70 dark:text-primary/70' : (color.icon || color.initial)} opacity-50 uppercase tracking-wider`}>
        / {product.unit}
      </span>

      {/* Barcode badge — shown on hover */}
      {product.barcode && (
        <span
          title={`SKU: ${product.barcode}`}
          className="text-[10px] mt-0.5 px-1.5 py-[1px] rounded-full
            bg-base-content/10 text-base-content/40
            group-hover:opacity-100 opacity-0 transition-opacity duration-200
            font-mono tracking-wider truncate max-w-full"
        >
          {product.barcode}
        </span>
      )}

      {children}
    </div>
  );
});

interface ProductCardSkeletonProps {
  className?: string;
}

export default ProductCard;

export function ProductCardSkeleton({ className = '' }: ProductCardSkeletonProps) {
  return (
    <div
      data-testid="product-card-skeleton"
      className={`rounded-lg p-2 flex flex-col items-center text-center
        border border-base-300/30 dark:border-base-300/20 backdrop-blur-sm
        bg-base-200/50 animate-pulse min-h-[120px] ${className}`}
      aria-hidden="true"
    >
      <div className="w-12 h-12 mb-1.5 rounded-full bg-base-300/50" />
      <div className="w-full flex flex-col items-center gap-1">
        <div className="w-3/4 h-3 rounded bg-base-300/50" />
        <div className="w-1/2 h-2 rounded bg-base-300/50" />
      </div>
    </div>
  );
}
