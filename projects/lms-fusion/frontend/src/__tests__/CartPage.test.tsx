/**
 * Tests for the Cart page loading behavior.
 *
 * Covers:
 * - Shows a skeleton placeholder (not "0 items") while the cart API is loading
 * - Shows the real item count once the cart API responds
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { ToastProvider } from '@/components/ui/Toast';

// ── Mock RTK Query hooks ──

const mockUseGetCartQuery = vi.fn();

vi.mock('@/store/api/endpoints/shop', () => ({
  useGetCartQuery: (...args: unknown[]) => mockUseGetCartQuery(...args),
  useGetProductsQuery: vi.fn(),
  useGetProductQuery: vi.fn(),
  useAddToCartMutation: vi.fn(),
  useUpdateCartItemMutation: () => [vi.fn()],
  useRemoveFromCartMutation: () => [vi.fn()],
  useCreateOrderMutation: vi.fn(),
  useGetOrdersQuery: vi.fn(),
}));

// ── Import page AFTER mocks ──

import CartPage from '@/app/cart/page';

// ── Helpers ──

function createStore() {
  return configureStore({ reducer: (state: any) => state ?? {} });
}

function renderCart() {
  return render(
    <Provider store={createStore()}>
      <ToastProvider>
        <CartPage />
      </ToastProvider>
    </Provider>,
  );
}

const CART_ITEMS = [
  { id: 1, product: 1, product_name: 'LMS Hoodie', product_image: '', product_price: 49.99, quantity: 1, subtotal: 49.99 },
  { id: 2, product: 2, product_name: 'LMS Mug', product_image: '', product_price: 19.99, quantity: 2, subtotal: 39.98 },
];

// ── Tests ──

describe('CartPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a skeleton placeholder instead of "0 items" while the cart is loading', () => {
    mockUseGetCartQuery.mockReturnValue({ data: undefined, isLoading: true });

    const { container } = renderCart();

    // Pulse skeleton rendered in the header item-count slot
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
    // The count must NOT render a premature "0 items in your cart"
    expect(screen.queryByText('0 items in your cart')).not.toBeInTheDocument();
    expect(screen.queryByText('0')).not.toBeInTheDocument();
  });

  it('shows the real item count once the cart API responds', () => {
    mockUseGetCartQuery.mockReturnValue({ data: CART_ITEMS, isLoading: false });

    renderCart();

    expect(screen.getByText('2 items in your cart')).toBeInTheDocument();
    // The pulse placeholder is gone after data arrives
    expect(screen.queryByText('0 items in your cart')).not.toBeInTheDocument();
  });
});
