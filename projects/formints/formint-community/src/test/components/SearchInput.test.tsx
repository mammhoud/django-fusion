import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import SearchInput from '../../components/ui/SearchInput';

describe('SearchInput component', () => {
  it('renders input with placeholder and aria-label', () => {
    render(
      <SearchInput
        value=""
        onChange={() => {}}
        placeholder="Search..."
        ariaLabel="Search products"
        testId="my-search"
      />,
    );
    const input = screen.getByTestId('my-search');
    expect(input).toHaveAttribute('placeholder', 'Search...');
    expect(input).toHaveAttribute('aria-label', 'Search products');
  });

  it('calls onChange when typing', () => {
    const onChange = vi.fn();
    render(
      <SearchInput value="" onChange={onChange} placeholder="Search..." ariaLabel="Search" testId="my-search" />,
    );
    fireEvent.change(screen.getByTestId('my-search'), { target: { value: 'burger' } });
    expect(onChange).toHaveBeenCalledWith('burger');
  });

  it('shows the clear button when there is a value and clears on click', () => {
    const onChange = vi.fn();
    render(
      <SearchInput value="burg" onChange={onChange} placeholder="Search..." ariaLabel="Search" testId="my-search" clearLabel="Clear search" />,
    );
    const clear = screen.getByRole('button', { name: 'Clear search' });
    expect(clear).toBeInTheDocument();
    fireEvent.click(clear);
    expect(onChange).toHaveBeenCalledWith('');
  });

  it('shows a loading spinner instead of the clear button while loading', () => {
    render(
      <SearchInput value="burg" onChange={() => {}} placeholder="Search..." ariaLabel="Search" testId="my-search" loading />,
    );
    expect(screen.getByLabelText('filtering')).toBeInTheDocument();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('disables the input when disabled', () => {
    render(
      <SearchInput value="" onChange={() => {}} placeholder="Search..." ariaLabel="Search" testId="my-search" disabled />,
    );
    expect(screen.getByTestId('my-search')).toBeDisabled();
  });

  it('uses the custom onClear handler when provided', () => {
    const onClear = vi.fn();
    render(
      <SearchInput value="x" onChange={() => {}} onClear={onClear} placeholder="Search..." ariaLabel="Search" testId="my-search" clearLabel="Clear" />,
    );
    fireEvent.click(screen.getByRole('button', { name: 'Clear' }));
    expect(onClear).toHaveBeenCalledTimes(1);
  });
});
