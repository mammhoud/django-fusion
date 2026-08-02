import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import { getInvokeHistory, clearInvokeHistory } from '../setup';
import Notes from '../../pages/admin/Notes';

const mockTemplates = [
  { id: 1, name: 'Standard Receipt', template_body: 'Receipt #{{num}}\nTotal: {{total}}', is_default: true },
  { id: 2, name: 'Compact Receipt',  template_body: '{{total}}',                       is_default: false },
  { id: 3, name: 'Thermal Receipt',  template_body: 'POS\n{{date}}\n{{total}}',        is_default: false },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  clearInvokeHistory();
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
      expect(screen.getByLabelText(/notes.searchPlaceholder|Search templates/)).toBeInTheDocument();
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

    const searchInput = screen.getByLabelText(/notes.searchPlaceholder|Search templates/);
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

    const searchInput = screen.getByLabelText(/notes.searchPlaceholder|Search templates/);
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

  // This test mounts the form, switches category, adds two prep steps and saves
  // — under full-suite CPU contention it can exceed vitest's default 5000ms
  // per-test timeout, so raise it explicitly (test runs in ~2.3s alone, ~5.2s
  // under parallel-file load).
  it('shows the prep-steps editor when the preparation category is selected', { timeout: 15000 }, async () => {
    renderWithRouter(<Notes />);
    await waitFor(() => {
      expect(screen.getAllByText('Standard Receipt').length).toBeGreaterThanOrEqual(1);
    });

    // Open the new-note form (AnimatePresence mode="wait" delays the panel ~200ms)
    await userEvent.click(screen.getByRole('button', { name: /notes.addTemplate|Add Template/ }));

    // The plain body textarea is shown by default (generous timeout for
    // full-suite CPU contention — AnimatePresence mode="wait" adds ~200ms).
    // Use getAllByPlaceholderText: under full-suite runs the placeholder can
    // briefly match multiple nodes (AnimatePresence exit + re-entry), so a
    // strict getBy throws a multiple-match error.
    await waitFor(
      () => {
        expect(screen.getAllByPlaceholderText(/notes.bodyPlaceholder|Write your notes here/).length).toBeGreaterThanOrEqual(1);
      },
      { timeout: 3000 },
    );

    // Choose the preparation category (form select is the 2nd combobox after sort)
    const combos = screen.getAllByRole('combobox');
    const categorySelect = combos[combos.length - 1];
    await userEvent.selectOptions(categorySelect, 'preparation');

    // Prep-steps editor replaces the plain textarea ("Add step" button is
    // unique to the PrepStepsEditor — the category <option> also literally
    // reads "Preparation Steps", so the title text alone is ambiguous)
    await waitFor(
      () => {
        expect(screen.getByRole('button', { name: /notes.addStep|Add step/ })).toBeInTheDocument();
        expect(screen.queryAllByPlaceholderText(/notes.bodyPlaceholder|Write your notes here/).length).toBe(0);
      },
      { timeout: 3000 },
    );

    // Add two steps — wait for the step row inputs after each click
    // (PrepStepsEditor mounts rows behind the same transition as the form)
    await userEvent.click(screen.getByRole('button', { name: /notes.addStep|Add step/ }));
    await waitFor(
      () => {
        expect(screen.getByLabelText('Step 1 title')).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
    await userEvent.type(screen.getByLabelText('Step 1 title'), 'Toast the bun');
    await userEvent.type(screen.getByLabelText('Step 1 details'), '2 min, golden brown');
    await userEvent.click(screen.getByRole('button', { name: /notes.addStep|Add step/ }));
    await waitFor(
      () => {
        expect(screen.getByLabelText('Step 2 title')).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
    await userEvent.type(screen.getByLabelText('Step 2 title'), 'Grill the patty');

    // Name required to save
    await userEvent.type(screen.getAllByPlaceholderText(/notes.titlePlaceholder|Note title/)[0], 'Burger Prep');

    mockInvokeSuccess('add_note', {
      id: 99,
      name: 'Burger Prep',
      template_body: '',
      category: 'preparation',
      is_default: false,
      use_as_template: false,
      selectable: true,
      steps: JSON.stringify([
        { title: 'Toast the bun', details: '2 min, golden brown' },
        { title: 'Grill the patty', details: undefined },
      ]),
    });

    await userEvent.click(screen.getByRole('button', { name: /common.save|Save/ }));

    await waitFor(() => {
      const addCall = getInvokeHistory().find(h => h.cmd === 'add_note');
      expect(addCall).toBeDefined();
      const tpl = addCall!.args!.template as Record<string, unknown>;
      expect(tpl.category).toBe('preparation');
      // Steps serialized to JSON; empty-title steps filtered out
      const steps = JSON.parse(String(tpl.steps));
      expect(steps).toEqual([
        { title: 'Toast the bun', details: '2 min, golden brown' },
        { title: 'Grill the patty', details: undefined },
      ]);
    });
  });

  // Same heavy modal class as the prep-steps test (~3.9–4.0s under
  // parallel-file load, close to vitest's 5000ms default per-test timeout)
  it('saves the selectable flag when the toggle is on', { timeout: 15000 }, async () => {
    renderWithRouter(<Notes />);
    await waitFor(() => {
      expect(screen.getAllByText('Standard Receipt').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('button', { name: /notes.addTemplate|Add Template/ }));
    await waitFor(
      () => {
        expect(screen.getAllByPlaceholderText(/notes.titlePlaceholder|Note title/).length).toBeGreaterThanOrEqual(1);
      },
      { timeout: 3000 },
    );
    await userEvent.type(screen.getAllByPlaceholderText(/notes.titlePlaceholder|Note title/)[0], 'Quick Allergen Note');
    await userEvent.type(screen.getAllByPlaceholderText(/notes.bodyPlaceholder|Write your notes here/)[0], 'Contains nuts');

    await userEvent.click(screen.getByRole('checkbox', { name: /notes.selectable|Quick-select/ }));

    mockInvokeSuccess('add_note', {
      id: 100,
      name: 'Quick Allergen Note',
      template_body: 'Contains nuts',
      category: null,
      is_default: false,
      use_as_template: false,
      selectable: true,
      steps: null,
    });

    await userEvent.click(screen.getByRole('button', { name: /common.save|Save/ }));

    await waitFor(() => {
      const addCall = getInvokeHistory().find(h => h.cmd === 'add_note');
      expect(addCall).toBeDefined();
      const tpl = addCall!.args!.template as Record<string, unknown>;
      expect(tpl.selectable).toBe(true);
    });
  });

  it('filters to selectable notes when the selectable pill is active', async () => {
    const notesWithSelectable = [
      { id: 1, name: 'Pinned Prep', template_body: 'Step 1', category: 'preparation', is_default: false, use_as_template: false, selectable: true },
      { id: 2, name: 'Plain Note', template_body: 'text', category: 'general', is_default: false, use_as_template: false, selectable: false },
    ];
    mockInvokeSuccess('get_notes', notesWithSelectable);
    renderWithRouter(<Notes />);

    await waitFor(() => {
      expect(screen.getAllByText('Pinned Prep').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Plain Note').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('button', { name: /notes.selectable|Quick-select/ }));

    await waitFor(() => {
      expect(screen.getAllByText('Pinned Prep').length).toBeGreaterThanOrEqual(1);
      expect(screen.queryByText('Plain Note')).not.toBeInTheDocument();
    });
  });
});
