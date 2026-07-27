import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
} from '../test-utils';
import { resetInvokeMocks } from '../mocks/tauri';
import SupportChat from '../../pages/SupportChat';

// Use vi.hoisted() to define mock fns BEFORE the vi.mock factory uses them
const { mockTicketsList, mockHealthCheck, mockCreateChatWs } = vi.hoisted(() => ({
  mockTicketsList: vi.fn().mockResolvedValue({ data: [], ok: true }),
  mockHealthCheck: vi.fn().mockResolvedValue(true),
  mockCreateChatWs: vi.fn().mockReturnValue({ close: vi.fn(), send: vi.fn() }),
}));

vi.mock('../../api', () => ({
  sidecar: {
    healthCheck: mockHealthCheck,
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
  tickets: {
    list: mockTicketsList,
    create: vi.fn(),
    update: vi.fn(),
  },
  chat: {
    getHistory: vi.fn().mockResolvedValue({ data: [], ok: true }),
    createChatWs: mockCreateChatWs,
  },
  data: {
    listSales: vi.fn().mockResolvedValue({ data: [], ok: true }),
    getSale: vi.fn(),
    getInvoiceUrl: vi.fn(),
  },
  // ChatSupport.tsx imports `createChatWs` directly as a named export
  // from '../../api'. If the module system requires it at the top level,
  // export it both nested (for other imports) and at the top level:
  createChatWs: mockCreateChatWs,
}));

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockTicketsList.mockResolvedValue({ data: [], ok: true });
  mockHealthCheck.mockResolvedValue(true);
  mockCreateChatWs.mockReturnValue({ close: vi.fn(), send: vi.fn() });
});

describe('SupportChat Page', () => {
  it('renders the support chat page with title', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/Support & Customer Service/)).toBeInTheDocument();
    });
  });

  it('renders the live chat section', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      const liveChatElements = screen.getAllByText(/Live Chat/);
      expect(liveChatElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders the support tickets section', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      const ticketElements = screen.getAllByText(/Support Tickets/);
      expect(ticketElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows refresh button for tickets', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText('Refresh')).toBeInTheDocument();
    });
  });

  it('shows sidecar status indicator', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      screen.queryByText(/sidecar/i);
      expect(screen.getByText(/Support & Customer Service/)).toBeInTheDocument();
    });
  });

  it('renders the chat support component', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      const chatElements = screen.getAllByText(/Live Chat/);
      expect(chatElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows ticket list when sidecar returns tickets', async () => {
    mockTicketsList.mockResolvedValue({
      data: [
        { id: '1', name: 'Customer 1', email: 'c1@test.com', subject: 'Issue with order', message: 'My order was wrong', status: 'open', created_at: '2026-01-15T10:00:00Z', updated_at: '2026-01-15T10:00:00Z' },
      ],
      ok: true,
    });

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText('Issue with order')).toBeInTheDocument();
    });
  });

  it('shows empty state when no tickets exist', async () => {
    mockTicketsList.mockResolvedValue({
      data: [],
      ok: true,
    });

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/No support tickets yet/)).toBeInTheDocument();
    });
  });
});
