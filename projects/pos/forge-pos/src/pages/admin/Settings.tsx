import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import Card from '../../components/ui/Card';
import { open, save } from '@tauri-apps/plugin-dialog';
import { readFile, writeFile } from '@tauri-apps/plugin-fs';
import { Settings as SettingsType, Employee, DeliveryZone } from '../../types';
import BackButton from '../../components/ui/BackButton';
import PageLayout from '../../components/layout/PageLayout';
import LanguageToggle from '../../components/display/LanguageToggle';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { useKeyboardTabNav } from '../../hooks/useKeyboardTabNav';
import ThemeToggle from '../../components/display/ThemeToggle';
import { useTheme, THEME_VARIANTS, THEME_MAP } from '../../contexts/ThemeContext';

import ThemePreviewModal from '../../components/display/ThemePreviewModal';
import { Ic } from '../../lib/icons';

interface FormErrors {
  restaurant_name?: string;
  email?: string;
  phone?: string;
  tax_rate?: string;
  opening_time?: string;
  closing_time?: string;
  dine_in_tables?: string;
  delivery_fee?: string;
  delivery_fee_per_km?: string;
}

type TabId = 'general' | 'business' | 'dining' | 'delivery' | 'employees' | 'profile' | 'email' | 'database' | 'theme';

interface TabDefinition {
  id: TabId;
  icon: React.ComponentType<{ className?: string }>;
}

// Map each error field to its tab so we know where to navigate
const fieldToTab: Record<string, TabId> = {
  restaurant_name: 'general',
  email: 'general',
  phone: 'general',
  dine_in_tables: 'dining',
  delivery_fee: 'delivery',
  delivery_fee_per_km: 'delivery',
  tax_rate: 'business',
  opening_time: 'business',
  closing_time: 'business',
};


// Heroicon eye icons for the show/hide password toggles
const EyeIcon = Ic('hi:eye');
const EyeSlashIcon = Ic('hi:eye-slash');

const tabs: TabDefinition[] = [
  { id: 'general', icon: Ic('globe') },
  { id: 'business', icon: Ic('briefcase') },
  { id: 'dining', icon: Ic('tools-kitchen-2') },
  { id: 'delivery', icon: Ic('truck') },
  { id: 'employees', icon: Ic('users') },
  { id: 'profile', icon: Ic('user') },
  { id: 'email', icon: Ic('mail') },
  { id: 'database', icon: Ic('database') },
  { id: 'theme', icon: Ic('palette') },
];



const currencyOptions = [
  { code: 'AED', name: 'UAE Dirham', symbol: 'د.إ' },
  { code: 'AFN', name: 'Afghan Afghani', symbol: '؋' },
  { code: 'ALL', name: 'Albanian Lek', symbol: 'L' },
  { code: 'AMD', name: 'Armenian Dram', symbol: '֏' },
  { code: 'ANG', name: 'Netherlands Antillean Guilder', symbol: 'ƒ' },
  { code: 'AOA', name: 'Angolan Kwanza', symbol: 'Kz' },
  { code: 'ARS', name: 'Argentine Peso', symbol: '$' },
  { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
  { code: 'AWG', name: 'Aruban Florin', symbol: 'ƒ' },
  { code: 'AZN', name: 'Azerbaijani Manat', symbol: '₼' },
  { code: 'BAM', name: 'Bosnia-Herzegovina Convertible Mark', symbol: 'KM' },
  { code: 'BBD', name: 'Barbadian Dollar', symbol: '$' },
  { code: 'BDT', name: 'Bangladeshi Taka', symbol: '৳' },
  { code: 'BGN', name: 'Bulgarian Lev', symbol: 'лв' },
  { code: 'BHD', name: 'Bahraini Dinar', symbol: '.د.ب' },
  { code: 'BIF', name: 'Burundian Franc', symbol: 'Fr' },
  { code: 'BMD', name: 'Bermudan Dollar', symbol: '$' },
  { code: 'BND', name: 'Brunei Dollar', symbol: '$' },
  { code: 'BOB', name: 'Bolivian Boliviano', symbol: 'Bs.' },
  { code: 'BRL', name: 'Brazilian Real', symbol: 'R$' },
  { code: 'BSD', name: 'Bahamian Dollar', symbol: '$' },
  { code: 'BTN', name: 'Bhutanese Ngultrum', symbol: 'Nu.' },
  { code: 'BWP', name: 'Botswanan Pula', symbol: 'P' },
  { code: 'BYN', name: 'Belarusian Ruble', symbol: 'Br' },
  { code: 'BZD', name: 'Belize Dollar', symbol: '$' },
  { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
  { code: 'CDF', name: 'Congolese Franc', symbol: 'Fr' },
  { code: 'CHF', name: 'Swiss Franc', symbol: 'Fr' },
  { code: 'CLP', name: 'Chilean Peso', symbol: '$' },
  { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
  { code: 'COP', name: 'Colombian Peso', symbol: '$' },
  { code: 'CRC', name: 'Costa Rican Colón', symbol: '₡' },
  { code: 'CUP', name: 'Cuban Peso', symbol: '$' },
  { code: 'CVE', name: 'Cape Verdean Escudo', symbol: '$' },
  { code: 'CZK', name: 'Czech Koruna', symbol: 'Kč' },
  { code: 'DJF', name: 'Djiboutian Franc', symbol: 'Fr' },
  { code: 'DKK', name: 'Danish Krone', symbol: 'kr' },
  { code: 'DOP', name: 'Dominican Peso', symbol: '$' },
  { code: 'DZD', name: 'Algerian Dinar', symbol: 'د.ج' },
  { code: 'EGP', name: 'Egyptian Pound', symbol: '£' },
  { code: 'ERN', name: 'Eritrean Nakfa', symbol: 'Nfk' },
  { code: 'ETB', name: 'Ethiopian Birr', symbol: 'Br' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'FJD', name: 'Fijian Dollar', symbol: '$' },
  { code: 'FKP', name: 'Falkland Islands Pound', symbol: '£' },
  { code: 'FOK', name: 'Faroese Króna', symbol: 'kr' },
  { code: 'GBP', name: 'British Pound Sterling', symbol: '£' },
  { code: 'GEL', name: 'Georgian Lari', symbol: '₾' },
  { code: 'GGP', name: 'Guernsey Pound', symbol: '£' },
  { code: 'GHS', name: 'Ghanaian Cedi', symbol: '₵' },
  { code: 'GIP', name: 'Gibraltar Pound', symbol: '£' },
  { code: 'GMD', name: 'Gambian Dalasi', symbol: 'D' },
  { code: 'GNF', name: 'Guinean Franc', symbol: 'Fr' },
  { code: 'GTQ', name: 'Guatemalan Quetzal', symbol: 'Q' },
  { code: 'GYD', name: 'Guyanaese Dollar', symbol: '$' },
  { code: 'HKD', name: 'Hong Kong Dollar', symbol: 'HK$' },
  { code: 'HNL', name: 'Honduran Lempira', symbol: 'L' },
  { code: 'HRK', name: 'Croatian Kuna', symbol: 'kn' },
  { code: 'HUF', name: 'Hungarian Forint', symbol: 'Ft' },
  { code: 'IDR', name: 'Indonesian Rupiah', symbol: 'Rp' },
  { code: 'ILS', name: 'Israeli New Shekel', symbol: '₪' },
  { code: 'IMP', name: 'Manx Pound', symbol: '£' },
  { code: 'INR', name: 'Indian Rupee', symbol: '₹' },
  { code: 'IQD', name: 'Iraqi Dinar', symbol: 'ع.د' },
  { code: 'IRR', name: 'Iranian Rial', symbol: '﷼' },
  { code: 'ISK', name: 'Icelandic Króna', symbol: 'kr' },
  { code: 'JEP', name: 'Jersey Pound', symbol: '£' },
  { code: 'JMD', name: 'Jamaican Dollar', symbol: '$' },
  { code: 'JOD', name: 'Jordanian Dinar', symbol: 'د.ا' },
  { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
  { code: 'KES', name: 'Kenyan Shilling', symbol: 'Sh' },
  { code: 'KGS', name: 'Kyrgystani Som', symbol: 'с' },
  { code: 'KHR', name: 'Cambodian Riel', symbol: '៛' },
  { code: 'KID', name: 'Kiribati Dollar', symbol: '$' },
  { code: 'KMF', name: 'Comorian Franc', symbol: 'Fr' },
  { code: 'KRW', name: 'South Korean Won', symbol: '₩' },
  { code: 'KWD', name: 'Kuwaiti Dinar', symbol: 'د.ك' },
  { code: 'KYD', name: 'Cayman Islands Dollar', symbol: '$' },
  { code: 'KZT', name: 'Kazakhstani Tenge', symbol: '₸' },
  { code: 'LAK', name: 'Laotian Kip', symbol: '₭' },
  { code: 'LBP', name: 'Lebanese Pound', symbol: 'ل.ل' },
  { code: 'LKR', name: 'Sri Lankan Rupee', symbol: 'Rs' },
  { code: 'LRD', name: 'Liberian Dollar', symbol: '$' },
  { code: 'LSL', name: 'Lesotho Loti', symbol: 'L' },
  { code: 'LYD', name: 'Libyan Dinar', symbol: 'ل.د' },
  { code: 'MAD', name: 'Moroccan Dirham', symbol: 'د.م.' },
  { code: 'MDL', name: 'Moldovan Leu', symbol: 'L' },
  { code: 'MGA', name: 'Malagasy Ariary', symbol: 'Ar' },
  { code: 'MKD', name: 'Macedonian Denar', symbol: 'ден' },
  { code: 'MMK', name: 'Myanmar Kyat', symbol: 'K' },
  { code: 'MNT', name: 'Mongolian Tugrik', symbol: '₮' },
  { code: 'MOP', name: 'Macanese Pataca', symbol: 'P' },
  { code: 'MRU', name: 'Mauritanian Ouguiya', symbol: 'UM' },
  { code: 'MUR', name: 'Mauritian Rupee', symbol: '₨' },
  { code: 'MVR', name: 'Maldivian Rufiyaa', symbol: '.ރ' },
  { code: 'MWK', name: 'Malawian Kwacha', symbol: 'MK' },
  { code: 'MXN', name: 'Mexican Peso', symbol: '$' },
  { code: 'MYR', name: 'Malaysian Ringgit', symbol: 'RM' },
  { code: 'MZN', name: 'Mozambican Metical', symbol: 'MT' },
  { code: 'NAD', name: 'Namibian Dollar', symbol: '$' },
  { code: 'NGN', name: 'Nigerian Naira', symbol: '₦' },
  { code: 'NIO', name: 'Nicaraguan Córdoba', symbol: 'C$' },
  { code: 'NOK', name: 'Norwegian Krone', symbol: 'kr' },
  { code: 'NPR', name: 'Nepalese Rupee', symbol: '₨' },
  { code: 'NZD', name: 'New Zealand Dollar', symbol: 'NZ$' },
  { code: 'OMR', name: 'Omani Rial', symbol: 'ر.ع.' },
  { code: 'PAB', name: 'Panamanian Balboa', symbol: 'B/.' },
  { code: 'PEN', name: 'Peruvian Sol', symbol: 'S/.' },
  { code: 'PGK', name: 'Papua New Guinean Kina', symbol: 'K' },
  { code: 'PHP', name: 'Philippine Peso', symbol: '₱' },
  { code: 'PKR', name: 'Pakistani Rupee', symbol: '₨' },
  { code: 'PLN', name: 'Polish Zloty', symbol: 'zł' },
  { code: 'PYG', name: 'Paraguayan Guarani', symbol: '₲' },
  { code: 'QAR', name: 'Qatari Riyal', symbol: 'ر.ق' },
  { code: 'RON', name: 'Romanian Leu', symbol: 'lei' },
  { code: 'RSD', name: 'Serbian Dinar', symbol: 'дин.' },
  { code: 'RUB', name: 'Russian Ruble', symbol: '₽' },
  { code: 'RWF', name: 'Rwandan Franc', symbol: 'Fr' },
  { code: 'SAR', name: 'Saudi Riyal', symbol: 'ر.س' },
  { code: 'SBD', name: 'Solomon Islands Dollar', symbol: '$' },
  { code: 'SCR', name: 'Seychellois Rupee', symbol: '₨' },
  { code: 'SDG', name: 'Sudanese Pound', symbol: '£' },
  { code: 'SEK', name: 'Swedish Krona', symbol: 'kr' },
  { code: 'SGD', name: 'Singapore Dollar', symbol: 'S$' },
  { code: 'SHP', name: 'Saint Helena Pound', symbol: '£' },
  { code: 'SLE', name: 'Sierra Leonean Leone', symbol: 'Le' },
  { code: 'SOS', name: 'Somali Shilling', symbol: 'Sh' },
  { code: 'SRD', name: 'Surinamese Dollar', symbol: '$' },
  { code: 'SSP', name: 'South Sudanese Pound', symbol: '£' },
  { code: 'STN', name: 'São Tomé and Príncipe Dobra', symbol: 'Db' },
  { code: 'SYP', name: 'Syrian Pound', symbol: '£S' },
  { code: 'SZL', name: 'Eswatini Lilangeni', symbol: 'L' },
  { code: 'THB', name: 'Thai Baht', symbol: '฿' },
  { code: 'TJS', name: 'Tajikistani Somoni', symbol: 'ЅМ' },
  { code: 'TMT', name: 'Turkmenistani Manat', symbol: 'm' },
  { code: 'TND', name: 'Tunisian Dinar', symbol: 'د.ت' },
  { code: 'TOP', name: 'Tongan Paʻanga', symbol: 'T$' },
  { code: 'TRY', name: 'Turkish Lira', symbol: '₺' },
  { code: 'TTD', name: 'Trinidad and Tobago Dollar', symbol: '$' },
  { code: 'TVD', name: 'Tuvaluan Dollar', symbol: '$' },
  { code: 'TWD', name: 'New Taiwan Dollar', symbol: 'NT$' },
  { code: 'TZS', name: 'Tanzanian Shilling', symbol: 'Sh' },
  { code: 'UAH', name: 'Ukrainian Hryvnia', symbol: '₴' },
  { code: 'UGX', name: 'Ugandan Shilling', symbol: 'Sh' },
  { code: 'USD', name: 'United States Dollar', symbol: '$' },
  { code: 'UYU', name: 'Uruguayan Peso', symbol: '$' },
  { code: 'UZS', name: 'Uzbekistani Som', symbol: "so'm" },
  { code: 'VES', name: 'Venezuelan Bolívar', symbol: 'Bs.' },
  { code: 'VND', name: 'Vietnamese Dong', symbol: '₫' },
  { code: 'VUV', name: 'Vanuatu Vatu', symbol: 'Vt' },
  { code: 'WST', name: 'Samoan Tala', symbol: 'T' },
  { code: 'XAF', name: 'Central African CFA Franc', symbol: 'Fr' },
  { code: 'XCD', name: 'East Caribbean Dollar', symbol: '$' },
  { code: 'XDR', name: 'Special Drawing Rights', symbol: 'SDR' },
  { code: 'XOF', name: 'West African CFA Franc', symbol: 'Fr' },
  { code: 'XPF', name: 'CFP Franc', symbol: 'Fr' },
  { code: 'YER', name: 'Yemeni Rial', symbol: '﷼' },
  { code: 'ZAR', name: 'South African Rand', symbol: 'R' },
  { code: 'ZMW', name: 'Zambian Kwacha', symbol: 'ZK' },
  { code: 'ZWL', name: 'Zimbabwean Dollar', symbol: '$' },
].sort((a, b) => a.name.localeCompare(b.name));

interface CurrencyDropdownProps {
  value: string;
  onChange: (value: string) => void;
}

const CurrencyDropdown = ({ value, onChange }: CurrencyDropdownProps) => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredOptions = currencyOptions.filter(currency =>
    currency.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    currency.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedCurrency = currencyOptions.find(c => c.code === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <div
        onClick={() => setIsOpen(!isOpen)}              className="select w-full cursor-pointer flex items-center justify-between"
      >
        <span>
          {selectedCurrency ? (
            `${selectedCurrency.name} (${selectedCurrency.code} ${selectedCurrency.symbol})`
          ) : t('settings.selectCurrency')}
        </span>
        <span className={`ri-arrow-down-s-line transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </div>
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-base-100 border border-base-300 rounded-lg shadow-xl">
          <div className="p-2">
            <div className="field">
              <input
                type="text"
                placeholder={t('settings.searchCurrency')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input w-full"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          </div>
          <div className="max-h-60 overflow-y-auto scrollbar-thumb-gray-600 scrollbar-track-transparent">
            {filteredOptions.map((currency) => (
              <div
                key={currency.code}
                onClick={() => {
                  onChange(currency.code);
                  setIsOpen(false);
                  setSearchTerm('');
                }}
                className={`px-4 py-2 cursor-pointer flex items-center justify-between
                  ${value === currency.code
                    ? 'bg-primary/10 text-primary'
                    : 'text-base-content hover:bg-base-200/50'}
                  transition-colors duration-200`}
              >
                <span>{currency.name}</span>
                <span className="text-base-content/50">
                  {currency.code} {currency.symbol}
                </span>
              </div>
            ))}
            {filteredOptions.length === 0 && (
              <div className="px-4 py-2 text-base-content/50 text-center">
                {t('settings.noCurrencies')}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};


export default function Settings() {
  const { t, i18n } = useTranslation();
  const { mode, variant, followSystem, setVariant } = useTheme();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabId>('general');
  // Track the previous tab so breadcrumbs can navigate back to it.
  const previousTabRef = useRef<TabId>('general');

  // Wrapped setActiveTab that tracks previous tab for breadcrumb navigation.
  // Used by both click handlers and keyboard navigation.
  const navigateToTab = useCallback((tab: TabId) => {
    if (tab !== activeTab) previousTabRef.current = activeTab;
    setActiveTab(tab);
  }, [activeTab]);

  // ── Arrow-key tab nav ──
  const settingsTabKeys: TabId[] = tabs.map(t => t.id);
  const { onKeyDown: onSettingsTabKeyDown } = useKeyboardTabNav(settingsTabKeys, activeTab, navigateToTab);

  const [settings, setSettings] = useState<SettingsType>({
    restaurant_name: 'Forge POS',
    address: '',
    phone: '',
    email: '',
    tax_rate: '',
    currency: 'USD',
    opening_time: '09:00',
    closing_time: '22:00',
    receipt_footer: '',
    logo: undefined,
    dine_in_tables: 0,
    delivery_fee: 0,
    delivery_fee_per_km: 0,
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_recipient: '',
    smtp_from_name: 'Forge POS',
    smtp_from_email: ''
  });

  const [isSuccess, setIsSuccess] = useState(false);
  const [logoPreview, setLogoPreview] = useState<string | undefined>(undefined);
  const [isNavigating, setIsNavigating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [employeeCount, setEmployeeCount] = useState(0);
  const [activeEmployeeCount, setActiveEmployeeCount] = useState(0);

  // Delivery zone management
  const [deliveryZones, setDeliveryZones] = useState<DeliveryZone[]>([]);
  const [zoneFormOpen, setZoneFormOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<DeliveryZone | null>(null);
  const [zoneForm, setZoneForm] = useState({ name: '', base_fee: 0, fee_per_km: 0, max_distance: 10 });
  const [deleteZoneId, setDeleteZoneId] = useState<number | null>(null);
  const [isSavingZone, setIsSavingZone] = useState(false);


  const [showThemePreview, setShowThemePreview] = useState(false);

  // Password change state
  const { user, isAuthRequired, inactivityTimeout, setInactivityTimeout } = useAuth();
  const [passwordOld, setPasswordOld] = useState('');
  const [passwordNew, setPasswordNew] = useState('');
  const [showPasswordOld, setShowPasswordOld] = useState(false);
  const [showPasswordNew, setShowPasswordNew] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState(false);
  const [passwordChangeError, setPasswordChangeError] = useState('');

  // Dirty tracking: compare current state against last saved snapshot
  const lastSavedSettings = useRef<SettingsType>(settings);
  const [pendingInactivityTimeout, setPendingInactivityTimeout] = useState(inactivityTimeout);

  const hasUnsavedChanges = useMemo(() => {
    const keys: (keyof SettingsType)[] = [
      'restaurant_name', 'address', 'phone', 'email', 'tax_rate', 'tax_id',
      'currency', 'opening_time', 'closing_time', 'receipt_footer',
      'dine_in_tables', 'delivery_fee', 'delivery_fee_per_km',
      'smtp_server', 'smtp_port', 'smtp_username', 'smtp_password',
      'smtp_recipient', 'smtp_from_name', 'smtp_from_email',
    ];
    const current = lastSavedSettings.current;
    for (const k of keys) {
      if ((settings[k] ?? '') !== (current[k] ?? '')) return true;
    }
    if ((settings.logo ?? null) !== (current.logo ?? null)) return true;
    if (pendingInactivityTimeout !== inactivityTimeout) return true;
    return false;
  }, [settings, pendingInactivityTimeout, inactivityTimeout]);

  // Human-readable field names for the error banner
  const fieldLabels: Record<string, string> = {
    restaurant_name: t('settings.fieldLabels.restaurantName'),
    email: t('settings.fieldLabels.email'),
    phone: t('settings.fieldLabels.phone'),
    tax_rate: t('settings.fieldLabels.taxRate'),
    opening_time: t('settings.fieldLabels.openingTime'),
    closing_time: t('settings.fieldLabels.closingTime'),
    dine_in_tables: t('settings.fieldLabels.dineInTables'),
    delivery_fee: t('settings.fieldLabels.deliveryFee'),
    delivery_fee_per_km: t('settings.fieldLabels.perKmFee'),
  };

  // Compute which tabs have errors for badges
  const errorTabs = new Set<TabId>();
  for (const field of Object.keys(errors) as (keyof FormErrors)[]) {
    const tab = fieldToTab[field];
    if (tab && errors[field]) errorTabs.add(tab);
  }

  const handleResetSettings = () => {
    loadSettings();
    setPendingInactivityTimeout(inactivityTimeout);
    setErrors({});
    setSubmitStatus('idle');
    setErrorMessage('');
  };

  const handleBackNavigation = () => {
    setIsNavigating(true);
    setTimeout(() => {
      navigate('/dashboard');
    }, 300);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const isNumber = type === 'number';
    setSettings(prev => ({
      ...prev,
      [name]: isNumber ? (value === '' ? 0 : Number(value)) : value
    }));
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): { valid: boolean; errors: FormErrors } => {
    const newErrors: FormErrors = {};
    if (!settings.restaurant_name || !settings.restaurant_name.trim()) {
      newErrors.restaurant_name = t('settings.validationName');
    }
    if (settings.email && settings.email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(settings.email)) {
      newErrors.email = t('settings.validationEmail');
    }
    if (settings.phone && settings.phone.trim() && !/^[\d\s\-\(\)]+$/.test(settings.phone)) {
      newErrors.phone = t('settings.validationPhone');
    }
    if (settings.tax_rate && settings.tax_rate.trim()) {
      const taxRate = parseFloat(settings.tax_rate);
      if (isNaN(taxRate)) {
        newErrors.tax_rate = t('settings.validationTaxNumber');
      } else if (taxRate < 0 || taxRate > 100) {
        newErrors.tax_rate = t('settings.validationTaxRange');
      }
    }
    if (settings.opening_time && settings.closing_time) {
      if (settings.opening_time >= settings.closing_time) {
        newErrors.opening_time = t('settings.validationOpeningTime');
        newErrors.closing_time = t('settings.validationClosingTime');
      }
    }
    setErrors(newErrors);
    return { valid: Object.keys(newErrors).length === 0, errors: newErrors };
  };

  const handleLogoChange = async () => {
    setIsUploadingLogo(true);
    try {
      const file = await open({
        multiple: false,
        filters: [{ name: 'Image', extensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'] }],
        title: 'Select Restaurant Logo',
      });
      if (file && typeof file === 'string') {
        const contents = await readFile(file);
        let binary = '';
        const chunkSize = 8192;
        for (let i = 0; i < contents.length; i += chunkSize) {
          const chunk = contents.slice(i, Math.min(i + chunkSize, contents.length));
          binary += String.fromCharCode.apply(null, Array.from(chunk));
        }
        const base64 = btoa(binary);
        const extension = file.split('.').pop()?.toLowerCase();
        let mimeType = 'image/jpeg';
        if (extension === 'png') mimeType = 'image/png';
        else if (extension === 'gif') mimeType = 'image/gif';
        else if (extension === 'webp') mimeType = 'image/webp';
        else if (extension === 'bmp') mimeType = 'image/bmp';
        const dataUrl = `data:${mimeType};base64,${base64}`;
        console.log(`[settings] handleLogoChange: logo loaded (${dataUrl.length} chars from ${file})`);
        setLogoPreview(dataUrl);
        setSettings(prev => ({ ...prev, logo: dataUrl }));
      } else {
        console.log('[settings] handleLogoChange: no file selected');
      }
    } catch (error) {
      console.error('[settings] Error selecting logo:', error);
    } finally {
      setIsUploadingLogo(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { valid, errors: newErrors } = validateForm();
    if (!valid) {
      // Check which tabs have errors
      const errFields = Object.keys(newErrors) as (keyof FormErrors)[];
      const tabsWithErrors: TabId[] = [];
      for (const field of errFields) {
        const tab = fieldToTab[field];
        if (tab && !tabsWithErrors.includes(tab)) {
          tabsWithErrors.push(tab);
        }
      }

      // Auto-navigate to the first tab with errors
      if (tabsWithErrors.length > 0) {
        navigateToTab(tabsWithErrors[0]);
      }
      return;
    }
    setIsSaving(true);
    setSubmitStatus('idle');
    setErrorMessage('');
    try {
      const logoInfo = settings.logo
        ? `logo present (${settings.logo.length} chars)`
        : 'logo is undefined/null';
      console.log(`[settings] handleSubmit: saving — ${logoInfo}, name="${settings.restaurant_name}"`);
      await invoke('save_settings', { settings });
      // Persist deferred inactivity timeout
      if (pendingInactivityTimeout !== inactivityTimeout) {
        setInactivityTimeout(pendingInactivityTimeout);
      }
      // Update saved snapshot for dirty tracking
      lastSavedSettings.current = { ...settings };
      setSubmitStatus('success');
      setIsSuccess(true);
      setErrors({});
      setTimeout(() => { setIsSuccess(false); setSubmitStatus('idle'); }, 3000);
    } catch (error) {
      console.error('[settings] Error saving settings:', error);
      setSubmitStatus('error');
      const msg = error instanceof Error ? error.message : t('settings.errorMessage');
      setErrorMessage(msg);
      setTimeout(() => { setSubmitStatus('idle'); setErrorMessage(''); }, 5000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleImportDatabase = async () => {
    setIsImporting(true);
    try {
      const file = await open({
        multiple: false,
        filters: [{ name: 'Database', extensions: ['db'] }],
      });
      if (file) {
        const contents = await readFile(file as string);
        let binary = '';
        const chunkSize = 8192;
        for (let i = 0; i < contents.length; i += chunkSize) {
          const chunk = contents.slice(i, Math.min(i + chunkSize, contents.length));
          binary += String.fromCharCode.apply(null, Array.from(chunk));
        }
        const base64 = btoa(binary);
        await invoke('import_database_cmd', { data: base64 });
        setIsSuccess(true);
        setTimeout(() => setIsSuccess(false), 3000);
        loadSettings();
      }
    } catch (error) {
      console.error('Error importing database:', error);
    } finally {
      setIsImporting(false);
    }
  };

  const handlePasswordChange = async () => {
    if (!user || !passwordOld || !passwordNew) return;
    if (passwordNew.length < 6) {
      setPasswordChangeError(t('settings.validationPasswordLength'));
      return;
    }
    setIsChangingPassword(true);
    setPasswordChangeSuccess(false);
    setPasswordChangeError('');
    try {
      await invoke('change_password_cmd', {
        email: user.email,
        oldPassword: passwordOld,
        newPassword: passwordNew,
      });
      setPasswordChangeSuccess(true);
      setPasswordOld('');
      setPasswordNew('');
      setTimeout(() => setPasswordChangeSuccess(false), 3000);
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      setPasswordChangeError(msg);
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleResetDatabase = async () => {
    if (isImporting || isExporting) return;
    setIsResetting(true);
    setShowResetConfirm(false);
    setSubmitStatus('idle');
    setErrorMessage('');
    try {
      console.log('[settings] handleResetDatabase: resetting database...');
      await invoke('reset_database_cmd');
      console.log('[settings] handleResetDatabase: database reset successful');
      setSubmitStatus('success');
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        setSubmitStatus('idle');
        // Reload the settings after reset
        loadSettings();
      }, 3000);
    } catch (error) {
      console.error('[settings] Error resetting database:', error);
      setSubmitStatus('error');
      const msg = error instanceof Error ? error.message : t('settings.errorMessage');
      setErrorMessage(msg);
      setTimeout(() => { setSubmitStatus('idle'); setErrorMessage(''); }, 5000);
    } finally {
      setIsResetting(false);
    }
  };

  const handleExportDatabase = async () => {
    setIsExporting(true);
    try {
      const base64Data = await invoke<string>('export_database_cmd');
      const date = new Date().toISOString().split('T')[0];
      const filePath = await save({
        defaultPath: `restaurant-database-${date}.db`,
        filters: [{ name: 'Database', extensions: ['db'] }],
      });
      if (filePath) {
        const binary = atob(base64Data);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        await writeFile(filePath, bytes);
        setIsSuccess(true);
        setTimeout(() => setIsSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Error exporting database:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const loadSettings = useCallback(async () => {
    try {
      const loadedSettings = await invoke<SettingsType>('get_settings');
      if (loadedSettings) {
        const logoInfo = loadedSettings.logo
          ? `logo present (${loadedSettings.logo.length} chars)`
          : 'logo is NULL';
        console.log(`[settings] loadSettings: loaded — ${logoInfo}, name="${loadedSettings.restaurant_name}"`);
        setSettings(prev => ({ ...prev, ...loadedSettings }));
        lastSavedSettings.current = { ...loadedSettings };
        if (loadedSettings.logo) {
          setLogoPreview(loadedSettings.logo);
        } else {
          setLogoPreview(undefined);
        }
      } else {
        console.log('[settings] loadSettings: returned null/undefined');
      }
    } catch (error) {
      console.error('[settings] Error loading settings:', error);
    }
  }, []);

  const loadEmployeeStats = useCallback(async () => {
    try {
      const employees = await invoke<Employee[]>('get_employees');
      setEmployeeCount(employees.length);
      setActiveEmployeeCount(employees.filter(e => e.is_active).length);
    } catch {
      // Silently fail — employee stats are non-critical
    }
  }, []);

  const loadZones = useCallback(async () => {
    try {
      const zones = await invoke<DeliveryZone[]>('get_delivery_zones', { includeInactive: true });
      // Guard against the backend returning null/undefined (deliveryZones.length
      // would otherwise crash the Delivery tab render).
      setDeliveryZones(zones ?? []);
    } catch {
      console.error('[settings] Failed to load delivery zones');
    }
  }, []);

  const handleZoneFormOpen = (zone?: DeliveryZone) => {
    if (zone) {
      setEditingZone(zone);
      setZoneForm({ name: zone.name, base_fee: zone.base_fee, fee_per_km: zone.fee_per_km, max_distance: zone.max_distance });
    } else {
      setEditingZone(null);
      setZoneForm({ name: '', base_fee: 0, fee_per_km: 0, max_distance: 10 });
    }
    setZoneFormOpen(true);
  };

  const handleZoneFormSave = async () => {
    if (!zoneForm.name.trim()) return;
    setIsSavingZone(true);
    try {
      if (editingZone) {
        await invoke('update_delivery_zone', { id: editingZone.id, update: { name: zoneForm.name, base_fee: zoneForm.base_fee, fee_per_km: zoneForm.fee_per_km, max_distance: zoneForm.max_distance, is_active: editingZone.is_active } });
      } else {
        await invoke('add_delivery_zone', { zone: zoneForm });
      }
      setZoneFormOpen(false);
      await loadZones();
    } catch (error) {
      console.error('[settings] Error saving zone:', error);
    } finally {
      setIsSavingZone(false);
    }
  };

  const handleDeleteZone = async () => {
    if (deleteZoneId === null) return;
    try {
      await invoke('soft_delete_delivery_zone', { id: deleteZoneId });
      setDeleteZoneId(null);
      await loadZones();
    } catch (error) {
      console.error('[settings] Error deleting zone:', error);
    }
  };

  useEffect(() => {
    loadSettings();
    loadEmployeeStats();
    loadZones();
  }, [loadSettings, loadEmployeeStats, loadZones]);

  // ---- Shared Input Classes (FlyonUI) ----
  // BEM input helpers — maps flyonui classes to standardized BEM tokens
  const BEM = {
    field: 'input w-full',
    label: 'label-text',
    msg: 'helper-text',
    wrap: (hasError?: boolean) => hasError ? 'field field--error' : 'field',
  };

  // ---- Tab: Theme ----
  const renderThemeTab = () => (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
        <button
          type="button"
          onClick={() => setActiveTab(previousTabRef.current === activeTab ? 'general' : previousTabRef.current)}
          className="flex items-center gap-1.5 text-base-content/60 hover:text-primary transition-colors duration-200"
        >
          <span className="ri-arrow-left-line ri-16px" />
          <span>{t('settings.backToSettings') || 'Settings'}</span>
        </button>
        <span className="text-base-content/30">/</span>
        <span className="text-base-content/70 font-medium">{t('settings.themeTab.title') || 'Theme'}</span>
      </nav>

      {/* ── Theme Section Navigation ── */}
      <div className="sticky top-0 z-10 bg-base-100/95 backdrop-blur-sm border-b border-base-300/50 -mx-1 px-1 py-2 overflow-x-auto">
        <div className="flex items-center gap-1">
          {[
            { id: 'theme-section-appearance', label: t('settings.themeTab.appearance'), icon: 'ri-paint-brush-line' },
            { id: 'theme-section-studio', label: t('settings.themeTab.studio'), icon: 'ri-palette-line' },
            { id: 'theme-section-preview', label: t('settings.themeTab.preview'), icon: 'ri-eye-line' },
            { id: 'theme-section-active', label: t('settings.themeTab.activeTheme'), icon: 'ri-information-line' },
          ].map(item => (
            <button
              key={item.id}
              type="button"
              onClick={() => document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                text-base-content/60 hover:text-base-content hover:bg-base-200/50
                transition-colors duration-200 whitespace-nowrap"
            >
              <span className={`${item.icon} ri-14px`} />
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Theme Mode Toggle ── */}
      <div className="card bg-base-200 border border-base-300 p-6">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {mode === 'dark' ? (
              <div className="bg-primary/10 rounded-full p-2.5">
                <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" /></svg>
              </div>
            ) : (
              <div className="bg-warning/10 rounded-full p-2.5">
                <svg className="w-5 h-5 text-warning" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" /></svg>
              </div>
            )}
            <div>
              <h3 className="font-semibold text-base-content">
                {t('settings.appearanceTab.modeTitle') || 'Theme Mode'}
              </h3>
              <p className="text-sm text-base-content/60">{t('settings.appearanceTab.modeDescription')}</p>
            </div>
          </div>
          <ThemeToggle />
        </div>
        <p className="mt-3 text-xs text-base-content/40 text-center">
          {followSystem
            ? t('settings.appearanceTab.systemControlled') || 'Following system preference'
            : mode === 'dark'
              ? t('settings.appearanceTab.darkModeSelected') || 'Dark mode selected'
              : t('settings.appearanceTab.lightModeSelected') || 'Light mode selected'
          }
        </p>
      </div>

      {/* ── Theme Variant Selector (Appearance) ── */}
      <div id="theme-section-appearance" className="scroll-mt-20" />
      <div className="card bg-base-200 border border-base-300 p-6">
        <div className="flex items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 rounded-full p-2.5">
              <span className="ri-paint-brush-line ri-20px text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-base-content">{t('settings.appearanceTab.title')}</h3>
              <p className="text-sm text-base-content/50">{t('settings.appearanceTab.description')}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowThemePreview(true)}
            className="btn btn-primary btn-sm gap-2"
          >
            <span className="ri-eye-line ri-16px" />
            {t('settings.appearanceTab.previewTitle') || 'Preview Theme'}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {THEME_VARIANTS.map((v) => {
            const isActive = variant === v.id;
            const descKey = `settings.appearanceTab.${v.id}Desc`;
            return (
              <button
                key={v.id}
                type="button"
                onClick={() => setVariant(v.id)}
                className={`relative flex items-start gap-3 p-4 rounded-xl text-left transition-all duration-200 border-2 ${
                  isActive
                    ? 'border-primary bg-primary/10 shadow-md shadow-primary/10'
                    : 'border-base-300/50 bg-base-100/50 hover:border-base-300 hover:shadow-sm'
                }`}
              >
                <span className={`${v.icon} ri-20px animate-scale-in`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-base-content text-sm">
                      {t(`settings.appearanceTab.theme${v.label}`, v.label)}
                    </span>
                    {isActive && (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-primary/10 text-primary">
                        {t('settings.appearanceTab.activeLabel')}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-base-content/50 mt-0.5">
                    {t(descKey, v.description)}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>


      {/* Theme Preview Card */}
      <div id="theme-section-preview" className="scroll-mt-20" />
      <div className="card bg-base-200 border border-base-300 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-primary/10 rounded-full p-2.5">
            <span className="ri-palette-line ri-20px text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-base-content">Component Preview</h3>
            <p className="text-sm text-base-content/50">Preview buttons, forms, alerts, badges, and more across all 5 theme variants</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowThemePreview(true)}
          className="btn btn-primary btn-sm gap-2"
        >
          <span className="ri-eye-line ri-16px" />
          Preview Theme Components
        </button>
      </div>

      {/* Current Theme Info */}
      <div id="theme-section-active" className="scroll-mt-20" />
      <div className="card bg-base-200 border border-base-300 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-info/10 rounded-full p-2.5">
            <span className="ri-information-line ri-20px text-info" />
          </div>
          <div>
            <h3 className="font-semibold text-base-content">Active Theme</h3>
            <p className="text-sm text-base-content/50">Current theme configuration</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="px-3 py-2 rounded-lg bg-base-100/50">
            <span className="text-base-content/50">Mode:</span>{' '}
            <span className="font-medium text-base-content capitalize">{followSystem ? 'System' : mode}</span>
          </div>
          <div className="px-3 py-2 rounded-lg bg-base-100/50">
            <span className="text-base-content/50">Variant:</span>{' '}
            <span className="font-medium text-base-content capitalize">{variant}</span>
          </div>
          <div className="col-span-2 px-3 py-2 rounded-lg bg-base-100/50">
            <span className="text-base-content/50">Resolved:</span>{' '}
            <code className="text-primary text-xs font-mono">{THEME_MAP[variant][mode]}</code>
          </div>
        </div>
      </div>
    </div>
  );

  // ---- Tab Content ----
  const renderGeneralTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Logo */}
      <div className="md:col-span-2">
        <label className={BEM.label}>{t('settings.businessLogo') || 'Business Logo (appears on invoices & receipts)'}</label>
        <div className="flex items-center gap-6">
          {logoPreview && (
            <div className="relative w-24 h-24 shrink-0">
              <img src={logoPreview} alt={t('settings.logoPreviewAlt')} className="rounded-full object-cover w-full h-full bg-white/20" />
              <button
                type="button"
                onClick={() => { setLogoPreview(undefined); setSettings(prev => ({ ...prev, logo: null })); }}
                className="btn btn-circle btn-error btn-xs absolute -top-2 -right-2 rtl:-left-2 rtl:right-auto shadow-lg"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          )}
          <button
            type="button"
            onClick={handleLogoChange}
            disabled={isUploadingLogo}
            className="flex flex-col items-center justify-center px-6 py-5 bg-base-100/30
              text-base-content/70 rounded-lg border-2 border-slate-300 dark:border-gray-600
              border-dashed cursor-pointer hover:border-primary hover:bg-primary/5 transition-all
              disabled:opacity-50 disabled:cursor-not-allowed flex-1"
          >
            {isUploadingLogo ? (
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"
              />
            ) : (
              <>
                <svg className="w-8 h-8 mb-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="text-sm">{logoPreview ? t('settings.changeLogo') : t('settings.uploadLogo')}</span>
              </>
            )}
          </button>
        </div>
        <p className="mt-2 text-xs text-base-content/50">{t('settings.generalTab.logoFormats')}</p>
      </div>

      {/* Restaurant Name */}
      <div>
        <div className={BEM.wrap(!!errors.restaurant_name)}>
          <label className={BEM.label}>{t('settings.restaurantName')} <span className="text-red-400">*</span></label>
          <input type="text" name="restaurant_name" value={settings.restaurant_name} onChange={handleChange}
            className={BEM.field} />
          {errors.restaurant_name && <p className={BEM.msg}><span className="ri-alert-line text-xs" />{errors.restaurant_name}</p>}
        </div>
      </div>

      {/* Language */}
      <div>
        <label className={BEM.label}>{t('settings.generalTab.languageLabel')}</label>
        <div className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-base-100/50 border border-slate-300 dark:border-gray-600">
          <span className="text-sm text-base-content flex-1">
            {i18n.language === 'ar' ? t('settings.generalTab.languageValueAr') : i18n.language === 'fr' ? t('settings.generalTab.languageValueFr') : i18n.language === 'de' ? t('settings.generalTab.languageValueDe') : i18n.language === 'es' ? t('settings.generalTab.languageValueEs') : t('settings.generalTab.languageValueEn')}
          </span>
          <LanguageToggle />
        </div>
        <p className="mt-1.5 text-xs text-base-content/50">
          {t('settings.generalTab.languageDesc')}
        </p>
      </div>

      {/* Inactivity Timeout — only when authenticated */}
      {isAuthRequired && user && (
        <div className="md:col-span-2">
          <div className="border-t border-slate-300/50 dark:border-gray-600/50 pt-6 mt-2">
            <h3 className="text-lg font-semibold text-base-content mb-1">
              <span className="ri-time-line inline mr-2 text-primary/80" />
              {t('settings.inactivityTimeout')}
            </h3>
            <p className="text-sm text-base-content/50 mb-4">
              {t('settings.inactivityTimeoutDesc')}
            </p>
            <div className="max-w-xs">
              <select
                value={pendingInactivityTimeout}
                onChange={(e) => setPendingInactivityTimeout(e.target.value)}
                className="select w-full"
              >
                <option value="never">{t('settings.timeoutNever')}</option>
                <option value="5">{t('settings.timeout5min')}</option>
                <option value="15">{t('settings.timeout15min')}</option>
                <option value="30">{t('settings.timeout30min')}</option>
                <option value="60">{t('settings.timeout1hour')}</option>
                <option value="120">{t('settings.timeout2hours')}</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Phone */}
      <div>
        <div className={BEM.wrap(!!errors.phone)}>
          <label className={BEM.label}>{t('settings.phone')}</label>
          <input type="tel" name="phone" value={settings.phone} onChange={handleChange} className={BEM.field} />
          {errors.phone && <p className={BEM.msg}><span className="ri-alert-line text-xs" />{errors.phone}</p>}
        </div>
      </div>

      {/* Email */}
      <div>
        <div className={BEM.wrap(!!errors.email)}>
          <label className={BEM.label}>{t('settings.email')}</label>
          <input type="email" name="email" value={settings.email} onChange={handleChange} className={BEM.field} />
          {errors.email && <p className={BEM.msg}><span className="ri-alert-line text-xs" />{errors.email}</p>}
        </div>
      </div>

      {/* Address */}
      <div className="field">
        <label className={BEM.label}>{t('settings.address')}</label>
        <textarea name="address" value={settings.address} onChange={handleChange} rows={3} className="textarea w-full" />
      </div>
    </div>
  );

  const renderProfileTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Account Info Card */}
      <div className="md:col-span-2">
        <div className="card bg-base-200 border border-base-300 p-5 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-primary/10 dark:bg-primary/20 rounded-full p-2.5">
              <span className="ri-user-line ri-20px text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-base-content">{t('settings.profileTab.title') || 'Profile & Account'}</h3>
              <p className="text-sm text-base-content/50">{t('settings.profileTab.description') || 'Manage your account details and security'}</p>
            </div>
          </div>
          {user ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="field">
                <label className={BEM.label}>{t('settings.profileTab.name') || 'Name'}</label>
                <input type="text" value={user.name || ''} readOnly className="input w-full opacity-70" />
              </div>
              <div className="field">
                <label className={BEM.label}>{t('settings.profileTab.email') || 'Email'}</label>
                <input type="email" value={user.email || ''} readOnly className="input w-full opacity-70" />
              </div>
            </div>
          ) : (
            <p className="text-sm text-base-content/50">{t('settings.profileTab.noUser') || 'No signed-in account.'}</p>
          )}
        </div>
      </div>

      {/* Password Change — only when authenticated */}
      {isAuthRequired && user && (
        <div className="md:col-span-2">
          <div className="card bg-base-200 border border-base-300 p-5">
            <h3 className="text-lg font-semibold text-base-content mb-1">
              <span className="ri-lock-2-line inline mr-2 text-primary/80" />
              {t('settings.changePassword')}
            </h3>
            <p className="text-sm text-base-content/50 mb-4">
              {t('settings.changePasswordDesc')} <strong>{user.email}</strong>
            </p>

            {passwordChangeSuccess && (
              <div role="alert" className="alert alert-success mb-4">
                <span className="ri-check-line ri-16px" />
                <span>{t('settings.passwordChangeSuccess')}</span>
              </div>
            )}

            {passwordChangeError && (
              <div role="alert" className="alert alert-error mb-4">
                <span className="ri-alert-line ri-16px" />
                <span>{passwordChangeError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="field">
                <label className={BEM.label}>{t('settings.currentPassword')}</label>
                <div className="relative">
                  <input
                    type={showPasswordOld ? 'text' : 'password'}
                    value={passwordOld}
                    onChange={(e) => { setPasswordOld(e.target.value); setPasswordChangeSuccess(false); setPasswordChangeError(''); }}
                    placeholder="••••••••"
                    className="input w-full pe-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordOld(s => !s)}
                    aria-pressed={showPasswordOld}
                    aria-label={t('auth.showPassword')}
                    className="absolute inset-y-0 end-2 my-auto flex items-center justify-center
                      text-base-content/50 hover:text-base-content transition-colors"
                  >
                    {showPasswordOld
                      ? <EyeSlashIcon className="size-4" />
                      : <EyeIcon className="size-4" />}
                  </button>
                </div>
              </div>
              <div className="field">
                <label className={BEM.label}>{t('settings.newPassword')}</label>
                <div className="relative">
                  <input
                    type={showPasswordNew ? 'text' : 'password'}
                    value={passwordNew}
                    onChange={(e) => { setPasswordNew(e.target.value); setPasswordChangeSuccess(false); setPasswordChangeError(''); }}
                    placeholder="••••••••"
                    className="input w-full pe-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordNew(s => !s)}
                    aria-pressed={showPasswordNew}
                    aria-label={t('auth.showPassword')}
                    className="absolute inset-y-0 end-2 my-auto flex items-center justify-center
                      text-base-content/50 hover:text-base-content transition-colors"
                  >
                    {showPasswordNew
                      ? <EyeSlashIcon className="size-4" />
                      : <EyeIcon className="size-4" />}
                  </button>
                </div>
              </div>
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={handlePasswordChange}
                  disabled={isChangingPassword || !passwordOld || !passwordNew}
                  className="btn btn-primary w-full"
                >
                  {isChangingPassword ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <><span className="ri-lock-2-line text-sm" /> {t('settings.updatePassword')}</>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inactivity Timeout — only when authenticated */}
      {isAuthRequired && user && (
        <div className="md:col-span-2">
          <div className="card bg-base-200 border border-base-300 p-5">
            <h3 className="text-lg font-semibold text-base-content mb-1">
              <span className="ri-time-line inline mr-2 text-primary/80" />
              {t('settings.inactivityTimeout')}
            </h3>
            <p className="text-sm text-base-content/50 mb-4">
              {t('settings.inactivityTimeoutDesc')}
            </p>
            <div className="max-w-xs">
              <select
                value={pendingInactivityTimeout}
                onChange={(e) => setPendingInactivityTimeout(e.target.value)}
                className="select w-full"
              >
                <option value="never">{t('settings.timeoutNever')}</option>
                <option value="5">{t('settings.timeout5min')}</option>
                <option value="15">{t('settings.timeout15min')}</option>
                <option value="30">{t('settings.timeout30min')}</option>
                <option value="60">{t('settings.timeout1hour')}</option>
                <option value="120">{t('settings.timeout2hours')}</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderEmailTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Email / SMTP Configuration — stored in DB (replaces .env SMTP_* vars) */}
      <div className="md:col-span-2">
        <div className="card bg-base-200 border border-base-300 p-5 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-sky-100 dark:bg-sky-800/30 rounded-full p-2.5">
              <span className="ri-mail-line ri-20px text-sky-600 dark:text-sky-400" />
            </div>
            <div>
              <h3 className="font-semibold text-base-content">{t('settings.emailTab.title')}</h3>
              <p className="text-sm text-base-content/50">{t('settings.emailTab.description')}</p>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.server')}</label>
              <input type="text" name="smtp_server" value={settings.smtp_server || ''} onChange={handleChange}
                placeholder="smtp.gmail.com" className="input w-full" />
            </div>
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.port')}</label>
              <input type="number" name="smtp_port" value={settings.smtp_port ?? 587} onChange={handleChange}
                min="1" max="65535" className="input w-full" />
            </div>
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.username')}</label>
              <input type="text" name="smtp_username" value={settings.smtp_username || ''} onChange={handleChange}
                autoComplete="off" placeholder="you@example.com" className="input w-full" />
            </div>
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.password')}</label>
              <input type="password" name="smtp_password" value={settings.smtp_password || ''} onChange={handleChange}
                autoComplete="new-password" placeholder="••••••••" className="input w-full" />
            </div>
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.recipient')}</label>
              <input type="email" name="smtp_recipient" value={settings.smtp_recipient || ''} onChange={handleChange}
                placeholder="support@yourrestaurant.com" className="input w-full" />
              <p className="helper-text mt-1">{t('settings.emailTab.recipientHint')}</p>
            </div>
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.fromName')}</label>
              <input type="text" name="smtp_from_name" value={settings.smtp_from_name || ''} onChange={handleChange}
                className="input w-full" />
            </div>
            <div className="field">
              <label className={BEM.label}>{t('settings.emailTab.fromEmail')}</label>
              <input type="email" name="smtp_from_email" value={settings.smtp_from_email || ''} onChange={handleChange}
                placeholder="no-reply@yourrestaurant.com" className="input w-full" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderBusinessTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Tax Rate */}
      <div>
        <div className={BEM.wrap(!!errors.tax_rate)}>
          <label className={BEM.label}>{t('settings.taxRate')}</label>
          <input type="number" name="tax_rate" value={settings.tax_rate} onChange={handleChange}
            step="0.01" min="0" max="100" className={BEM.field} />
          {errors.tax_rate && <p className={BEM.msg}><span className="ri-alert-line text-xs" />{errors.tax_rate}</p>}
        </div>
      </div>

      {/* Tax ID */}
      <div className="field">
        <label className={BEM.label}>{t('settings.taxId') || 'Tax ID'}</label>
        <input type="text" name="tax_id" value={settings.tax_id || ''} onChange={handleChange}
          placeholder="e.g. NTN-1234567" className="input w-full" />
      </div>

      {/* Currency */}
      <div>
        <label className={BEM.label}>{t('settings.currency')}</label>
        <CurrencyDropdown value={settings.currency || 'USD'} onChange={(v) => setSettings(prev => ({ ...prev, currency: v }))} />
      </div>

      {/* Opening Time */}
      <div>
        <div className={BEM.wrap(!!errors.opening_time)}>
          <label className={BEM.label}>{t('settings.openingTime')}</label>
          <input type="time" name="opening_time" value={settings.opening_time} onChange={handleChange} className={BEM.field} />
          {errors.opening_time && <p className={BEM.msg}><span className="ri-alert-line text-xs" />{errors.opening_time}</p>}
        </div>
      </div>

      {/* Closing Time */}
      <div>
        <div className={BEM.wrap(!!errors.closing_time)}>
          <label className={BEM.label}>{t('settings.closingTime')}</label>
          <input type="time" name="closing_time" value={settings.closing_time} onChange={handleChange} className={BEM.field} />
          {errors.closing_time && <p className={BEM.msg}><span className="ri-alert-line text-xs" />{errors.closing_time}</p>}
        </div>
      </div>

      {/* Receipt Footer */}
      <div className="field md:col-span-2">
        <label className={BEM.label}>{t('settings.receiptFooter')}</label>
        <textarea name="receipt_footer" value={settings.receipt_footer} onChange={handleChange}
          rows={3} className="textarea w-full"
          placeholder={t('settings.receiptFooterPlaceholder')} />
      </div>
    </div>
  );

  const renderDiningTab = () => (
    <div className="max-w-lg mx-auto">
      <div className="card bg-base-200 border border-base-300 p-6 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-amber-100 dark:bg-amber-800/30 rounded-full p-2.5">
            <span className="ri-restaurant-2-line ri-20px text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-base-content">{t('settings.diningTab.title')}</h3>
            <p className="text-sm text-base-content/50">{t('settings.diningTab.description')}</p>
          </div>
        </div>
        <div className="field">
          <label className={BEM.label}>{t('settings.numberOfTables')}</label>
          <input type="number" name="dine_in_tables" value={settings.dine_in_tables ?? 0}
            onChange={handleChange} min="0"
            className="input w-full" />
          <p className="mt-1.5 text-xs text-base-content/50">
            {t('settings.diningTab.zeroToDisable')}
          </p>
        </div>
      </div>
    </div>
  );

  const renderDeliveryTab = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
        <button
          type="button"
          onClick={() => setActiveTab(previousTabRef.current === activeTab ? 'general' : previousTabRef.current)}
          className="flex items-center gap-1.5 text-base-content/60 hover:text-primary transition-colors duration-200"
        >
          <span className="ri-arrow-left-line ri-16px" />
          <span>{t('settings.backToSettings') || 'Settings'}</span>
        </button>
        <span className="text-base-content/30">/</span>
        <span className="text-base-content/70 font-medium">{t('settings.tabs.delivery')}</span>
      </nav>

      {/* Delivery Fee Settings */}
      <div className="card bg-base-200 border border-base-300 p-6 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-sky-100 dark:bg-sky-800/30 rounded-full p-2.5">
            <span className="ri-truck-line ri-20px text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 className="font-semibold text-base-content">{t('settings.deliveryTab.title')}</h3>
            <p className="text-sm text-base-content/50">{t('settings.deliveryTab.description')}</p>
          </div>
        </div>
        <div className="space-y-6">
          <div>
            <label className={BEM.label}>{t('settings.deliveryFeeFlat', { currency: settings.currency || 'USD' })}</label>
            <input type="number" name="delivery_fee" value={settings.delivery_fee ?? 0}
              onChange={handleChange} min="0" step="0.5" className={BEM.field} />
          </div>
          <div>
            <label className={BEM.label}>{t('settings.deliveryFeePerKm', { currency: settings.currency || 'USD' })}</label>
            <input type="number" name="delivery_fee_per_km" value={settings.delivery_fee_per_km ?? 0}
              onChange={handleChange} min="0" step="0.1" className={BEM.field} />
            <p className="mt-1.5 text-xs text-base-content/50">
              {t('settings.deliveryTab.perKmDescription')}
            </p>
          </div>
        </div>
      </div>

      {/* Delivery Zone Management */}
      <div className="card bg-base-200 border border-base-300 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="bg-success/10 dark:bg-emerald-800/30 rounded-full p-2.5">
              <span className="ri-map-pin-2-line ri-20px text-success dark:text-success/80" />
            </div>
            <div>
              <h3 className="font-semibold text-base-content">Delivery Zones</h3>
              <p className="text-xs text-base-content/50">Manage distance-based delivery pricing by city/zone</p>
            </div>
          </div>
          <button type="button" onClick={() => handleZoneFormOpen()}
            className="btn btn-primary btn-sm gap-1.5">
            <span className="ri-add-line ri-16px" /> Add Zone
          </button>
        </div>

        {/* Zone Table */}
        {deliveryZones.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <span className="ri-map-2-line ri-40px mx-auto mb-2 block opacity-50" />
            <p className="text-sm">No delivery zones configured. Click "Add Zone" to create one.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full text-sm">
              <thead>
                <tr>
                  <th>Zone</th>
                  <th>Base Fee</th>
                  <th>Per KM</th>
                  <th>Max Dist.</th>
                  <th>Status</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {deliveryZones.map(zone => (
                  <tr key={zone.id} className={!zone.is_active ? 'opacity-50' : ''}>
                    <td className="font-medium">{zone.name}</td>
                    <td>{settings.currency} {zone.base_fee.toFixed(2)}</td>
                    <td>{settings.currency} {zone.fee_per_km.toFixed(2)}</td>
                    <td>{zone.max_distance} km</td>
                    <td>
                      <span className={`tag tag--sm ${zone.is_active ? 'tag--success' : 'tag--ghost'}`}>
                        {zone.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button type="button" onClick={() => handleZoneFormOpen(zone)}
                          className="btn btn-ghost btn-xs btn-square" title="Edit">
                          <span className="ri-pencil-line ri-16px" />
                        </button>
                        <button type="button" onClick={() => setDeleteZoneId(zone.id)}
                          className="btn btn-ghost btn-xs btn-square text-red-500" title="Deactivate">
                          <span className="ri-delete-bin-line ri-16px" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Add/Edit Zone Form Modal */}
        {zoneFormOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={() => setZoneFormOpen(false)}>
            <div className="bg-base-100 rounded-2xl p-6 w-full max-w-md shadow-2xl border border-slate-200 dark:border-slate-700" onClick={e => e.stopPropagation()}>
              <h3 className="text-lg font-semibold text-base-content mb-4">
                {editingZone ? `Edit Zone: ${editingZone.name}` : 'Add Delivery Zone'}
              </h3>
              <div className="space-y-4">
                <div className="field">
                  <label className={BEM.label}>Zone Name *</label>
                  <input type="text" value={zoneForm.name} onChange={e => setZoneForm(p => ({ ...p, name: e.target.value }))}
                    className="input w-full" placeholder="e.g. Downtown" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="field">
                    <label className={BEM.label}>Base Fee ({settings.currency})</label>
                    <input type="number" value={zoneForm.base_fee} onChange={e => setZoneForm(p => ({ ...p, base_fee: Number(e.target.value) }))}
                      min="0" step="0.5" className="input w-full" />
                  </div>
                  <div className="field">
                    <label className={BEM.label}>Fee Per KM</label>
                    <input type="number" value={zoneForm.fee_per_km} onChange={e => setZoneForm(p => ({ ...p, fee_per_km: Number(e.target.value) }))}
                      min="0" step="0.1" className="input w-full" />
                  </div>
                </div>
                <div className="field">
                  <label className={BEM.label}>Max Distance (km)</label>
                  <input type="number" value={zoneForm.max_distance} onChange={e => setZoneForm(p => ({ ...p, max_distance: Number(e.target.value) }))}
                    min="0" step="1" className="input w-full" />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setZoneFormOpen(false)}
                  className="btn btn-ghost">Cancel</button>
                <button type="button" onClick={handleZoneFormSave} disabled={!zoneForm.name.trim() || isSavingZone}
                  className="btn btn-primary">
                  {isSavingZone ? <span className="loading loading-spinner loading-sm" /> : (editingZone ? 'Update Zone' : 'Add Zone')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation */}
        {deleteZoneId !== null && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" onClick={() => setDeleteZoneId(null)}>
            <div className="bg-base-100 rounded-2xl p-6 w-full max-w-sm shadow-2xl border border-slate-200 dark:border-slate-700" onClick={e => e.stopPropagation()}>
              <div className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="bg-red-500/20 rounded-full p-4">
                    <span className="ri-alert-line text-4xl text-red-500" />
                  </div>
                </div>
                <h3 className="text-xl font-bold text-base-content mb-2">Deactivate Zone?</h3>
                <p className="text-base-content/70 text-sm">
                  This will disable this delivery zone. You can re-enable it later.
                </p>
              </div>
              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setDeleteZoneId(null)}
                  className="btn btn-ghost flex-1">Cancel</button>
                <button type="button" onClick={handleDeleteZone}
                  className="btn btn-error flex-1">
                  <span className="ri-delete-bin-line ri-16px" /> Deactivate
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderEmployeesTab = () => (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm" aria-label="Breadcrumb">
        <button
          type="button"
          onClick={() => setActiveTab(previousTabRef.current === activeTab ? 'general' : previousTabRef.current)}
          className="flex items-center gap-1.5 text-base-content/60 hover:text-primary transition-colors duration-200"
        >
          <span className="ri-arrow-left-line ri-16px" />
          <span>{t('settings.backToSettings') || 'Settings'}</span>
        </button>
        <span className="text-base-content/30">/</span>
        <span className="text-base-content/70 font-medium">{t('settings.tabs.employees')}</span>
      </nav>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-white/40 dark:bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-base-300/50">
          <div className="flex items-center gap-3">
            <div className="bg-info/10 dark:bg-info/30 rounded-full p-2.5">
              <span className="ri-group-line ri-20px text-info dark:text-indigo-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-base-content">{employeeCount}</p>
              <p className="text-xs text-base-content/50">{t('settings.employeesTab.totalEmployees')}</p>
            </div>
          </div>
        </div>
        <div className="bg-white/40 dark:bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-base-300/50">
          <div className="flex items-center gap-3">
            <div className="bg-success/10 dark:bg-emerald-800/30 rounded-full p-2.5">
              <span className="ri-check-line ri-20px text-success dark:text-success/80" />
            </div>
            <div>
              <p className="text-2xl font-bold text-base-content">{activeEmployeeCount}</p>
              <p className="text-xs text-base-content/50">{t('settings.employeesTab.activeEmployees')}</p>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-white/40 dark:bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-base-300/50">
        <h3 className="font-semibold text-base-content mb-3">{t('settings.employeesTab.managementTitle')}</h3>
        <p className="text-sm text-base-content/60 mb-4">
          {t('settings.employeesTab.managementDesc')}
        </p>
        <button
          type="button"
          onClick={() => navigate('/employees')}            className="btn btn-info gap-2"
        >
          <span className="ri-group-line ri-16px" />
          {t('settings.employeesTab.goToEmployees')}
        </button>
      </div>
    </div>
  );

  const renderDatabaseTab = () => (
    <div className="max-w-lg mx-auto">
      <div className="card bg-base-200 border border-base-300 p-6 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-purple-100 dark:bg-purple-800/30 rounded-full p-2.5">
            <span className="ri-database-2-line ri-20px text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold text-base-content">{t('settings.databaseTab.title')}</h3>
            <p className="text-sm text-base-content/50">{t('settings.databaseTab.description')}</p>
          </div>
        </div>

        {/* Database Info Card */}
        <div className="bg-base-100/50 rounded-lg p-4 mb-6 border border-base-300/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-base-content/60">{t('settings.databaseTab.status')}</span>
            <span className="tag tag--sm tag--success">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              {t('settings.databaseTab.connected')}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-base-content/60">{t('settings.databaseTab.type')}</span>
            <span className="text-sm font-medium text-base-content">{t('settings.databaseTab.sqlite')}</span>
          </div>
        </div>

        {/* Import / Export */}
        <div className="space-y-3">
          <button
            type="button"
            onClick={handleImportDatabase}
            disabled={isImporting}
            className="w-full py-3 bg-primary hover:brightness-90 text-primary-content rounded-xl
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isImporting ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <><span className="ri-file-transfer-line text-lg" />{t('settings.importDatabase')}</>
            )}
          </button>
          <button
            type="button"
            onClick={handleExportDatabase}
            disabled={isExporting}
            className="w-full py-3 bg-primary hover:brightness-90 text-primary-content rounded-xl
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isExporting ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <><span className="ri-file-transfer-line text-lg" />{t('settings.exportDatabase')}</>
            )}
          </button>
        </div>

        {/* Danger Zone — Reset Database */}
        <div className="mt-8 pt-6 border-t-2 border-red-300 dark:border-red-700/50">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-red-100 dark:bg-red-800/30 rounded-full p-2">
              <span className="ri-alert-line ri-20px text-red-600 dark:text-red-400" />
            </div>
            <div>
              <h4 className="font-semibold text-red-700 dark:text-red-400 text-sm">
                {t('settings.databaseTab.dangerZone') || 'Danger Zone'}
              </h4>
              <p className="text-xs text-base-content/50">
                {t('settings.databaseTab.resetDescription') || 'This will delete all data and reset to factory settings'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setShowResetConfirm(true)}
            disabled={isResetting}
            className="w-full py-3 bg-error hover:brightness-90 text-error-content rounded-xl
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isResetting ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>{t('settings.resetting') || 'Resetting...'}</span>
              </>
            ) : (
              <><span className="ri-database-2-line text-lg" />{t('settings.resetDatabase') || 'Reset Database'}</>
            )}
          </button>
        </div>
      </div>

      {/* Reset Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showResetConfirm}
        onClose={() => setShowResetConfirm(false)}
        onConfirm={handleResetDatabase}
        title={t('settings.resetConfirmTitle') || 'Reset Database?'}
        message={t('settings.resetConfirmMessage') || 'All data will be permanently deleted and the database will be reset to factory settings. This action cannot be undone.'}
        itemName={t('settings.resetConfirmItemName') || 'the database'}
        confirmLabel={t('settings.resetConfirmLabel') || 'Yes, Reset Everything'}
        variant="danger"
        description={t('settings.resetConfirmDescription') || 'All products, sales, employees, settings, and other data will be lost.'}
      />
    </div>
  );

  return (
    <PageLayout
      background="bg-linear-to-br from-base-200 via-primary/10 to-base-200"
      containerWidth="max-w-5xl"
      padding="py-10 md:py-16"
    >
      {/* Header */}
      <div
        className="text-center mb-10"
      >
        <div
          className="bg-white/10 backdrop-blur-sm rounded-full p-4 w-fit mx-auto mb-4"
        >
          <span className="ri-settings-3-line ri-48px md:w-14 md:h-14 text-primary/80" />
        </div>
        <h1
          className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-linear-to-r from-primary to-secondary"
        >
          {t('settings.title')}
        </h1>
      </div>

      {/* Settings Form */}
      <form
        onSubmit={handleSubmit}
      >
        {/* Persistent Error Banner — shows when there are inline validation errors */}
        {Object.keys(errors).length > 0 && (
          <div
            role="alert" className="alert alert-error mb-6 items-start"
          >
            <div className="bg-red-100 dark:bg-red-800/30 rounded-full p-1.5 flex-shrink-0 mt-0.5">
              <span className="ri-alert-line ri-16px text-red-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-red-700 dark:text-red-300 text-sm">
                {t('settings.errorBanner')}
              </p>
              <ul className="mt-1.5 space-y-1">
                {(Object.keys(errors) as (keyof FormErrors)[]).map((field) => (
                  <li key={field} className="text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
                    <span className="w-1 h-1 rounded-full bg-red-400 flex-shrink-0" />
                    <span className="font-medium">{fieldLabels[field] || field}:</span>
                    <span>{errors[field]}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Unified Tab View — in-content sidebar nav + panel (no tab header) */}
        <Card padding="xl" transitional className="md:p-8 mb-6 min-h-[320px]">
          <div className="settings__layout">
            <nav
              className="settings__nav"
              aria-label="Settings sections"
              role="tablist"
              data-tab-prefix="settings-tab"
              onKeyDown={onSettingsTabKeyDown}
            >
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                const hasError = errorTabs.has(tab.id);
                return (
                  <button
                    key={tab.id}
                    type="button"
                    role="tab"
                    id={`settings-tab-${tab.id}`}
                    aria-controls={`settings-panel-${tab.id}`}
                    aria-selected={isActive}
                    onClick={() => navigateToTab(tab.id)}
                    className={`settings__nav-item
                      ${isActive ? 'settings__nav-item--active' : ''}
                      ${hasError ? 'settings__nav-item--error' : ''}
                    `}
                  >
                    <Icon className="settings__nav-icon" />
                    <span className="settings__nav-label">{t('settings.tabs.' + tab.id)}</span>
                    {hasError && (
                      <span
                        className="settings__nav-badge settings__nav-badge--error"
                        title={t('settings.hasValidationErrors')}
                      />
                    )}
                    {isActive && hasUnsavedChanges && !hasError && (
                      <span
                        className="settings__nav-badge settings__nav-badge--unsaved"
                        title={t('settings.unsavedChanges')}
                      />
                    )}
                  </button>
                );
              })}
            </nav>
            <div
              className="settings__panel"
              key={activeTab}
              role="tabpanel"
              id={`settings-panel-${activeTab}`}
              aria-labelledby={`settings-tab-${activeTab}`}
            >
              {activeTab === 'general' && renderGeneralTab()}
              {activeTab === 'business' && renderBusinessTab()}
              {activeTab === 'dining' && renderDiningTab()}
              {activeTab === 'delivery' && renderDeliveryTab()}
              {activeTab === 'employees' && renderEmployeesTab()}
              {activeTab === 'profile' && renderProfileTab()}
              {activeTab === 'email' && renderEmailTab()}
              {activeTab === 'database' && renderDatabaseTab()}
              {activeTab === 'theme' && renderThemeTab()}
            </div>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <BackButton onClick={handleBackNavigation} disabled={isNavigating} />
          <button
            type="button"
            onClick={handleResetSettings}
            disabled={!hasUnsavedChanges || isSaving}
            className="px-4 py-3 bg-base-100 border border-base-300 text-base-content rounded-xl
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-40 disabled:cursor-not-allowed hover:bg-base-200"
            title={hasUnsavedChanges ? 'Revert unsaved changes' : 'No unsaved changes'}
          >
            <span className="ri-refresh-line text-lg" />
            <span className="hidden sm:inline">{t('common.reset') || 'Reset'}</span>
          </button>
          <button
            type="submit"
            disabled={isSaving || !hasUnsavedChanges}
            className="flex-1 py-3 bg-linear-to-r from-primary to-secondary text-white rounded-xl
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>{t('settings.saving')}</span>
              </>
            ) : (
              <><span className="ri-save-3-line text-lg" /> {t('settings.saveSettings')}</>
            )}
          </button>
        </div>
      </form>        {/* Success Toast */}
        {submitStatus === 'success' && isSuccess && (
          <div
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-success shadow-lg"
          >
            <span className="ri-check-line text-lg" />
            {t('settings.successMessage')}
          </div>
        )}

        {/* Error Toast — only for API/save errors, not for validation errors (shown inline) */}
        {submitStatus === 'error' && errorMessage && Object.keys(errors).length === 0 && (
          <div
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-error shadow-lg max-w-md"
          >
            <span className="ri-alert-line text-lg" />
            <span>{errorMessage}</span>
          </div>
        )}
      {/* Theme Preview Modal */}
      <ThemePreviewModal isOpen={showThemePreview} onClose={() => setShowThemePreview(false)} />
    </PageLayout>
  );
}

