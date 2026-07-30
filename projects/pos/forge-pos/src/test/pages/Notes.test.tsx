import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Notes from '../../pages/settings/Notes';

const mockTemplates = [
  { id: 1, name: 'Standard Receipt', template_body: 'Receipt #{{num}}\nTotal: {{total}}', is_default: true },
  { id: 2, name: 'Compact Receipt',  template_body: '{{total}}',                       is_default: false },
  { id: 3, name: 'Thermal Receipt',  template_body: 'POS\n{{date}}\n{{total}}',        is_default: false },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_notes', mockTemplates);
});

describe('Notes page', () => {
  it('hydrates the template list from the backend', async () => {
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getAllByText('Standard Receipt').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('Compact Receipt').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Thermal Receipt').length).toBeGreaterThanOrEqual(1);
  });

  it('shows search input + result counter', async () => {
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getByLabelText(/notes.searchPlaceholder|Search notes/)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });
  });

  it('search by name filters after the idle debounce window', async () => {
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getAllByText('Thermal Receipt').length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/notes.searchPlaceholder|Search notes/);
    await userEvent.type(searchInput, 'thermal');

    await waitFor(
      () => {
        expect(screen.getAllByText('Thermal Receipt').length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText('Standard Receipt')).not.toBeInTheDocument();
        expect(screen.queryByText('Compact Receipt')).not.toBeInTheDocument();
        expect(screen.getByText('1 / 3')).toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('search also matches by template_body substring', async () => {
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getAllByText('Thermal Receipt').length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/notes.searchPlaceholder|Search notes/);
    // unique substring only present in template_body of Standard Receipt
    await userEvent.type(searchInput, 'Receipt #');

    await waitFor(
      () => {
        expect(screen.getAllByText('Standard Receipt').length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText('Thermal Receipt')).not.toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('sort-by-name-asc reorders alphabetically', async () => {
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getAllByText('Standard Receipt').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.selectOptions(screen.getByLabelText(/notes.sortBy|Sort by/), 'name-asc');

    await waitFor(() => {
      const headings = screen.getAllByRole('heading', { level: 3 });
      expect(headings[0].textContent).toBe('Compact Receipt');
      expect(headings[1].textContent).toBe('Standard Receipt');
      expect(headings[2].textContent).toBe('Thermal Receipt');
    });
  });

  it('shows the no-templates empty state when the list is empty', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_notes', []);
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getByText(/notes.noTemplates|No notes/)).toBeInTheDocument();
    });
  });
});
