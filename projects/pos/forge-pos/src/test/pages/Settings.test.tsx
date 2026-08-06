import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { LanguageProvider } from '../../contexts/LanguageContext';
import { AuthProvider } from '../../contexts/AuthContext';
import Settings from '../../pages/admin/Settings';

const mockSettings = {
  restaurant_name: 'Test Restaurant',
  address: '123 Main St',
  phone: '+1234567890',
  email: 'test@restaurant.com',
  tax_rate: '10',
  currency: 'USD',
  opening_time: '09:00',
  closing_time: '22:00',
  receipt_footer: 'Thank you!',
  dine_in_tables: 10,
  delivery_fee: 5,
  delivery_fee_per_km: 2,
};

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  localStorage.clear(); // theme-variant leaks between tests via ThemeContext
  sessionStorage.clear();
  mockInvokeSuccess('get_settings', mockSettings);
  mockInvokeSuccess('get_employees', [
    { id: 1, name: 'John Doe', phone: '1234567890', email: 'john@example.com', employee_type_id: 1, salary: 3000, is_active: true, joined_at: '2024-01-15' },
  ]);
  mockInvokeSuccess('check_auth_required', false);
});

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <MemoryRouter>
      <ThemeProvider>
        <LanguageProvider>
          <AuthProvider>{ui}</AuthProvider>
        </LanguageProvider>
      </ThemeProvider>
    </MemoryRouter>
  );
}

describe('Settings Page', () => {
  it('renders the settings page with restaurant name in form', async () => {
    renderWithProviders(<Settings />);

    const nameInput = await screen.findByDisplayValue('Test Restaurant');
    expect(nameInput).toBeInTheDocument();
  });

  it('renders all tab navigation buttons', async () => {
    renderWithProviders(<Settings />);

    // Tabs have hardcoded English labels — not translation keys.
    // (role="tab" also avoids matching the breadcrumb trail segment)
    const generalTab = await screen.findByRole('tab', { name: 'General' });
    expect(generalTab).toBeInTheDocument();

    expect(screen.getByText('Business')).toBeInTheDocument();
    expect(screen.getByText('Dining')).toBeInTheDocument();
    expect(screen.getByText('Delivery')).toBeInTheDocument();
    const empElements = screen.getAllByText('Employees');
    expect(empElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Database')).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Theme' })).toBeInTheDocument();
  });

  it('shows the single save settings button in the sticky bar', async () => {
    renderWithProviders(<Settings />);

    // Save lives in the sticky breadcrumb bar (Save All Settings) — the old
    // duplicate bottom button was removed.
    const saveBtns = await screen.findAllByText('Save All Settings');
    expect(saveBtns.length).toBeGreaterThanOrEqual(1);
    expect(screen.queryByText('Save Settings')).not.toBeInTheDocument();
  });

  it('shows the breadcrumb bar with the Save All Settings quick action', async () => {
    renderWithProviders(<Settings />);

    // Quick action is always visible in the sticky bar
    expect(await screen.findByText('Save All Settings')).toBeInTheDocument();
    // Breadcrumb trail includes Home → Settings → current tab
    // ('Home' also exists in the side nav, so assert at least one match)
    expect(screen.getAllByText('Home').length).toBeGreaterThanOrEqual(1);
    const settingsCrumb = screen.getAllByText('Settings');
    expect(settingsCrumb.length).toBeGreaterThanOrEqual(1);
  });

  it('opens the import dialog with append/replace mode options', async () => {
    renderWithProviders(<Settings />);

    // Navigate to the Database tab
    fireEvent.click(await screen.findByRole('tab', { name: 'Database' }));
    fireEvent.click(await screen.findByText('Import Database'));

    // Mode selector is shown (no password field when no account is signed in)
    expect(await screen.findByText('Import mode')).toBeInTheDocument();
    expect(screen.getByText('Append data')).toBeInTheDocument();
    expect(screen.getByText('Replace everything')).toBeInTheDocument();

    // Replace is the default selection
    expect(screen.getByRole('button', { name: /Replace everything/ })).toHaveAttribute('aria-pressed', 'true');

    // Switching to Append updates the selection
    fireEvent.click(screen.getByRole('button', { name: /Append data/ }));
    expect(screen.getByRole('button', { name: /Append data/ })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: /Replace everything/ })).toHaveAttribute('aria-pressed', 'false');
  });

  it('asks for the password before exporting when an account is signed in', async () => {
    // Seed a signed-in account so the password gate is enforced
    localStorage.setItem('auth_user', JSON.stringify({ id: 1, email: 'owner@restaurant.com', name: 'Owner' }));
    localStorage.setItem('is_authenticated', 'true');
    mockInvokeSuccess('check_auth_required', true);
    mockInvokeSuccess('has_users', true);
    mockInvokeSuccess('verify_user', true);
    mockInvokeError('login_user', 'Invalid credentials');

    renderWithProviders(<Settings />);

    fireEvent.click(await screen.findByRole('tab', { name: 'Database' }));
    fireEvent.click(await screen.findByText('Export Database'));

    // Gate dialog opens with a password field
    expect(await screen.findByText('Enter your password to export the database.')).toBeInTheDocument();
    const passwordInput = screen.getByLabelText('Password');
    expect(passwordInput).toBeInTheDocument();

    // A wrong password surfaces an inline error (login_user is mocked to fail)
    fireEvent.change(passwordInput, { target: { value: 'wrong-password' } });
    fireEvent.click(screen.getByRole('button', { name: 'Export' }));
    expect(await screen.findByText('Incorrect password. Please try again.')).toBeInTheDocument();
  });


  it('shows phone and email fields', async () => {
    renderWithProviders(<Settings />);

    // Real i18n resolves these from en.json
    const phoneLabel = await screen.findByText('Phone');
    expect(phoneLabel).toBeInTheDocument();

    // 'Email' matches both the Email settings tab and the field label —
    // assert at least one is present.
    const emailElements = screen.getAllByText('Email');
    expect(emailElements.length).toBeGreaterThanOrEqual(1);
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_settings', 'Network error');
    mockInvokeSuccess('get_employees', []);
    mockInvokeSuccess('check_auth_required', false);

    renderWithProviders(<Settings />);

    // Falls back to default name 'POS'
    const nameInput = await screen.findByDisplayValue('Formint');
    expect(nameInput).toBeInTheDocument();
  });

  // ── Tab Switching Tests ──

  it('switches to Business tab and shows business fields', async () => {
    renderWithProviders(<Settings />);

    // Default tab is General — find and click Business
    const businessTab = await screen.findByText('Business');
    fireEvent.click(businessTab);

    // Business tab content should now be visible: Tax Rate, Currency, Opening/Closing Time
    await waitFor(() => {
      expect(screen.getByText('Tax Rate (%)')).toBeInTheDocument();
    });
    expect(screen.getByText('Currency')).toBeInTheDocument();
    expect(screen.getByText('Opening Time')).toBeInTheDocument();
    expect(screen.getByText('Closing Time')).toBeInTheDocument();
  });

  it('switches to Dining tab and shows table config', async () => {
    renderWithProviders(<Settings />);

    const diningTab = await screen.findByText('Dining');
    fireEvent.click(diningTab);

    await waitFor(() => {
      expect(screen.getByText('Number of Tables')).toBeInTheDocument();
    });
    // Verify the table count input has the mock value
    expect(screen.getByDisplayValue('10')).toBeInTheDocument();
  });

  it('switches to Delivery tab and shows delivery fee fields', async () => {
    renderWithProviders(<Settings />);

    const deliveryTab = await screen.findByText('Delivery');
    fireEvent.click(deliveryTab);

    await waitFor(() => {
      // Delivery Fee (flat) (USD) comes from en.json with currency interpolation
      expect(screen.getByText('Delivery Fee (flat) (USD)')).toBeInTheDocument();
    });
    expect(screen.getByText('Delivery Fee per KM (USD)')).toBeInTheDocument();
  });

  it('switches to Employees tab and shows stats', async () => {
    renderWithProviders(<Settings />);

    // Settings tab buttons use role="tab" (sidebar nav items are role="button"),
    // so a role-scoped query matches only the settings Employees tab.
    const employeesTab = screen.getByRole('tab', { name: /Employees/ });
    fireEvent.click(employeesTab);

    await waitFor(() => {
      const totalElements = screen.getAllByText('Total Employees');
      expect(totalElements.length).toBeGreaterThanOrEqual(1);
    });
    const activeElements = screen.getAllByText('Active Employees');
    expect(activeElements.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to Appearance tab and shows theme options', async () => {
    renderWithProviders(<Settings />);

    const appearanceTab = await screen.findByRole('tab', { name: 'Theme' });
    fireEvent.click(appearanceTab);

    await waitFor(() => {
      expect(screen.getByText('Theme Customization')).toBeInTheDocument();
    });
    // Mode options (Light / Dark / System) render inside the ThemeToggle
    // dropdown — open it to reveal them. The trigger shows the current
    // mode too, so Light may appear twice (trigger + option).
    fireEvent.click(screen.getByRole('button', { name: /Theme:/ }));
    expect(screen.getAllByText('Light').length).toBeGreaterThan(0);
    expect(screen.getByText('Dark')).toBeInTheDocument();
    // System mode is supported (follows the OS preference) — the label
    // comes from the i18n key settings.appearanceTab.systemMode ('System Mode')
    expect(screen.getByText('System Mode')).toBeInTheDocument();
  });

  it('renders the Theme Studio token tree with copyable CSS variables', async () => {
    renderWithProviders(<Settings />);

    fireEvent.click(await screen.findByRole('tab', { name: 'Theme' }));

    // Studio section (theme-section-studio anchor) renders the live token tree.
    // 'Theme Studio' also appears on the section-nav button, so scope to the
    // section heading role.
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Theme Studio' })).toBeInTheDocument());
    expect(screen.getByText('--color-primary')).toBeInTheDocument();
    expect(screen.getByText('--color-base-100')).toBeInTheDocument();
    expect(screen.getByText('--radius-box')).toBeInTheDocument();

    // Click a token copies `${token}: <value>;` to the clipboard
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    fireEvent.click(screen.getByText('--color-primary'));
    await waitFor(() => expect(writeText).toHaveBeenCalled());
    expect(writeText.mock.calls[0][0]).toContain('--color-primary');
  });

  it('shows the Active Theme stats and live palette', async () => {
    renderWithProviders(<Settings />);

    fireEvent.click(await screen.findByRole('tab', { name: 'Theme' }));

    // Stats chips (Mode / Variant / Resolved) render in the Active Theme card
    await waitFor(() => expect(screen.getByText('Resolved')).toBeInTheDocument());
    expect(screen.getByText('Variant')).toBeInTheDocument();
    // Live palette labels (Primary / Success / Base 100 …) are present
    expect(screen.getByText('Primary')).toBeInTheDocument();
    expect(screen.getByText('Base 100')).toBeInTheDocument();
  });

  it('switches through multiple tabs in succession', async () => {
    renderWithProviders(<Settings />);

    // General → Business
    fireEvent.click(await screen.findByText('Business'));
    await waitFor(() => expect(screen.getByText('Tax Rate (%)')).toBeInTheDocument());

    // Business → Dining
    fireEvent.click(screen.getByText('Dining'));
    await waitFor(() => expect(screen.getByText('Number of Tables')).toBeInTheDocument());

    // Dining → Delivery
    fireEvent.click(screen.getByText('Delivery'));
    await waitFor(() => expect(screen.getByText('Delivery Fee (flat) (USD)')).toBeInTheDocument());

    // Delivery → Appearance
    fireEvent.click(screen.getByRole('tab', { name: 'Theme' }));
    await waitFor(() => expect(screen.getByText('Theme Customization')).toBeInTheDocument());

    // Appearance → General (back to first tab)
    fireEvent.click(screen.getByText('General'));
    await waitFor(() => expect(screen.getByDisplayValue('Test Restaurant')).toBeInTheDocument());
  });

  // ── Settings Save Flow Tests ──

  // Note: The save flow (invoke('save_settings'), button disabling, success/error
  // toasts) cannot be reliably tested with real framer-motion in jsdom. The
  // state update setIsSaving(true) inside handleSubmit triggers a component
  // re-render that causes framer-motion to silently fail, preventing the async
  // invoke(...) call from executing. The validation test above confirms
  // handleSubmit IS called (the early-return validation path works). To test
  // the full save flow, framer-motion must be mocked (see test-utils.tsx pattern)
  // or use @testing-library/user-event for native browser event simulation.

  it('prevents save with empty restaurant name', async () => {
    renderWithProviders(<Settings />);

    // Clear the restaurant name
    const nameInput = await screen.findByDisplayValue('Test Restaurant');
    fireEvent.change(nameInput, { target: { value: '' } });

    // Try to save (single submit lives in the sticky bar)
    const saveBtn = screen.getByText('Save All Settings');
    fireEvent.click(saveBtn);

    // Validation error should appear — may render in multiple spots (inline + tab badge)
    await waitFor(() => {
      const errorElements = screen.getAllByText('Restaurant name is required');
      expect(errorElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  // ── Theme Variant Selection Tests ──

  it('selects Corporate theme variant from Appearance tab', async () => {
    renderWithProviders(<Settings />);

    // Navigate to Appearance tab
    const appearanceTab = await screen.findByRole('tab', { name: 'Theme' });
    fireEvent.click(appearanceTab);

    // Wait for theme variant buttons to render
    await waitFor(() => {
      expect(screen.getByText('Corporate')).toBeInTheDocument();
    });

    // Click the Corporate variant card (scoped to its title span).
    const corporateButton = screen.getByText('Corporate', { selector: 'span.font-semibold' });
    fireEvent.click(corporateButton);

    // After clicking Corporate, it should show the Active label
    await waitFor(() => {
      // The Active badge should appear — there may be multiple "Active" elements,
      // but at least one should be visible
      const activeBadges = screen.getAllByText('Active');
      expect(activeBadges.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('switches theme variant from Corporate to Pastel', async () => {
    renderWithProviders(<Settings />);

    // Navigate to Appearance tab
    fireEvent.click(await screen.findByRole('tab', { name: 'Theme' }));
    await waitFor(() => expect(screen.getByText('Corporate', { selector: 'span.font-semibold' })).toBeInTheDocument());

    // Select Corporate
    fireEvent.click(screen.getByText('Corporate', { selector: 'span.font-semibold' }));

    // Now switch to Pastel
    await waitFor(() => {
      expect(screen.getByText('Pastel', { selector: 'span.font-semibold' })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Pastel', { selector: 'span.font-semibold' }));

    // Pastel description should be visible
    await waitFor(() => {
      expect(
        screen.getByText('Soft candy colors — light, playful, and inviting')
      ).toBeInTheDocument();
    });
  });

  it('shows all theme variant options (cyberpunk removed)', async () => {
    renderWithProviders(<Settings />);

    fireEvent.click(await screen.findByRole('tab', { name: 'Theme' }));
    await waitFor(() => expect(screen.getByText('Theme Customization')).toBeInTheDocument());

    // All remaining variants should be present (scoped to variant card titles —
    // the ThemeToggle button no longer renders a variant label).
    expect(screen.getByText('Default', { selector: 'span.font-semibold' })).toBeInTheDocument();
    expect(screen.getByText('Corporate', { selector: 'span.font-semibold' })).toBeInTheDocument();
    expect(screen.getByText('Luxury', { selector: 'span.font-semibold' })).toBeInTheDocument();
    expect(screen.getByText('Pastel', { selector: 'span.font-semibold' })).toBeInTheDocument();
    expect(screen.getByText('Perplexity', { selector: 'span.font-semibold' })).toBeInTheDocument();
    expect(screen.queryByText('Cyberpunk', { selector: 'span.font-semibold' })).not.toBeInTheDocument();
  });

  it('toggles between Light and Dark mode in Appearance tab', async () => {
    renderWithProviders(<Settings />);

    fireEvent.click(await screen.findByRole('tab', { name: 'Theme' }));
    await waitFor(() => expect(screen.getByText('Theme Customization')).toBeInTheDocument());

    // Mode options live inside the ThemeToggle dropdown — open it first
    const toggleBtn = screen.getByRole('button', { name: /Theme:/ });
    fireEvent.click(toggleBtn);
    expect(screen.getAllByText('Light').length).toBeGreaterThan(0);
    expect(screen.getByText('Dark')).toBeInTheDocument();

    // Selecting a mode closes the dropdown — reopen between switches
    fireEvent.click(screen.getByText('Dark'));
    fireEvent.click(screen.getByRole('button', { name: /Theme:.*Dark/ }));
    fireEvent.click(screen.getByText('Light'));
    fireEvent.click(screen.getByRole('button', { name: /Theme:.*Light/ }));

    // The toggle reports the selected mode (light)
    expect(screen.getByRole('button', { name: /Theme:.*Light/ })).toBeInTheDocument();
  });
});
