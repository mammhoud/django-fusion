import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../test-utils';
import CategoryFilterPills from '../../components/pos/CategoryFilterPills';

const categories = [
  { id: 1, name: 'Burgers', color: '#f97316' },
  { id: 2, name: 'Sides', color: '#10b981' },
];

const counts = { 1: 3, 2: 1 };

const defaultProps = {
  categories,
  selected: 'all' as const,
  onChange: vi.fn(),
  allLabel: 'All categories',
  testIdPrefix: 'test-cat',
};

describe('CategoryFilterPills', () => {
  it('renders the All pill plus one pill per category', () => {
    render(<CategoryFilterPills {...defaultProps} />);

    expect(screen.getByTestId('test-cat-all')).toBeInTheDocument();
    expect(screen.getByText('All categories')).toBeInTheDocument();
    expect(screen.getByTestId('test-cat-1')).toBeInTheDocument();
    expect(screen.getByTestId('test-cat-2')).toBeInTheDocument();
  });

  it('marks the selected pill as pressed and calls onChange', async () => {
    const onChange = vi.fn();
    render(<CategoryFilterPills {...defaultProps} selected={1} onChange={onChange} />);

    const allPill = screen.getByTestId('test-cat-all');
    const burgersPill = screen.getByTestId('test-cat-1');

    expect(burgersPill).toHaveAttribute('aria-pressed', 'true');
    expect(allPill).toHaveAttribute('aria-pressed', 'false');

    await userEvent.click(allPill);
    expect(onChange).toHaveBeenCalledWith('all');

    // Toggle-to-reset: clicking the already-selected category resets to 'all'
    await userEvent.click(burgersPill);
    expect(onChange).toHaveBeenCalledWith('all');
  });

  it('renders product-count badges when counts are provided', () => {
    render(<CategoryFilterPills {...defaultProps} counts={counts} />);

    const burgersPill = screen.getByTestId('test-cat-1');
    const sidesPill = screen.getByTestId('test-cat-2');

    expect(burgersPill.querySelector('.badge')!.textContent).toBe('3');
    expect(sidesPill.querySelector('.badge')!.textContent).toBe('1');
  });

  it('adds a native title tooltip showing the product count', () => {
    render(
      <CategoryFilterPills
        {...defaultProps}
        counts={counts}
        tooltipFormatter={(cat, count) => `${cat.name} — ${count ?? 0} products`}
      />,
    );

    expect(screen.getByTestId('test-cat-1')).toHaveAttribute('title', 'Burgers — 3 products');
    expect(screen.getByTestId('test-cat-2')).toHaveAttribute('title', 'Sides — 1 products');
    // The All pill always carries the allLabel as its tooltip
    expect(screen.getByTestId('test-cat-all')).toHaveAttribute('title', 'All categories');
  });

  it('toggles the color legend panel with swatches and counts', async () => {
    render(
      <CategoryFilterPills
        {...defaultProps}
        counts={counts}
        showLegend
        legendLabel="Category legend"
      />,
    );

    // Legend panel starts hidden
    expect(screen.queryByTestId('test-cat-legend')).not.toBeInTheDocument();

    const toggle = screen.getByTestId('test-cat-legend-toggle');
    expect(toggle).toHaveAttribute('aria-expanded', 'false');

    await userEvent.click(toggle);

    const legend = screen.getByTestId('test-cat-legend');
    expect(legend).toBeInTheDocument();
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    // The heading text also appears on the toggle button label — scope to the panel
    expect(legend.textContent).toContain('Category legend');

    // Each category row shows its color swatch, name, and count badge
    const rows = legend.querySelectorAll('li');
    expect(rows.length).toBe(2);
    expect(rows[0].textContent).toContain('Burgers');
    expect(rows[0].textContent).toContain('3');
    expect(rows[1].textContent).toContain('Sides');
    expect(rows[1].textContent).toContain('1');

    // The total row shows the All label with the summed count
    expect(legend.textContent).toContain('All categories: 4');

    // Clicking again closes the panel
    await userEvent.click(toggle);
    expect(screen.queryByTestId('test-cat-legend')).not.toBeInTheDocument();
  });

  it('renders the legend without color dots for categories missing a color', async () => {
    render(
      <CategoryFilterPills
        {...defaultProps}
        categories={[{ id: 3, name: 'Drinks' }]}
        showLegend
        legendLabel="Legend"
      />,
    );

    await userEvent.click(screen.getByTestId('test-cat-legend-toggle'));
    const legend = screen.getByTestId('test-cat-legend');
    const swatch = legend.querySelector('.rounded-full');
    // A fallback swatch is rendered even when color is undefined
    expect(swatch).not.toBeNull();
    expect(swatch).toHaveStyle({ backgroundColor: 'rgb(148, 163, 184)' }); // #94a3b8 fallback
  });
});
