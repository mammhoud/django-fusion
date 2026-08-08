import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  render,
  screen,
  waitFor,
  fireEvent,
  userEvent,
} from '../test-utils';
import ThemePreviewModal from '../../components/display/ThemePreviewModal';
import { ThemeProvider } from '../../contexts/ThemeContext';

function renderPreview(initialMode: 'light' | 'dark' = 'light') {
  localStorage.setItem('theme-mode', initialMode);
  return render(
    <ThemeProvider>
      <ThemePreviewModal isOpen onClose={() => {}} />
    </ThemeProvider>,
  );
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

describe('ThemePreviewModal', () => {
  it('renders the preview sections and the resolved theme badge', () => {
    renderPreview('light');

    expect(screen.getByRole('dialog', { name: 'Theme Component Preview' })).toBeInTheDocument();
    expect(screen.getByText('Buttons')).toBeInTheDocument();
    expect(screen.getByText('Form Controls')).toBeInTheDocument();
    expect(screen.getByText('Alerts')).toBeInTheDocument();
    expect(screen.getByText('Stats')).toBeInTheDocument();
    expect(screen.getByText('Table')).toBeInTheDocument();
  });

  it('switches the live theme to dark and back via the mode switcher', async () => {
    renderPreview('light');

    // Starts light — theme badge resolves to the default light theme
    // (the badge + footer both render the resolved theme name)
    expect(screen.getAllByText('perplexity').length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole('button', { name: /Dark/ }));

    await waitFor(() => {
      expect(localStorage.getItem('theme-mode')).toBe('dark');
      // Default variant dark resolves to perplexity-dark
      expect(document.documentElement.getAttribute('data-theme')).toBe('perplexity-dark');
    });

    await userEvent.click(screen.getByRole('button', { name: /Light/ }));

    await waitFor(() => {
      expect(localStorage.getItem('theme-mode')).toBe('light');
    });
  });

  it('changes the variant through the chooser and updates the theme live', async () => {
    renderPreview('light');

    await userEvent.click(screen.getByRole('button', { name: /Corporate/ }));

    await waitFor(() => {
      expect(localStorage.getItem('theme-variant')).toBe('corporate');
      expect(document.documentElement.getAttribute('data-theme')).toBe('corporate-light');
    });
  });

  it('switching to System follows the OS preference', async () => {
    // Force a dark system preference for the test
    const originalMatchMedia = window.matchMedia;
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: query.includes('dark'),
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia;

    renderPreview('light');

    await userEvent.click(screen.getByRole('button', { name: /System/ }));

    await waitFor(() => {
      expect(localStorage.getItem('theme-follow-system')).toBe('true');
      // System preference is dark → dark theme applied
      expect(document.documentElement.getAttribute('data-theme')).toBe('perplexity-dark');
    });

    // Restore the original so later tests aren't affected
    window.matchMedia = originalMatchMedia;
  });

  it('closes when the modal is dismissed', async () => {
    const onClose = vi.fn();
    render(
      <ThemeProvider>
        <ThemePreviewModal isOpen onClose={onClose} />
      </ThemeProvider>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Close' }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
