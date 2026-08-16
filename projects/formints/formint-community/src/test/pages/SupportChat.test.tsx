import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import SupportChat from '../../app/pages/admin/SupportChat';

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
});

describe('SupportChat Page', () => {
  it('renders the support chat page with title', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText('Support')).toBeInTheDocument();
    });
  });

  it('shows a warning when no support email is configured', async () => {
    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/No support email configured/)).toBeInTheDocument();
    });
  });

  it('shows the configured support email status', async () => {
    mockInvokeSuccess('get_smtp_config', {
      configured: true,
      support_email: 'support@structa.cloud',
    });

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/Support email configured/)).toBeInTheDocument();
    });
    // The email renders in 3 spots (status, contact info, mailto link)
    expect(screen.getAllByText('support@structa.cloud').length).toBeGreaterThanOrEqual(1);
  });

  it('renders the chat support component when an email is configured', async () => {
    mockInvokeSuccess('get_smtp_config', {
      configured: true,
      support_email: 'support@structa.cloud',
    });

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText('Need Help?')).toBeInTheDocument();
    });
    expect(screen.getByText(/We're here to assist you/)).toBeInTheDocument();
  });

  it('shows contact information with the support email', async () => {
    mockInvokeSuccess('get_smtp_config', {
      configured: true,
      support_email: 'help@structa.cloud',
    });

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/Contact Information/)).toBeInTheDocument();
    });
    // The email renders in 3 spots (status, contact info, mailto link)
    expect(screen.getAllByText('help@structa.cloud').length).toBeGreaterThanOrEqual(1);
  });

  it('shows persisted message history with status', async () => {
    mockInvokeSuccess('get_smtp_config', {
      configured: true,
      support_email: 'support@structa.cloud',
    });
    mockInvokeSuccess('get_support_messages', [
      {
        id: 1,
        name: 'Sara',
        email: 'sara@example.com',
        phone: '+20 100 000 0000',
        subject: 'Billing question',
        category: 'billing',
        priority: 'high',
        message: 'My invoice total looks wrong.',
        status: 'new',
        created_at: '2026-09-10 10:00:00',
        updated_at: '2026-09-10 10:00:00',
      },
    ]);

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/Message History/)).toBeInTheDocument();
    });
    expect(screen.getByText('Sara')).toBeInTheDocument();
    expect(screen.getByText('sara@example.com')).toBeInTheDocument();
    expect(screen.getByText('Billing question')).toBeInTheDocument();
    // 'new' renders twice: as the <select> option value and as the status badge
    expect(screen.getAllByText('new').length).toBeGreaterThan(0);
  });

  it('shows empty state when no messages exist', async () => {
    mockInvokeSuccess('get_smtp_config', {
      configured: true,
      support_email: 'support@structa.cloud',
    });
    mockInvokeSuccess('get_support_messages', []);

    renderWithRouter(<SupportChat />);

    await waitFor(() => {
      expect(screen.getByText(/No messages yet/)).toBeInTheDocument();
    });
  });
});
