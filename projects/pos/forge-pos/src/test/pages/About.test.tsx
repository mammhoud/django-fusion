import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import About from '../../pages/admin/About';

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
});

describe('About Page', () => {
  it('renders the about title', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.title|About Forge POS/)).toBeInTheDocument();
    });
  });

  it('renders the project description section', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.projectTitle|About the Project/)).toBeInTheDocument();
    });
  });

  it('renders the support and contact section', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.supportTitle|Support & Contact/)).toBeInTheDocument();
    });
  });

  it('renders support form fields', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.sendMessage|Send Message/)).toBeInTheDocument();
    });
  });

  it('shows support name field', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      const nameInputs = screen.getAllByPlaceholderText(/support\.namePlaceholder|John Doe/);
      expect(nameInputs.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows support email field', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      const emailInputs = screen.getAllByPlaceholderText(/support\.emailPlaceholder|john@example\.com/);
      expect(emailInputs.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows support subject field', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      const subjectInputs = screen.getAllByPlaceholderText(/support\.subjectPlaceholder|How can we help/);
      expect(subjectInputs.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows support message textarea', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      const messageTextareas = screen.getAllByPlaceholderText(/support\.messagePlaceholder|Tell us how we can help/);
      expect(messageTextareas.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders version information', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.versionLabel|Version/)).toBeInTheDocument();
    });
  });

  it('renders the developed by section', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.developedBy|Developed by/)).toBeInTheDocument();
    });
  });

  it('renders the back button', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/common\.backToHome|Back to Home/)).toBeInTheDocument();
    });
  });

  it('validates support form - shows error on empty name', async () => {
    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.sendMessage|Send Message/)).toBeInTheDocument();
    });

    const sendButton = screen.getByText(/about\.sendMessage|Send Message/).closest('button');
    if (sendButton) {
      await userEvent.click(sendButton);

      await waitFor(() => {
        const nameErrors = screen.getAllByText(/support\.validationName|Please enter your name/);
        expect(nameErrors.length).toBeGreaterThanOrEqual(1);
      });
    }
  });

  it('submits support form successfully', async () => {
    mockInvokeSuccess('send_support_email', undefined);

    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.sendMessage|Send Message/)).toBeInTheDocument();
    });

    // Fill out the form
    const nameInputs = screen.getAllByPlaceholderText(/support\.namePlaceholder|John Doe/);
    const emailInputs = screen.getAllByPlaceholderText(/support\.emailPlaceholder|john@example\.com/);
    const subjectInputs = screen.getAllByPlaceholderText(/support\.subjectPlaceholder|How can we help/);
    const messageTextareas = screen.getAllByPlaceholderText(/support\.messagePlaceholder|Tell us how we can help/);

    await userEvent.type(nameInputs[0], 'John Doe');
    await userEvent.type(emailInputs[0], 'john@example.com');
    await userEvent.type(subjectInputs[0], 'Test Subject');
    await userEvent.type(messageTextareas[0], 'This is a test message that is long enough.');

    const sendButton = screen.getByText(/about\.sendMessage|Send Message/).closest('button');
    if (sendButton) {
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText(/about\.successToast|Message sent successfully/)).toBeInTheDocument();
      });
    }
  });

  it('shows error toast when support form submission fails', async () => {
    mockInvokeError('send_support_email', 'Failed to send message');

    renderWithRouter(<About />);

    await waitFor(() => {
      expect(screen.getByText(/about\.sendMessage|Send Message/)).toBeInTheDocument();
    });

    // Fill out the form
    const nameInputs = screen.getAllByPlaceholderText(/support\.namePlaceholder|John Doe/);
    const emailInputs = screen.getAllByPlaceholderText(/support\.emailPlaceholder|john@example\.com/);
    const subjectInputs = screen.getAllByPlaceholderText(/support\.subjectPlaceholder|How can we help/);
    const messageTextareas = screen.getAllByPlaceholderText(/support\.messagePlaceholder|Tell us how we can help/);

    await userEvent.type(nameInputs[0], 'John Doe');
    await userEvent.type(emailInputs[0], 'john@example.com');
    await userEvent.type(subjectInputs[0], 'Test Subject');
    await userEvent.type(messageTextareas[0], 'This is a test message that is long enough.');

    const sendButton = screen.getByText(/about\.sendMessage|Send Message/).closest('button');
    if (sendButton) {
      await userEvent.click(sendButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to send message')).toBeInTheDocument();
      });
    }
  });
});
