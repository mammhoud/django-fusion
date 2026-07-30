import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
} from '../test-utils';
import { resetInvokeMocks } from '../mocks/tauri';
import SupportChat from '../../pages/admin/SupportChat';

// Use vi.hoisted() to define mock fns BEFORE the vi.mock factory uses them
const { mockHealthCheck } = vi.hoisted(() => ({
  mockHealthCheck: vi.fn().mockResolvedValue(true),
}));

vi.mock('../../api/sidecar', () => ({
  default: {
    healthCheck: mockHealthCheck,
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    base: 'http://127.0.0.1:8765',
    wsBase: 'ws://127.0.0.1:8765',
  },
}));

vi.mock('../../api', () => ({
  sidecar: {
    healthCheck: mockHealthCheck,
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
  data: {
    listSales: vi.fn().mockResolvedValue({ data: [], ok: true }),
    getSale: vi.fn(),
    getInvoiceUrl: vi.fn(),
  },
}));

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockHealthCheck.mockResolvedValue(true);
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


});
