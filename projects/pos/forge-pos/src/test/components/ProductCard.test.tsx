import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ProductCard, { ProductCardSkeleton, PRODUCT_CARD_COLORS, productAccentColor, accentColorFromSeed } from '../../components/pos/ProductCard';
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
    expect(card).toHaveClass('border-primary');
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

describe('productAccentColor', () => {
  it('is deterministic — same product always yields the same color', () => {
    expect(productAccentColor(mockProduct)).toBe(productAccentColor(mockProduct));
    expect(productAccentColor(mockProductWithImage)).toBe(productAccentColor(mockProductWithImage));
  });

  it('returns a valid #rrggbb hex string', () => {
    expect(productAccentColor(mockProduct)).toMatch(/^#[0-9a-fA-F]{6}$/);
  });

  it('yields distinct colors for distinct products', () => {
    const a = productAccentColor(mockProduct);
    const b = productAccentColor(mockProductWithImage);
    // Different id + name seeds must not collide for the fixture set.
    expect(a).not.toBe(b);
  });

  it('productAccentColor and accentColorFromSeed agree on the same seed', () => {
    expect(accentColorFromSeed(`${mockProduct.id}:${mockProduct.name}`))
      .toBe(productAccentColor(mockProduct));
  });

  it('accentColorFromSeed is deterministic and distinct for different seeds', () => {
    const a = accentColorFromSeed('Chicken Burger');
    const b = accentColorFromSeed('French Fries');
    expect(a).toMatch(/^#[0-9a-fA-F]{6}$/);
    expect(b).toMatch(/^#[0-9a-fA-F]{6}$/);
    expect(accentColorFromSeed('Chicken Burger')).toBe(a);
    expect(a).not.toBe(b);
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
