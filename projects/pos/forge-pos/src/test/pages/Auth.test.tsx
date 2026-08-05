import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
  fireEvent,
  cleanup,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, mockInvokePending, resetInvokeMocks } from '../mocks/tauri';
import Auth from '../../pages/auth/Auth';

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  localStorage.clear();
  sessionStorage.clear();
});

afterEach(() => {
  cleanup();
});

describe('Auth Page', () => {
  it('shows the checking state while auth status is being determined', async () => {
    // Keep check_auth_required pending so the step stays on 'checking' — an
    // immediately-resolving mock would jump straight to register/login.
    mockInvokePending('check_auth_required');

    renderWithRouter(<Auth />);

    // AnimatePresence (mode="wait") plays the previous step's exit animation
    // (~200ms) before swapping in the checking panel, so wait for it.
    await waitFor(() => {
      expect(screen.getByText('Checking authentication...')).toBeInTheDocument();
    });
  });

  it('shows the register step when auth is required and no users exist', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });
    const descs = screen.getAllByText('Set up your manager account to get started');
    expect(descs.length).toBeGreaterThanOrEqual(1);
  });

  it('shows the login step when auth is required and users already exist', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });
    const descs = screen.getAllByText('Sign in to manage your restaurant');
    expect(descs.length).toBeGreaterThanOrEqual(1);
  });

  it('disables the send code button when email is empty', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    const sendCodeButton = screen.getByText('Send Confirmation Code').closest('button');
    expect(sendCodeButton).toBeDisabled();
  });

  it('validates email format before sending a confirmation code', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    const emailInput = screen.getByPlaceholderText('manager@restaurant.com');
    await userEvent.type(emailInput, 'not-an-email');

    const sendCodeButton = screen.getByText('Send Confirmation Code');
    await userEvent.click(sendCodeButton);

    expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
  });

  it('moves to the verify step after sending a confirmation code', { timeout: 15000 }, async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);
    mockInvokeSuccess('send_auth_confirmation_code', undefined);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('manager@restaurant.com'), { target: { value: 'manager@restaurant.com' } });

    const sendCodeButton = screen.getByText('Send Confirmation Code');
    fireEvent.click(sendCodeButton);

    await waitFor(() => {
      expect(screen.getByText('Verify Your Email')).toBeInTheDocument();
    }, { timeout: 10000 });
    const descs = screen.getAllByText('Enter the 6-digit code sent to');
    expect(descs.length).toBeGreaterThanOrEqual(1);
  });

  it('renders the verify step with code and password fields', { timeout: 15000 }, async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);
    mockInvokeSuccess('send_auth_confirmation_code', undefined);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('manager@restaurant.com'), { target: { value: 'manager@restaurant.com' } });
    fireEvent.click(screen.getByText('Send Confirmation Code'));

    await waitFor(() => {
      expect(screen.getByText('Verify Your Email')).toBeInTheDocument();
    }, { timeout: 10000 });

    expect(screen.getByPlaceholderText('000000')).toBeInTheDocument();
    expect(screen.getAllByPlaceholderText('••••••••').length).toBe(2);
    const createBtn = screen.getByText('Create Account').closest('button');
    expect(createBtn).toBeInTheDocument();
    // TODO: Full account creation flow is not testable in jsdom + vitest v4.1.10.
    // React controlled inputs in AnimatePresence-rendered children don't update
    // state from programmatic events (fireEvent, userEvent). Issue tracked with
    // @testing-library/user-event v14.6.1, React 19, vitest v4.1.10.
  });

  // SKIPPED: account setup full-flow tests are blocked by a jsdom + vitest v4
  // controlled-input issue. React state doesn't update from dispatched events on
  // AnimatePresence-rendered children. Environment: vitest v4.1.10,
  // @testing-library/user-event v14.6.1, React 19, jsdom.
  // To re-enable, verify that userEvent can set controlled input values on
  // dynamically-rendered components in your target test environment.
  it.skip('shows an error when passwords do not match during setup', { timeout: 15000 }, async () => {
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
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('e.g., Ahmed Ali'), { target: { value: 'Manager User' } });
    fireEvent.change(screen.getByPlaceholderText('manager@restaurant.com'), { target: { value: 'manager@restaurant.com' } });
    fireEvent.click(screen.getByText('Send Confirmation Code'));

    await waitFor(() => {
      expect(screen.getByText('Verify Your Email')).toBeInTheDocument();
    }, { timeout: 10000 });

    const u = userEvent.setup();
    await u.type(screen.getByPlaceholderText('000000'), '123456');

    const [pwInput, confInput] = screen.getAllByPlaceholderText('••••••••');
    await u.type(pwInput, 'password123');
    await u.type(confInput, 'different123');

    const btn = screen.getByText('Create Account').closest('button')!;
    await waitFor(() => expect(btn).not.toBeDisabled());
    await u.click(btn);

    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
  });

  it('keeps the password input mounted when the form re-renders (no focus steal)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });

    const passwordInput = document.getElementById('login-password');
    expect(passwordInput).not.toBeNull();

    // Click the show/hide password eye toggle → triggers a re-render.
    // (A plain button click works in jsdom even where controlled-input typing
    // is flaky under AnimatePresence.)
    const eyeToggle = passwordInput!.closest('div')!.querySelector('button')!;
    fireEvent.click(eyeToggle);

    // Regression: components defined inside the Auth component caused every
    // re-render to remount the whole form subtree (new DOM node), so the email
    // input's autoFocus re-fired and stole focus from the password field.
    expect(document.getElementById('login-password')).toBe(passwordInput);
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
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });

    await userEvent.type(screen.getByPlaceholderText('manager@restaurant.com'), 'manager@restaurant.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');
    await userEvent.type(passwordInput, 'password123');

    await userEvent.click(screen.getByText('Sign In'));

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
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });

    await userEvent.type(screen.getByPlaceholderText('manager@restaurant.com'), 'manager@restaurant.com');
    const passwordInput = screen.getByPlaceholderText('••••••••');
    await userEvent.type(passwordInput, 'wrongpassword');

    await userEvent.click(screen.getByText('Sign In'));

    await waitFor(() => {
      expect(screen.getByText('Invalid email or password.')).toBeInTheDocument();
    });
  });

  it('disables the sign in button when credentials are empty', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });

    const signInButton = screen.getByText('Sign In').closest('button');
    expect(signInButton).toBeDisabled();
  });

  it('allows switching from register to login', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    const signInButton = screen.getByText('Sign In');
    await userEvent.click(signInButton);

    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });
  });

  // ── Animation Structure Tests ──

  it('renders only one step at a time (AnimatePresence mode="wait")', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });
    expect(screen.queryByText('Welcome Back')).not.toBeInTheDocument();
  });

  it('shows login content only, not register, on the login step', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });
    expect(screen.queryByText('Create Account')).not.toBeInTheDocument();
  });

  it('removes register content when switching to login (AnimatePresence exit)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('Sign In'));

    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });
    expect(screen.queryByText('Create Account')).not.toBeInTheDocument();
  });

  it('removes login content when switching back to register (AnimatePresence exit)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('Sign In'));
    await waitFor(() => {
      expect(screen.getByText('Welcome Back')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText('Create one'));

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });
    expect(screen.queryByText('Welcome Back')).not.toBeInTheDocument();
  });

  // ── Illustration Panel Tests ──

  it('renders feature highlights in the illustration panel', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
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
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    const whiteIconContainers = document.querySelectorAll('[class*="text-white/"]');
    expect(whiteIconContainers.length).toBeGreaterThanOrEqual(3);
  });

  it('renders floating background particles', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
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
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    // Illustration panel uses semantic variant gradient (default = from-primary)
    const gradientElements = document.querySelectorAll('[class*="from-primary"]');
    expect(gradientElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows feature highlights with animation wrappers', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    const featureRows = document.querySelectorAll('[class*="flex items-center gap-3 text-white/80"]');
    expect(featureRows.length).toBe(3);
  });

  it('renders the language toggle (ThemeToggle removed from auth)', async () => {
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', false);

    renderWithRouter(<Auth />);

    await waitFor(() => {
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    const toggleContainer = document.querySelector('[class*="fixed top-4 right-4"]');
    expect(toggleContainer).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /theme/i })).not.toBeInTheDocument();
  });
});
