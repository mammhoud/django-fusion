import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProductCard, { ProductCardSkeleton, PRODUCT_CARD_COLORS } from '../../components/pos/ProductCard';
import { Product } from '../../types';

const mockProduct: Product = {
  id: 1,
  name: 'Chicken Burger',
  price: 350,
  unit: 'item',
  category_id: 1,
  image: null,
  product_type: 'product',
};

const mockProductWithImage: Product = {
  id: 2,
  name: 'French Fries',
  price: 200,
  unit: 'plate',
  category_id: 2,
  image: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  product_type: 'product',
};

describe('ProductCard', () => {
  it('renders product name, price and unit', () => {
    render(<ProductCard product={mockProduct} color={PRODUCT_CARD_COLORS[0]} />);

    expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    expect(screen.getByText(/350\.00/)).toBeInTheDocument();
    expect(screen.getByText(/item/)).toBeInTheDocument();
  });

  it('displays product initial when no image is provided', () => {
    render(<ProductCard product={mockProduct} color={PRODUCT_CARD_COLORS[0]} />);

    const initial = screen.getByTestId('product-initial');
    expect(initial).toBeInTheDocument();
    expect(initial).toHaveTextContent('C');
  });

  it('renders product image when image is provided', () => {
    render(<ProductCard product={mockProductWithImage} color={PRODUCT_CARD_COLORS[1]} />);

    const img = screen.getByAltText('French Fries');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', mockProductWithImage.image);
  });

  it('calls addToCart when add button is clicked', async () => {
    const handleAdd = vi.fn();
    render(
      <ProductCard product={mockProduct} color={PRODUCT_CARD_COLORS[0]}>
        <button onClick={handleAdd}>Add</button>
      </ProductCard>
    );

    await userEvent.click(screen.getByText('Add'));
    expect(handleAdd).toHaveBeenCalledTimes(1);
  });

  it('applies selected styling when isSelected is true', () => {
    render(<ProductCard product={mockProduct} color={PRODUCT_CARD_COLORS[0]} isSelected />);

    const card = screen.getByText('Chicken Burger').closest('[class*="rounded-xl"]');
    expect(card).toHaveClass('border-teal-500');
  });

  it('renders children inside the card', () => {
    render(
      <ProductCard product={mockProduct} color={PRODUCT_CARD_COLORS[0]}>
        <span data-testid="child">Child Content</span>
      </ProductCard>
    );

    expect(screen.getByTestId('child')).toBeInTheDocument();
  });
});

describe('ProductCardSkeleton', () => {
  it('renders skeleton placeholder with aria-hidden', () => {
    render(<ProductCardSkeleton />);

    const skeleton = screen.getByTestId('product-card-skeleton');
    expect(skeleton).toHaveAttribute('aria-hidden', 'true');
  });

  it('applies custom className', () => {
    render(<ProductCardSkeleton className="custom-class" />);

    const skeleton = screen.getByTestId('product-card-skeleton');
    expect(skeleton).toHaveClass('custom-class');
  });
});
