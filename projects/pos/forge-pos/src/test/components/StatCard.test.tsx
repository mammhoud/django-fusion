import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import StatCard from '../../components/ui/StatCard';

describe('StatCard component', () => {
  it('renders title, value, and desc', () => {
    render(<StatCard title="Revenue" value="$1,245" desc="vs yesterday" />);
    expect(screen.getByText('Revenue')).toBeInTheDocument();
    expect(screen.getByText('$1,245')).toBeInTheDocument();
    expect(screen.getByText('vs yesterday')).toBeInTheDocument();
  });

  it('resolves semantic color classes', () => {
    render(<StatCard title="T" value="1" color="success" />);
    expect(screen.getByText('1')).toHaveClass('text-success');
  });

  it('resolves legacy gradient names to semantic colors', () => {
    render(<StatCard title="T" value="1" color="from-emerald-500 to-teal-600" />);
    expect(screen.getByText('1')).toHaveClass('text-success');
  });

  it('renders an icon node', () => {
    render(<StatCard title="T" value="1" icon={<span data-testid="stat-icon" />} />);
    expect(screen.getByTestId('stat-icon')).toBeInTheDocument();
  });

  it('calls onClick when the card is clicked', () => {
    const onClick = vi.fn();
    render(<StatCard title="T" value="1" onClick={onClick} animated={false} />);
    fireEvent.click(screen.getByText('1').closest('.stat')!);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('calls onDescClick when the desc is clicked', () => {
    const onDescClick = vi.fn();
    render(<StatCard title="T" value="1" desc="More" onDescClick={onDescClick} animated={false} />);
    fireEvent.click(screen.getByText('More'));
    expect(onDescClick).toHaveBeenCalledTimes(1);
  });

  it('renders skeleton blocks while loading', () => {
    render(<StatCard loading title="T" value="1" animated={false} />);
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('applies compact padding', () => {
    render(<StatCard title="T" value="1" compact animated={false} />);
    expect(screen.getByText('T').closest('.stat')).toHaveClass('p-3');
  });
});
