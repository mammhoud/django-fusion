import { useState, memo } from 'react';
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
  /**
   * Hex color (e.g. `#f97316`) from the product's category, or a generated
   * per-product accent (see `productAccentColor`). When provided it tints the
   * card background/border/initial instead of the rotating palette.
   */
  categoryColor?: string | null;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  /**
   * Show the bottom Edit/Delete action row. Defaults to `true` when at least
   * one of onEdit/onDelete is provided. Pass `false` on screens where the card
   * is only used to add to cart (e.g. Sale) so the dead buttons never render.
   */
  showActions?: boolean;
}

/** Parse a hex color (#rgb, #rrggbb, #rrggbbaa) into rgba() with the given alpha. */
export function hexToRgba(hex: string, alpha: number): string {
  let h = hex.trim().replace(/^#/, '');
  if (h.length === 3) {
    h = h.split('').map(c => c + c).join('');
  }
  if (h.length !== 6 && h.length !== 8) return `rgba(148, 163, 184, ${alpha})`; // slate-400 fallback
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/** Convert HSL (h: 0-360, s: 0-100, l: 0-100) to a #rrggbb hex string. */
function hslToHex(h: number, s: number, l: number): string {
  h = ((h % 360) + 360) % 360;
  s /= 100;
  l /= 100;
  const a = s * Math.min(l, 1 - l);
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(-1, Math.min(k - 3, Math.min(9 - k, 1)));
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

/**
 * Deterministic unique accent color from an arbitrary seed string, using
 * golden-angle hue spacing (≈137.5°) so consecutive items get visually
 * distinct hues instead of repeating a small palette. Lightness 45 keeps
 * white text on the accent readable across all hues (yellow-ish golden-angle
 * hues at 55% would fail contrast).
 */
export function accentColorFromSeed(seed: string): string {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (Math.imul(hash, 31) + seed.charCodeAt(i)) | 0;
  }
  const hue = (Math.abs(hash) * 137.508) % 360;
  return hslToHex(hue, 72, 45);
}

/**
 * Deterministic unique accent color for a product card, derived from the
 * product's id + name. Golden-angle hue spacing (≈137.5°) keeps consecutive
 * products visually distinct instead of cycling the same 7-palette colors.
 * Returns a hex string that can be passed through `categoryColor` so the
 * existing inline-tint rendering (bg/border/initial/image) is reused.
 */
export function productAccentColor(product: Product): string {
  return accentColorFromSeed(`${product.id ?? ''}:${product.name}`);
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
  categoryColor,
  onClick,
  onEdit,
  onDelete,
  showActions,
}: ProductCardProps) {
  const hasActions = showActions ?? !!(onEdit || onDelete);
  const [imageError, setImageError] = useState(false);
  // Category-driven tint overrides the rotating palette (inline styles because
  // category colors are arbitrary hex values, not Tailwind theme utilities).
  const hasCategoryColor = !!categoryColor && !isSelected;
  const baseClasses = isSelected
    ? selectedClassName
    : hasCategoryColor
      ? ''
      : `${color.bg} ${color.border}`;
  const cardStyle = hasCategoryColor
    ? {
        backgroundColor: hexToRgba(categoryColor as string, 0.12),
        borderColor: hexToRgba(categoryColor as string, 0.4),
        animationDelay: `${(index ?? 0) * 40}ms`,
      }
    : { animationDelay: `${(index ?? 0) * 40}ms` };

  const accentStyle = hasCategoryColor ? { color: categoryColor as string } : undefined;
  const mutedAccentStyle = hasCategoryColor ? { color: hexToRgba(categoryColor as string, 0.75) } : undefined;
  const imageBorderStyle = hasCategoryColor
    ? { borderColor: hexToRgba(categoryColor as string, 0.5) }
    : undefined;

  return (
    <div
      className={`rounded-xl p-2 flex flex-col border backdrop-blur-sm
        transition-all duration-200 group relative cursor-pointer select-none animate--slide-up
        ${baseClasses} ${className}
        hover:shadow-lg hover:-translate-y-0.5 active:scale-[0.98]`}
      style={cardStyle}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick?.(); } }}
    >
      {/* Top section: Image + Name + Price */}
      <div className="flex flex-col items-center text-center flex-1 min-h-0 px-0.5">
        {/* Product Image */}
        <div className={`w-11 h-11 mb-1 rounded-full overflow-hidden flex items-center justify-center border
          ${isSelected ? 'border-primary/50 dark:border-primary/50' : color.border}
          bg-base-100/70 shadow-sm shrink-0`}
          style={imageBorderStyle}>
          {product.image && !imageError ? (
            <img
              src={product.image}
              alt={product.name}
              onError={() => setImageError(true)}
              className="w-full h-full object-contain group-hover:scale-110 transition-transform duration-300"
            />
          ) : (
            <span
              data-testid="product-initial"
              className={`text-base font-extrabold ${isSelected ? 'text-primary dark:text-primary/80' : (hasCategoryColor ? '' : color.initial)} select-none`}
              style={accentStyle}
            >
              {product.name.charAt(0).toUpperCase()}
            </span>
          )}
        </div>

        {/* Name */}
        <h3 className="text-[11px] font-bold text-base-content leading-tight line-clamp-1 w-full" title={product.name}>
          {product.name}
        </h3>

        {/* Price */}
        <div className={`font-semibold text-xs tabular-nums ${isSelected ? 'text-primary dark:text-primary/80' : (hasCategoryColor ? '' : color.initial)}`} style={accentStyle}>
          {currency} {product.price.toFixed(2)}
        </div>

        {/* Unit */}
        <span className={`text-[9px] tabular-nums ${isSelected ? 'text-primary/70 dark:text-primary/70' : (hasCategoryColor ? '' : (color.icon || color.initial))} opacity-50 uppercase tracking-wider`} style={mutedAccentStyle}>
          / {product.unit}
        </span>

        {children}
      </div>

      {/* Bottom: Full-width action buttons row (only when edit/delete wired) */}
      {hasActions && (
        <div className="flex gap-1 pt-1.5 mt-1.5 border-t border-base-300/30 w-full opacity-100 transition-opacity duration-200">
          <button
            onClick={(e) => { e.stopPropagation(); onEdit?.(); }}
            className="flex-1 flex items-center justify-center gap-1 py-1 rounded-lg text-[10px] font-medium
              text-primary bg-primary/10 hover:bg-primary/20 active:scale-[0.97] transition-all"
            aria-label="Edit product"
          >
            <span className="icon-[tabler--pencil] w-3 h-3" />
            Edit
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete?.(); }}
            className="flex-1 flex items-center justify-center gap-1 py-1 rounded-lg text-[10px] font-medium
              text-error bg-error/10 hover:bg-error/20 active:scale-[0.97] transition-all"
            aria-label="Delete product"
          >
            <span className="icon-[tabler--trash] w-3 h-3" />
            Delete
          </button>
        </div>
      )}
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
