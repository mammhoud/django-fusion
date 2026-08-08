import { describe, it, expect } from 'vitest';
import { render, screen } from '../test-utils';
import Card from '../../components/ui/Card';

describe('Card component', () => {
  it('renders children with base card class', () => {
    render(<Card>Hello</Card>);
    expect(screen.getByText('Hello')).toHaveClass('card');
  });

  it('applies padding preset classes', () => {
    render(<Card padding="sm">Hi</Card>);
    expect(screen.getByText('Hi')).toHaveClass('p-3');
  });

  it('applies radius preset classes', () => {
    render(<Card radius="2xl">Hi</Card>);
    expect(screen.getByText('Hi')).toHaveClass('rounded-2xl');
  });

  it('applies shadow preset classes', () => {
    render(<Card shadow="md">Hi</Card>);
    expect(screen.getByText('Hi')).toHaveClass('shadow-md');
  });

  it('maps BEM variant modifiers', () => {
    render(<Card variant="elevated">Hi</Card>);
    expect(screen.getByText('Hi')).toHaveClass('card--elevated');
  });

  it('maps legacy border prop to the bordered variant for backward compat', () => {
    render(<Card border="base-200">Hi</Card>);
    expect(screen.getByText('Hi')).toHaveClass('card--bordered');
  });

  it('applies hover, center, and transitional flags', () => {
    render(<Card hover center transitional>Hi</Card>);
    const card = screen.getByText('Hi');
    expect(card).toHaveClass('card--hover', 'text-center', 'transition-colors');
  });

  it('applies spaceY spacing', () => {
    render(<Card spaceY="4">Hi</Card>);
    expect(screen.getByText('Hi')).toHaveClass('space-y-4');
  });

  it('forwarded extra props to the div', () => {
    render(<Card data-testid="card-el">Hi</Card>);
    expect(screen.getByTestId('card-el')).toBeInTheDocument();
  });
});
