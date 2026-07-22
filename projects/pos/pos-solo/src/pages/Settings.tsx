import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FaCog, FaSave, FaCheck, FaFileImport, FaFileExport, FaChevronDown,
  FaExclamationTriangle, FaGlobe, FaBriefcase, FaUtensils, FaTruck,
  FaUsers, FaDatabase, FaLock, FaClock
} from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { isTauri } from '../utils/tauri';
import { open, save } from '@tauri-apps/plugin-dialog';
import { readFile, writeFile } from '@tauri-apps/plugin-fs';
import { useGetSettingsQuery, useUpdateSettingsMutation } from '../store/api/endpoints/core';
import { useGetEmployeesQuery } from '../store/api/endpoints/core';
import type { Settings as SettingsType } from '../types';
import BackButton from '../components/BackButton';
import PageLayout from '../components/PageLayout';
import LanguageToggle from '../components/LanguageToggle';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';

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

type TabId = 'general' | 'business' | 'dining' | 'delivery' | 'employees' | 'database';

interface TabDefinition {
  id: TabId;
  label: string;
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

const tabs: TabDefinition[] = [
  { id: 'general', label: 'General', icon: FaGlobe },
  { id: 'business', label: 'Business', icon: FaBriefcase },
  { id: 'dining', label: 'Dining', icon: FaUtensils },
  { id: 'delivery', label: 'Delivery', icon: FaTruck },
  { id: 'employees', label: 'Employees', icon: FaUsers },
  { id: 'database', label: 'Database', icon: FaDatabase },
];

const tabVariants = {
  enter: { opacity: 0, x: 20 },
  center: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

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
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2 rounded-lg bg-white/50 dark:bg-white/5 border 
          border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white 
          cursor-pointer hover:border-teal-400 transition-all duration-200 flex items-center justify-between"
      >
        <span>
          {selectedCurrency ? (
            `${selectedCurrency.name} (${selectedCurrency.code} ${selectedCurrency.symbol})`
          ) : t('settings.selectCurrency')}
        </span>
        <FaChevronDown className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </div>
      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white dark:bg-slate-800 border border-slate-300 dark:border-gray-600 rounded-lg shadow-xl">
          <div className="p-2">
            <input
              type="text"
              placeholder={t('settings.searchCurrency')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 
                rounded-md text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-gray-400
                focus:outline-none focus:border-teal-400 transition-colors"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
          <div className="max-h-60 overflow-y-auto u-scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent">
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
                    ? 'bg-teal-500/20 text-teal-600 dark:text-teal-400' 
                    : 'text-slate-900 dark:text-white hover:bg-slate-100 dark:hover:bg-white/5'}
                  transition-colors duration-200`}
              >
                <span>{currency.name}</span>
                <span className="text-slate-500 dark:text-gray-400">
                  {currency.code} {currency.symbol}
                </span>
              </div>
            ))}
            {filteredOptions.length === 0 && (
              <div className="px-4 py-2 text-slate-500 dark:text-gray-400 text-center">
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
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabId>('general');
  const [settings, setSettings] = useState<SettingsType>({
    restaurant_name: 'POS',
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
    delivery_fee_per_km: 0
  });

  // ── RTK Query hooks ──
  const { data: settingsRes } = useGetSettingsQuery();
  const [updateSettings] = useUpdateSettingsMutation();
  const { data: employeesRes = [] } = useGetEmployeesQuery();

  const [isSuccess, setIsSuccess] = useState(false);
  const [logoPreview, setLogoPreview] = useState<string | undefined>(undefined);
  const [isNavigating, setIsNavigating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [employeeCount, setEmployeeCount] = useState(0);
  const [activeEmployeeCount, setActiveEmployeeCount] = useState(0);

  // Sync RTK data into local state
  useEffect(() => {
    if (settingsRes) {
      setSettings(prev => ({ ...prev, ...settingsRes as unknown as Partial<SettingsType> }));
      const s = settingsRes as any;
      if (s?.logo) setLogoPreview(s.logo);
    }
  }, [settingsRes]);

  useEffect(() => {
    setEmployeeCount(employeesRes.length);
    setActiveEmployeeCount(employeesRes.filter((e: any) => e.is_active).length);
  }, [employeesRes]);

  // Password change state
  const { user, isAuthRequired, inactivityTimeout, setInactivityTimeout } = useAuth();
  const [passwordOld, setPasswordOld] = useState('');
  const [passwordNew, setPasswordNew] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState(false);
  const [passwordChangeError, setPasswordChangeError] = useState('');

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

  const handleBackNavigation = () => {
    setIsNavigating(true);
    setTimeout(() => {
      navigate('/');
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
        setLogoPreview(dataUrl);
        setSettings(prev => ({ ...prev, logo: dataUrl }));
      }
    } catch (error) {
      console.error('Error selecting logo:', error);
    } finally {
      setIsUploadingLogo(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { valid, errors: newErrors } = validateForm();
    if (!valid) {
      const errFields = Object.keys(newErrors) as (keyof FormErrors)[];
      const tabsWithErrors: TabId[] = [];
      for (const field of errFields) {
        const tab = fieldToTab[field];
        if (tab && !tabsWithErrors.includes(tab)) {
          tabsWithErrors.push(tab);
        }
      }
      if (tabsWithErrors.length > 0) {
        setActiveTab(tabsWithErrors[0]);
      }
      return;
    }
    setIsSaving(true);
    setSubmitStatus('idle');
    setErrorMessage('');
    try {
      await updateSettings(settings as any).unwrap();
      setSubmitStatus('success');
      setIsSuccess(true);
      setErrors({});
      setTimeout(() => { setIsSuccess(false); setSubmitStatus('idle'); }, 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
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
        if (isTauri) {
          const { invoke } = await import('@tauri-apps/api/core');
          await invoke('import_database_cmd', { data: base64 });
        } else {
          console.warn('import_database_cmd is only available in Tauri desktop mode');
        }
        setIsSuccess(true);
        setTimeout(() => setIsSuccess(false), 3000);
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
      if (isTauri) {
        const { invoke } = await import('@tauri-apps/api/core');
        await invoke('change_password_cmd', {
          email: user.email,
          oldPassword: passwordOld,
          newPassword: passwordNew,
        });
      } else {
        throw new Error('Password change requires Tauri desktop mode');
      }
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

  const handleExportDatabase = async () => {
    setIsExporting(true);
    try {
      let base64Data: string;
      if (isTauri) {
        const { invoke } = await import('@tauri-apps/api/core');
        base64Data = await invoke<string>('export_database_cmd');
      } else {
        throw new Error('Database export requires Tauri desktop mode');
      }
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

  // ---- Shared Input Classes ----
  const inputClass = (fieldName?: keyof FormErrors) =>
    `w-full px-4 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border 
    text-slate-900 dark:text-white focus:outline-none transition-all duration-200
    ${fieldName && errors[fieldName]
      ? 'border-red-500 focus:border-red-500 ring-1 ring-red-500/30'
      : 'border-slate-300 dark:border-gray-600 focus:border-teal-400 focus:ring-1 focus:ring-teal-400/30'}
    placeholder:text-slate-400 dark:placeholder:text-gray-500`;

  const labelClass = 'block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5';
  const errorClass = 'mt-1 text-sm text-red-400 flex items-center gap-1.5';

  // ---- Tab Content ----
  const renderGeneralTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Logo */}
      <div className="md:col-span-2">
        <label className={labelClass}>{t('settings.restaurantLogo')}</label>
        <div className="flex items-center gap-6">
          {logoPreview && (
            <div className="relative w-24 h-24 shrink-0">
              <img src={logoPreview} alt={t('settings.logoPreviewAlt')} className="rounded-lg object-contain w-full h-full bg-white/20" />
              <button
                type="button"
                onClick={() => { setLogoPreview(undefined); setSettings(prev => ({ ...prev, logo: undefined })); }}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors shadow-lg"
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
            className="flex flex-col items-center justify-center px-6 py-5 bg-white/30 dark:bg-white/5 
              text-slate-600 dark:text-gray-300 rounded-lg border-2 border-slate-300 dark:border-gray-600 
              border-dashed cursor-pointer hover:border-teal-400 hover:bg-teal-500/5 transition-all 
              disabled:opacity-50 disabled:cursor-not-allowed flex-1"
          >
            {isUploadingLogo ? (
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-8 h-8 border-2 border-teal-400 border-t-transparent rounded-full"
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
        <p className="mt-2 text-xs text-slate-500 dark:text-gray-400">{t('settings.generalTab.logoFormats')}</p>
      </div>

      {/* Restaurant Name */}
      <div>
        <label className={labelClass}>{t('settings.restaurantName')} <span className="text-red-400">*</span></label>
        <input type="text" name="restaurant_name" value={settings.restaurant_name} onChange={handleChange}
          className={inputClass('restaurant_name')} />
        {errors.restaurant_name && <p className={errorClass}><FaExclamationTriangle className="text-xs" />{errors.restaurant_name}</p>}
      </div>

      {/* Language */}
      <div>
        <label className={labelClass}>{t('settings.generalTab.languageLabel')}</label>
        <div className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600">
          <span className="text-sm text-slate-900 dark:text-white flex-1">
            {i18n.language === 'ar' ? t('settings.generalTab.languageValueAr') : i18n.language === 'fr' ? t('settings.generalTab.languageValueFr') : t('settings.generalTab.languageValueEn')}
          </span>
          <LanguageToggle />
        </div>
        <p className="mt-1.5 text-xs text-slate-500 dark:text-gray-400">
          {t('settings.generalTab.languageDesc')}
        </p>
      </div>

      {/* Inactivity Timeout — only when authenticated */}
      {isAuthRequired && user && (
        <div className="md:col-span-2">
          <div className="border-t border-slate-300/50 dark:border-gray-600/50 pt-6 mt-2">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">
              <FaClock className="inline mr-2 text-teal-400" />
              {t('settings.inactivityTimeout')}
            </h3>
            <p className="text-sm text-slate-500 dark:text-gray-400 mb-4">
              {t('settings.inactivityTimeoutDesc')}
            </p>
            <div className="max-w-xs">
              <select
                value={inactivityTimeout}
                onChange={(e) => setInactivityTimeout(e.target.value)}
                className={inputClass()}
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

      {/* Password Change — only when authenticated */}
      {isAuthRequired && user && (
        <div className="md:col-span-2">
          <div className="border-t border-slate-300/50 dark:border-gray-600/50 pt-6 mt-2">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">
              <FaLock className="inline mr-2 text-teal-400" />
              {t('settings.changePassword')}
            </h3>
            <p className="text-sm text-slate-500 dark:text-gray-400 mb-4">
              {t('settings.changePasswordDesc')} <strong>{user.email}</strong>
            </p>

            {passwordChangeSuccess && (
              <div className="mb-4 bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-700/40 rounded-xl p-3 flex items-center gap-2">
                <FaCheck className="w-4 h-4 text-teal-500" />
                <span className="text-sm text-teal-700 dark:text-teal-300">{t('settings.passwordChangeSuccess')}</span>
              </div>
            )}

            {passwordChangeError && (
              <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/40 rounded-xl p-3 flex items-center gap-2">
                <FaExclamationTriangle className="w-4 h-4 text-red-500" />
                <span className="text-sm text-red-700 dark:text-red-300">{passwordChangeError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className={labelClass}>{t('settings.currentPassword')}</label>
                <input
                  type="password"
                  value={passwordOld}
                  onChange={(e) => { setPasswordOld(e.target.value); setPasswordChangeSuccess(false); setPasswordChangeError(''); }}
                  placeholder="••••••••"
                  className={inputClass()}
                />
              </div>
              <div>
                <label className={labelClass}>{t('settings.newPassword')}</label>
                <input
                  type="password"
                  value={passwordNew}
                  onChange={(e) => { setPasswordNew(e.target.value); setPasswordChangeSuccess(false); setPasswordChangeError(''); }}
                  placeholder="••••••••"
                  className={inputClass()}
                />
              </div>
              <div className="flex items-end">
                <motion.button
                  type="button"
                  onClick={handlePasswordChange}
                  disabled={isChangingPassword || !passwordOld || !passwordNew}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-2.5 bg-teal-500 hover:bg-teal-600 text-white rounded-lg 
                    font-medium transition-all duration-200 flex items-center justify-center gap-2
                    disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isChangingPassword ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <><FaLock className="text-sm" /> {t('settings.updatePassword')}</>
                  )}
                </motion.button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Phone */}
      <div>
        <label className={labelClass}>{t('settings.phone')}</label>
        <input type="tel" name="phone" value={settings.phone} onChange={handleChange} className={inputClass('phone')} />
        {errors.phone && <p className={errorClass}><FaExclamationTriangle className="text-xs" />{errors.phone}</p>}
      </div>

      {/* Email */}
      <div>
        <label className={labelClass}>{t('settings.email')}</label>
        <input type="email" name="email" value={settings.email} onChange={handleChange} className={inputClass('email')} />
        {errors.email && <p className={errorClass}><FaExclamationTriangle className="text-xs" />{errors.email}</p>}
      </div>

      {/* Address */}
      <div>
        <label className={labelClass}>{t('settings.address')}</label>
        <textarea name="address" value={settings.address} onChange={handleChange} rows={3} className={inputClass()} />
      </div>
    </div>
  );

  const renderBusinessTab = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Tax Rate */}
      <div>
        <label className={labelClass}>{t('settings.taxRate')}</label>
        <input type="number" name="tax_rate" value={settings.tax_rate} onChange={handleChange}
          step="0.01" min="0" max="100" className={inputClass('tax_rate')} />
        {errors.tax_rate && <p className={errorClass}><FaExclamationTriangle className="text-xs" />{errors.tax_rate}</p>}
      </div>

      {/* Currency */}
      <div>
        <label className={labelClass}>{t('settings.currency')}</label>
        <CurrencyDropdown value={settings.currency || 'USD'} onChange={(v) => setSettings(prev => ({ ...prev, currency: v }))} />
      </div>

      {/* Opening Time */}
      <div>
        <label className={labelClass}>{t('settings.openingTime')}</label>
        <input type="time" name="opening_time" value={settings.opening_time} onChange={handleChange} className={inputClass('opening_time')} />
        {errors.opening_time && <p className={errorClass}><FaExclamationTriangle className="text-xs" />{errors.opening_time}</p>}
      </div>

      {/* Closing Time */}
      <div>
        <label className={labelClass}>{t('settings.closingTime')}</label>
        <input type="time" name="closing_time" value={settings.closing_time} onChange={handleChange} className={inputClass('closing_time')} />
        {errors.closing_time && <p className={errorClass}><FaExclamationTriangle className="text-xs" />{errors.closing_time}</p>}
      </div>

      {/* Receipt Footer */}
      <div className="md:col-span-2">
        <label className={labelClass}>{t('settings.receiptFooter')}</label>
        <textarea name="receipt_footer" value={settings.receipt_footer} onChange={handleChange}
          rows={3} className={inputClass()}
          placeholder={t('settings.receiptFooterPlaceholder')} />
      </div>
    </div>
  );

  const renderDiningTab = () => (
    <div className="max-w-lg mx-auto">
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl p-6 mb-8 border border-amber-200 dark:border-amber-700/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-amber-100 dark:bg-amber-800/30 rounded-full p-2.5">
            <FaUtensils className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">{t('settings.diningTab.title')}</h3>
            <p className="text-sm text-slate-500 dark:text-gray-400">{t('settings.diningTab.description')}</p>
          </div>
        </div>
        <div>
          <label className={labelClass}>{t('settings.numberOfTables')}</label>
          <input type="number" name="dine_in_tables" value={settings.dine_in_tables ?? 0}
            onChange={handleChange} min="0"
            className={inputClass()} />
          <p className="mt-1.5 text-xs text-slate-500 dark:text-gray-400">
            {t('settings.diningTab.zeroToDisable')}
          </p>
        </div>
      </div>
    </div>
  );

  const renderDeliveryTab = () => (
    <div className="max-w-lg mx-auto">
      <div className="bg-gradient-to-br from-sky-50 to-blue-50 dark:from-sky-900/20 dark:to-blue-900/20 rounded-xl p-6 mb-8 border border-sky-200 dark:border-sky-700/30">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-sky-100 dark:bg-sky-800/30 rounded-full p-2.5">
            <FaTruck className="w-5 h-5 text-sky-600 dark:text-sky-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">{t('settings.deliveryTab.title')}</h3>
            <p className="text-sm text-slate-500 dark:text-gray-400">{t('settings.deliveryTab.description')}</p>
          </div>
        </div>
        <div className="space-y-6">
          <div>
            <label className={labelClass}>{t('settings.deliveryFeeFlat', { currency: settings.currency || 'USD' })}</label>
            <input type="number" name="delivery_fee" value={settings.delivery_fee ?? 0}
              onChange={handleChange} min="0" step="0.5" className={inputClass()} />
          </div>
          <div>
            <label className={labelClass}>{t('settings.deliveryFeePerKm', { currency: settings.currency || 'USD' })}</label>
            <input type="number" name="delivery_fee_per_km" value={settings.delivery_fee_per_km ?? 0}
              onChange={handleChange} min="0" step="0.1" className={inputClass()} />
            <p className="mt-1.5 text-xs text-slate-500 dark:text-gray-400">
              {t('settings.deliveryTab.perKmDescription')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderEmployeesTab = () => (
    <div className="max-w-2xl mx-auto">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        <div className="bg-white/40 dark:bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-slate-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-100 dark:bg-indigo-800/30 rounded-full p-2.5">
              <FaUsers className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{employeeCount}</p>
              <p className="text-xs text-slate-500 dark:text-gray-400">{t('settings.employeesTab.totalEmployees')}</p>
            </div>
          </div>
        </div>
        <div className="bg-white/40 dark:bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-slate-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-100 dark:bg-emerald-800/30 rounded-full p-2.5">
              <FaCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{activeEmployeeCount}</p>
              <p className="text-xs text-slate-500 dark:text-gray-400">{t('settings.employeesTab.activeEmployees')}</p>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-white/40 dark:bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-slate-200 dark:border-gray-700">
        <h3 className="font-semibold text-slate-900 dark:text-white mb-3">{t('settings.employeesTab.managementTitle')}</h3>
        <p className="text-sm text-slate-600 dark:text-gray-400 mb-4">
          {t('settings.employeesTab.managementDesc')}
        </p>
        <button
          type="button"
          onClick={() => navigate('/employees')}
          className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 
            text-white rounded-lg text-sm font-medium transition-colors"
        >
          <FaUsers className="w-4 h-4" />
          {t('settings.employeesTab.goToEmployees')}
        </button>
      </div>
    </div>
  );

  const renderDatabaseTab = () => (
    <div className="max-w-lg mx-auto">
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 mb-8 border border-purple-200 dark:border-purple-700/30">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-purple-100 dark:bg-purple-800/30 rounded-full p-2.5">
            <FaDatabase className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">{t('settings.databaseTab.title')}</h3>
            <p className="text-sm text-slate-500 dark:text-gray-400">{t('settings.databaseTab.description')}</p>
          </div>
        </div>

        {/* Database Info Card */}
        <div className="bg-white/50 dark:bg-white/5 rounded-lg p-4 mb-6 border border-slate-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-600 dark:text-gray-400">{t('settings.databaseTab.status')}</span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium
              bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              {t('settings.databaseTab.connected')}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600 dark:text-gray-400">{t('settings.databaseTab.type')}</span>
            <span className="text-sm font-medium text-slate-900 dark:text-white">{t('settings.databaseTab.sqlite')}</span>
          </div>
        </div>

        {/* Import / Export */}
        <div className="space-y-3">
          <button
            type="button"
            onClick={handleImportDatabase}
            disabled={isImporting}
            className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-xl 
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isImporting ? (
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <><FaFileImport className="text-lg" />{t('settings.importDatabase')}</>
            )}
          </button>
          <button
            type="button"
            onClick={handleExportDatabase}
            disabled={isExporting}
            className="w-full py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-xl 
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isExporting ? (
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <><FaFileExport className="text-lg" />{t('settings.exportDatabase')}</>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <PageLayout
      background="bg-linear-to-br from-slate-100 via-purple-100 to-slate-100 dark:from-slate-900 dark:via-purple-900 dark:to-slate-900"
      containerWidth="max-w-5xl"
      padding="py-10 md:py-16"
    >
      {/* Header */}
      <motion.div
        className="text-center mb-10"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          className="bg-white/10 backdrop-blur-sm rounded-full p-4 w-fit mx-auto mb-4"
        >
          <FaCog className="w-12 h-12 md:w-14 md:h-14 text-teal-400" />
        </motion.div>
        <motion.h1
          className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-linear-to-r from-teal-400 to-purple-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          {t('settings.title')}
        </motion.h1>
      </motion.div>

      {/* Tab Navigation */}
      <motion.div
        className="bg-white/60 dark:bg-white/10 backdrop-blur-md rounded-2xl p-1.5 mb-6 border border-slate-200/50 dark:border-gray-700/50"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex overflow-x-auto scrollbar-none gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const hasError = errorTabs.has(tab.id);
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`relative flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium 
                  whitespace-nowrap transition-all duration-200 shrink-0 justify-center
                  ${isActive
                    ? 'bg-white dark:bg-white/10 text-teal-600 dark:text-teal-400 shadow-sm'
                    : 'text-slate-500 dark:text-gray-400 hover:text-slate-700 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-white/5'
                  }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-teal-500' : ''} ${hasError ? 'text-red-400' : ''}`} />                  <span>{t('settings.tabs.' + tab.id)}</span>
                {hasError && (
                  <span className="w-2 h-2 rounded-full bg-red-400 flex-shrink-0" title={t('settings.hasValidationErrors')} />
                )}
                {isActive && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 rounded-xl bg-white dark:bg-white/10 -z-10"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Settings Form */}
      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {/* Persistent Error Banner — shows when there are inline validation errors */}
        {Object.keys(errors).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/40 
              rounded-xl p-4 flex items-start gap-3"
          >
            <div className="bg-red-100 dark:bg-red-800/30 rounded-full p-1.5 flex-shrink-0 mt-0.5">
              <FaExclamationTriangle className="w-4 h-4 text-red-500" />
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
          </motion.div>
        )}

        {/* Tab Content */}
        <div className="card--glass rounded-2xl p-6 md:p-8 mb-6 transition-colors duration-300 min-h-[320px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              variants={tabVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.2 }}
            >
              {activeTab === 'general' && renderGeneralTab()}
              {activeTab === 'business' && renderBusinessTab()}
              {activeTab === 'dining' && renderDiningTab()}
              {activeTab === 'delivery' && renderDeliveryTab()}
              {activeTab === 'employees' && renderEmployeesTab()}
              {activeTab === 'database' && renderDatabaseTab()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <BackButton onClick={handleBackNavigation} disabled={isNavigating} />
          <motion.button
            type="submit"
            whileHover={{ scale: isSaving ? 1 : 1.02 }}
            whileTap={{ scale: isSaving ? 1 : 0.98 }}
            disabled={isSaving}
            className="flex-1 py-3 bg-linear-to-r from-teal-400 to-purple-400 text-white rounded-xl 
              font-medium transition-all duration-200 flex items-center justify-center gap-2
              disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
                <span>{t('settings.saving')}</span>
              </>
            ) : (
              <><FaSave className="text-lg" /> {t('settings.saveSettings')}</>
            )}
          </motion.button>
        </div>
      </motion.form>        {/* Success Toast */}
        {submitStatus === 'success' && isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-teal-500 text-white px-6 py-3 
              rounded-xl flex items-center gap-2 shadow-lg z-50"
          >
            <FaCheck className="text-lg" />
            {t('settings.successMessage')}
          </motion.div>
        )}

        {/* Error Toast — only for API/save errors, not for validation errors (shown inline) */}
        {submitStatus === 'error' && errorMessage && Object.keys(errors).length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-red-500 text-white px-6 py-3 
              rounded-xl flex items-center gap-2 shadow-lg z-50 max-w-md"
          >
            <FaExclamationTriangle className="text-lg" />
            <span>{errorMessage}</span>
          </motion.div>
        )}
    </PageLayout>
  );
}
