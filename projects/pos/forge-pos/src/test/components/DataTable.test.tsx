import { describe, it, expect, afterEach, vi } from 'vitest';
import { renderWithRouter, screen, fireEvent } from '../test-utils';
import DataTable, { type Column } from '../../components/ui/DataTable';

// The CSV export test stubs URL.createObjectURL — always restore globals
// so a failing assertion doesn't leak the stub into subsequent tests.
afterEach(() => {
  vi.unstubAllGlobals();
});

interface Row {
  id: number;
  name: string;
  price: number;
}

const columns: Column<Row>[] = [
  { key: 'name', label: 'Name', sortable: true, render: (r) => r.name },
  { key: 'price', label: 'Price', sortable: true, render: (r) => `$${r.price}` },
];

const rows: Row[] = [
  { id: 1, name: 'Apple', price: 5 },
  { id: 2, name: 'Banana', price: 3 },
  { id: 3, name: 'Cherry', price: 8 },
];

function renderTable(props: Partial<React.ComponentProps<typeof DataTable<Row>>> = {}) {
  return renderWithRouter(
    <DataTable<Row>
      columns={columns}
      data={rows}
      keyExtractor={(r) => r.id}
      {...props}
    />,
  );
}

describe('DataTable component', () => {
  it('renders column headers and row content', () => {
    renderTable();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Price')).toBeInTheDocument();
    expect(screen.getByText('Apple')).toBeInTheDocument();
    expect(screen.getByText('$5')).toBeInTheDocument();
    expect(screen.getByText('Cherry')).toBeInTheDocument();
  });

  it('renders the empty state when there is no data', () => {
    renderTable({ data: [] });
    expect(screen.getByText(/common\.noDataFound|No data/)).toBeInTheDocument();
  });

  it('sorts rows by clicking a sortable header', () => {
    renderTable();
    fireEvent.click(screen.getByText('Price'));
    // After first click (asc): Banana ($3) should appear before Apple ($5)
    const priceCells = screen.getAllByText(/\$\d/);
    expect(priceCells[0]).toHaveTextContent('$3');
    // Click again (desc): Cherry ($8) first
    fireEvent.click(screen.getByText('Price'));
    const priceCellsDesc = screen.getAllByText(/\$\d/);
    expect(priceCellsDesc[0]).toHaveTextContent('$8');
  });

  it('supports row selection via checkboxes', () => {
    const onSelectionChange = vi.fn();
    renderTable({ selectable: true, onSelectionChange });

    const checkboxes = screen.getAllByRole('checkbox');
    // Header select-all + 3 rows
    expect(checkboxes.length).toBeGreaterThanOrEqual(4);
    fireEvent.click(checkboxes[1]); // select first row
    expect(onSelectionChange).toHaveBeenCalled();
  });

  it('shows selected count in the toolbar', () => {
    renderTable({ selectable: true });
    const checkboxes = screen.getAllByRole('checkbox');
    fireEvent.click(checkboxes[1]);
    fireEvent.click(checkboxes[2]);
    expect(screen.getByText(/common\.selected|selected/)).toBeInTheDocument();
  });

  it('supports inline editing and saves on Enter', async () => {
    const onEditSave = vi.fn().mockResolvedValue(undefined);
    const editableColumns: Column<Row>[] = [
      { key: 'name', label: 'Name', editable: true, render: (r) => r.name },
    ];
    renderWithRouter(
      <DataTable<Row>
        columns={editableColumns}
        data={rows}
        keyExtractor={(r) => r.id}
        onEditSave={onEditSave}
      />,
    );

    fireEvent.click(screen.getByText('Apple'));
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Green Apple' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await vi.waitFor(() => {
      expect(onEditSave).toHaveBeenCalledWith(rows[0], 'name', 'Green Apple');
    });
  });

  it('renders mobile renderer on small screens', () => {
    const mobileRender = (r: Row) => <div data-testid={`mobile-${r.id}`}>{r.name} (mobile)</div>;
    renderTable({ mobileRender });
    expect(screen.getByTestId('mobile-1')).toBeInTheDocument();
  });

  it('exports CSV when the export button is clicked', () => {
    const createObjectURL = vi.fn(() => 'blob:mock');
    vi.stubGlobal('URL', { ...URL, createObjectURL, revokeObjectURL: vi.fn() });
    renderTable({ exportable: true, fileName: 'products' });

    fireEvent.click(screen.getByRole('button', { name: /common\.csv|CSV/ }));
    expect(createObjectURL).toHaveBeenCalled();
  });
});
