/**
 * Unit tests for the Accordion component.
 *
 * Covers:
 * - Renders all items with titles
 * - Toggles open/close on click
 * - Single mode: only one item open at a time
 * - Multiple mode: can open multiple items
 * - defaultOpen opens items initially
 * - Empty state (no items → null)
 * - onToggle callback
 * - Size variants (sm, md, lg)
 * - Compact mode (no border)
 * - Icon rendering
 * - Content visibility (hidden when closed, shown when open)
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Accordion from '@/components/ui/Accordion';
import type { AccordionItem } from '@/components/ui/Accordion';
import { HiInformationCircle } from 'react-icons/hi';

const sampleItems: AccordionItem[] = [
  { id: 'item-1', title: 'Item One', content: <div>Content One</div> },
  { id: 'item-2', title: 'Item Two', content: <div>Content Two</div> },
  { id: 'item-3', title: 'Item Three', content: <div>Content Three</div> },
];

describe('Accordion', () => {
  it('renders all item titles', () => {
    render(<Accordion items={sampleItems} />);
    expect(screen.getByText('Item One')).toBeInTheDocument();
    expect(screen.getByText('Item Two')).toBeInTheDocument();
    expect(screen.getByText('Item Three')).toBeInTheDocument();
  });

  it('returns null when items array is empty', () => {
    const { container } = render(<Accordion items={[]} />);
    expect(container.innerHTML).toBe('');
  });

  it('hides content by default', () => {
    render(<Accordion items={sampleItems} />);
    expect(screen.queryByText('Content One')).not.toBeInTheDocument();
  });

  it('shows content when clicking an item header', () => {
    render(<Accordion items={sampleItems} />);
    fireEvent.click(screen.getByText('Item One'));
    expect(screen.getByText('Content One')).toBeInTheDocument();
  });

  it('hides content when clicking an open item header again', async () => {
    render(<Accordion items={sampleItems} />);
    fireEvent.click(screen.getByText('Item One'));
    expect(screen.getByText('Content One')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Item One'));
    // AnimatePresence keeps exiting elements in DOM during exit animation
    await vi.waitFor(() => {
      expect(screen.queryByText('Content One')).not.toBeInTheDocument();
    });
  });

  it('single mode: only one item open at a time', async () => {
    render(<Accordion items={sampleItems} multiple={false} />);
    fireEvent.click(screen.getByText('Item One'));
    expect(screen.getByText('Content One')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Item Two'));
    // AnimatePresence keeps exiting elements in DOM during exit animation
    await vi.waitFor(() => {
      expect(screen.queryByText('Content One')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Content Two')).toBeInTheDocument();
  });

  it('multiple mode: can open multiple items simultaneously', () => {
    render(<Accordion items={sampleItems} multiple />);
    fireEvent.click(screen.getByText('Item One'));
    fireEvent.click(screen.getByText('Item Two'));

    expect(screen.getByText('Content One')).toBeInTheDocument();
    expect(screen.getByText('Content Two')).toBeInTheDocument();
  });

  it('defaultOpen opens specified items on mount', () => {
    render(<Accordion items={sampleItems} defaultOpen={['item-1', 'item-3']} />);
    expect(screen.getByText('Content One')).toBeInTheDocument();
    expect(screen.getByText('Content Three')).toBeInTheDocument();
    expect(screen.queryByText('Content Two')).not.toBeInTheDocument();
  });

  it('calls onToggle when an item is opened', () => {
    const onToggle = vi.fn();
    render(<Accordion items={sampleItems} onToggle={onToggle} />);
    fireEvent.click(screen.getByText('Item One'));
    expect(onToggle).toHaveBeenCalledWith('item-1', true);
  });

  it('calls onToggle when an item is closed', () => {
    const onToggle = vi.fn();
    render(<Accordion items={sampleItems} defaultOpen={['item-1']} onToggle={onToggle} />);
    fireEvent.click(screen.getByText('Item One'));
    expect(onToggle).toHaveBeenCalledWith('item-1', false);
  });

  it('renders aria-expanded attribute', () => {
    render(<Accordion items={sampleItems} defaultOpen={['item-1']} />);
    const btn1 = screen.getByText('Item One').closest('button');
    const btn2 = screen.getByText('Item Two').closest('button');
    expect(btn1).toHaveAttribute('aria-expanded', 'true');
    expect(btn2).toHaveAttribute('aria-expanded', 'false');
  });

  it('renders with accordion ARIA role', () => {
    const { container } = render(<Accordion items={sampleItems} />);
    const region = container.querySelector('[role="region"]');
    expect(region).toHaveAttribute('aria-label', 'Accordion');
  });

  it('supports size variants', () => {
    const { container, rerender } = render(<Accordion items={sampleItems} size="sm" />);
    const smallBtn = screen.getByText('Item One').closest('button');
    expect(smallBtn?.className).toContain('text-xs');

    rerender(<Accordion items={sampleItems} size="lg" />);
    const largeBtn = screen.getByText('Item One').closest('button');
    expect(largeBtn?.className).toContain('text-base');
  });

  it('renders icons when provided', () => {
    const itemsWithIcon: AccordionItem[] = [
      { id: 'icon-item', title: 'Icon Item', content: 'Content', icon: <HiInformationCircle data-testid="accordion-icon" /> },
    ];
    render(<Accordion items={itemsWithIcon} />);
    expect(screen.getByTestId('accordion-icon')).toBeInTheDocument();
  });

  it('does not render border in compact mode', () => {
    const { container } = render(<Accordion items={sampleItems} compact />);
    const outer = container.querySelector('.divide-y');
    expect(outer?.className).not.toContain('border');
    expect(outer?.className).not.toContain('rounded-xl');
  });
});
