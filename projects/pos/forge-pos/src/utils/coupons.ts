import type { Coupon } from '../types';

/**
 * Coupon helpers for the point-of-sale checkout.
 *
 * Coupons are stored in the database (see the admin Coupons page) and fetched
 * via the `get_active_coupons` Tauri command. These helpers are pure — they
 * operate on the coupon list passed in by the caller.
 */

/** Find an active coupon by code (case-insensitive), honoring the minimum-subtotal rule. */
export function lookupCoupon(coupons: Coupon[], rawCode: string, subtotal: number): Coupon | null {
  const code = rawCode.trim().toUpperCase();
  if (!code) return null;
  const coupon = coupons.find(c => c.is_active && c.code.toUpperCase() === code);
  if (!coupon) return null;
  if (coupon.min_subtotal != null && subtotal < coupon.min_subtotal) return null;
  return coupon;
}

/** Compute the discount amount a coupon yields for a given subtotal. */
export function applyCoupon(coupon: Coupon, subtotal: number): number {
  if (coupon.kind === 'percent') {
    return (subtotal * coupon.value) / 100;
  }
  return Math.min(coupon.value, subtotal);
}
