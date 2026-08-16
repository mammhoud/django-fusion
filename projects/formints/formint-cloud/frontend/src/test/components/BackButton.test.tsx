import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '../test-utils';
import BackButton from '../../components/ui/BackButton';

describe('BackButton component', () => {
  it('renders default back label from i18n', () => {
    render(<BackButton onClick={() => {}} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<BackButton onClick={onClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('renders custom text label', () => {
    render(<BackButton onClick={() => {}} text="Go Back Home" />);
    expect(screen.getByText('Go Back Home')).toBeInTheDocument();
  });

  it('renders breadcrumb trail with last segment emphasized', () => {
    render(<BackButton onClick={() => {}} breadcrumb={['Home', 'Settings']} />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('sets data-tooltip when tooltip is provided', () => {
    render(<BackButton onClick={() => {}} tooltip="Back to the page you came from" />);
    expect(screen.getByRole('button')).toHaveAttribute('data-tooltip', 'Back to the page you came from');
  });

  it('shows a loading spinner and loading label when disabled', () => {
    render(<BackButton onClick={() => {}} disabled />);
    expect(screen.getByText(/common\.loading|Loading/)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
