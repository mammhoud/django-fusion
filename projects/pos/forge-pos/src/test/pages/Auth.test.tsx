import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Auth from '../../pages/Auth';

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  localStorage.clear();
  sessionStorage.clear();
});

describe('Auth Page', () => {
  it('shows the checking state while auth status is being determined', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    expect(screen.getByText('auth.checking')).toBeInTheDocument();
  });

  it('shows the register step when auth is required and no users exist', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });
    const descs = screen.getAllByText('auth.registerDesc');
    expect(descs.length).toBeGreaterThanOrEqual(1);
  });

  it('shows the login step when auth is required and users already exist', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });
    const descs = screen.getAllByText('auth.loginDesc');
    expect(descs.length).toBeGreaterThanOrEqual(1);
  });

  it('disables the send code button when email is empty', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const sendCodeButton = screen.getByText('auth.sendCode').closest('button');
    expect(sendCodeButton).toBeDisabled();
  });

  it('validates email format before sending a confirmation code', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const emailInput = screen.getByPlaceholderText('manager@restaurant.com');
    await userEvent.type(emailInput, 'not-an-email');

    const sendCodeButton = screen.getByText('auth.sendCode');
    await userEvent.click(sendCodeButton);

    expect(screen.getByText('auth.validationEmailInvalid')).toBeInTheDocument();
  });

  it('moves to the verify step after sending a confirmation code', { timeout: 15000 }, async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);
    mockInvokeSuccess('send_auth_confirmation_code', undefined);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const emailInput = screen.getByPlaceholderText('manager@restaurant.com');
    await userEvent.type(emailInput, 'manager@restaurant.com');

    const sendCodeButton = screen.getByText('auth.sendCode');
    await userEvent.click(sendCodeButton);

    await waitFor(() => {
      expect(screen.getByText('auth.verifyEmail')).toBeInTheDocument();
    }, { timeout: 10000 });
    const descs = screen.getAllByText('auth.verifyDesc');
    expect(descs.length).toBeGreaterThanOrEqual(1);
  });

  it('completes account setup after entering code and password', { timeout: 15000 }, async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);
    mockInvokeSuccess('send_auth_confirmation_code', undefined);
    mockInvokeSuccess('setup_account', {
      id: 1,
      email: 'manager@restaurant.com',
      name: 'Manager User',
    });

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    // Register step
    await userEvent.type(screen.getByPlaceholderText('auth.namePlaceholder'), 'Manager User');
    await userEvent.type(screen.getByPlaceholderText('manager@restaurant.com'), 'manager@restaurant.com');
    await userEvent.click(screen.getByText('auth.sendCode'));

    await waitFor(() => {
      expect(screen.getByText('auth.verifyEmail')).toBeInTheDocument();
    }, { timeout: 10000 });

    // Verify step
    const codeInput = screen.getByPlaceholderText('000000');
    await userEvent.type(codeInput, '123456');

    const [passwordInput, confirmInput] = screen.getAllByPlaceholderText('••••••••');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.type(confirmInput, 'password123');

    await userEvent.click(screen.getByText('auth.createAccountBtn'));

    await waitFor(() => {
      expect(screen.getByText('auth.accountCreated')).toBeInTheDocument();
    });
  });

  it('shows an error when passwords do not match during setup', { timeout: 15000 }, async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);
    mockInvokeSuccess('send_auth_confirmation_code', undefined);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    await userEvent.type(screen.getByPlaceholderText('auth.namePlaceholder'), 'Manager User');
    await userEvent.type(screen.getByPlaceholderText('manager@restaurant.com'), 'manager@restaurant.com');
    await userEvent.click(screen.getByText('auth.sendCode'));

    await waitFor(() => {
      expect(screen.getByText('auth.verifyEmail')).toBeInTheDocument();
    }, { timeout: 10000 });

    const codeInput = screen.getByPlaceholderText('000000');
    await userEvent.type(codeInput, '123456');

    const [passwordInput, confirmInput] = screen.getAllByPlaceholderText('••••••••');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.type(confirmInput, 'different123');

    await userEvent.click(screen.getByText('auth.createAccountBtn'));

    expect(screen.getByText('auth.validationPasswordMatch')).toBeInTheDocument();
  });

  it('logs in with valid credentials', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);
    mockInvokeSuccess('login_user', {
      id: 1,
      email: 'manager@restaurant.com',
      name: 'Manager User',
    });

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });

    await userEvent.type(screen.getByPlaceholderText('manager@restaurant.com'), 'manager@restaurant.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');
    await userEvent.type(passwordInput, 'password123');

    await userEvent.click(screen.getByText('auth.signIn'));

    await waitFor(() => {
      expect(localStorage.getItem('is_authenticated')).toBe('true');
    });
    const storedUser = JSON.parse(localStorage.getItem('auth_user') || '{}');
    expect(storedUser.email).toBe('manager@restaurant.com');
  });

  it('shows an error when login fails', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);
    mockInvokeError('login_user', 'Invalid email or password.');

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });

    await userEvent.type(screen.getByPlaceholderText('manager@restaurant.com'), 'manager@restaurant.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');
    await userEvent.type(passwordInput, 'wrongpassword');

    await userEvent.click(screen.getByText('auth.signIn'));

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
    });
  });

  it('disables the sign in button when credentials are empty', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });

    const signInButton = screen.getByText('auth.signIn').closest('button');
    expect(signInButton).toBeDisabled();
  });

  it('allows switching from register to login', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const signInButton = screen.getByText('auth.signIn');
    await userEvent.click(signInButton);

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });
  });

  // ── Animation Structure Tests ──

  it('renders only one step at a time (AnimatePresence mode="wait")', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });
    expect(screen.queryByText('auth.welcomeBack')).not.toBeInTheDocument();
  });

  it('shows login content only, not register, on the login step', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });
    expect(screen.queryByText('auth.createAccount')).not.toBeInTheDocument();
  });

  it('removes register content when switching to login (AnimatePresence exit)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('auth.signIn'));

    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });
    expect(screen.queryByText('auth.createAccount')).not.toBeInTheDocument();
  });

  it('removes login content when switching back to register (AnimatePresence exit)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('auth.signIn'));
    await waitFor(() => {
      expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('auth.createOne'));

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });
    expect(screen.queryByText('auth.welcomeBack')).not.toBeInTheDocument();
  });

  // ── Illustration Panel Tests ──

  it('renders feature highlights in the illustration panel', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    expect(screen.getByText('Point of Sale & Order Management')).toBeInTheDocument();
    expect(screen.getByText('Real-time Analytics & Reports')).toBeInTheDocument();
    expect(screen.getByText('Inventory & Recipe Tracking')).toBeInTheDocument();
  });

  it('renders the Forge POS brand heading in the illustration panel', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Forge POS')).toBeInTheDocument();
    });
  });

  it('renders floating brand icons with white opacity colors', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const whiteIconContainers = document.querySelectorAll('[class*="text-white/"]');
    expect(whiteIconContainers.length).toBeGreaterThanOrEqual(3);
  });

  it('renders floating background particles', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const particles = document.querySelectorAll('[class*="bg-white/10"]');
    expect(particles.length).toBeGreaterThanOrEqual(15);
  });

  // ── Theme Variant & Gradient Tests ──

  it('renders the illustration panel with variant-aware gradient default (teal)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const gradientElements = document.querySelectorAll('[class*="from-teal-600"]');
    expect(gradientElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows feature highlights with animation wrappers', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const featureRows = document.querySelectorAll('[class*="flex items-center gap-3 text-white/80"]');
    expect(featureRows.length).toBe(3);
  });

  it('renders the visibility toggle toggles (LanguageToggle + ThemeToggle)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('auth.createAccount')).toBeInTheDocument();
    });

    const toggleContainer = document.querySelector('[class*="fixed top-4 right-4"]');
    expect(toggleContainer).toBeInTheDocument();
  });
});
