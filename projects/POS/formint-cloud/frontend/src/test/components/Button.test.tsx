import { describe, it, expect, vi } from 'vitest';
import { render, screen, userEvent } from '../test-utils';
import Button from '../../components/ui/Button';

describe('Button component', () => {
  it('renders children with base btn class + variant', () => {
    render(<Button>Save</Button>);
    const btn = screen.getByRole('button', { name: 'Save' });
    expect(btn).toHaveClass('btn', 'btn-primary');
  });

  it('applies variant + size classes', () => {
    render(<Button variant="error" size="sm">Delete</Button>);
    const btn = screen.getByRole('button', { name: 'Delete' });
    expect(btn).toHaveClass('btn-error', 'btn-sm');
  });

  it('applies gap classes for icon-label spacing', () => {
    render(<Button gap="lg" iconStart={<span data-testid="icon" />}>Label</Button>);
    const btn = screen.getByRole('button', { name: 'Label' });
    expect(btn).toHaveClass('gap-3');
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('applies margin placement classes (RTL-aware)', () => {
    render(<Button margin="start">A</Button>);
    expect(screen.getByRole('button', { name: 'A' })).toHaveClass('ms-2');
  });

  it('renders block + square shape modifiers', () => {
    render(<Button block shape="square" aria-label="square" />);
    const btn = screen.getByRole('button', { name: 'square' });
    expect(btn).toHaveClass('btn-block', 'btn-square');
  });

  it('shows a spinner and disables while loading', () => {
    render(<Button loading>Processing</Button>);
    const btn = screen.getByRole('button', { name: 'Processing' });
    expect(btn).toBeDisabled();
    expect(btn.querySelector('[aria-hidden="true"]')).toBeInTheDocument();
  });

  it('fires onClick', async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Go</Button>);
    await userEvent.click(screen.getByRole('button', { name: 'Go' }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders a trailing icon via iconEnd', () => {
    render(<Button iconEnd={<span data-testid="icon-end" />}>Next</Button>);
    expect(screen.getByTestId('icon-end')).toBeInTheDocument();
  });
});
