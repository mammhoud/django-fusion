import { createContext, useContext, useEffect, useState, useCallback, useMemo, ReactNode } from 'react';
import { invoke } from '@tauri-apps/api/core';

// ── Exchange rates (relative to USD = 1.0) ──
// Static snapshot for POS use; in production these would come from an API.
const STATIC_EXCHANGE_RATES: Record<string, number> = {
  USD: 1.0,
  EUR: 0.92,
  GBP: 0.79,
  JPY: 149.5,
  CAD: 1.36,
  AUD: 1.53,
  CHF: 0.88,
  CNY: 7.24,
  INR: 83.1,
  MXN: 17.1,
  BRL: 4.97,
  KRW: 1320.0,
  SEK: 10.45,
  NOK: 10.6,
  DKK: 6.86,
  NZD: 1.63,
  SGD: 1.34,
  HKD: 7.82,
  TRY: 30.2,
  ZAR: 18.7,
  RUB: 89.5,
  AED: 3.67,
  SAR: 3.75,
  QAR: 3.64,
  EGP: 30.9,
  MAD: 10.0,
  TND: 3.1,
  PLN: 4.02,
  CZK: 22.8,
  HUF: 355.0,
  ILS: 3.7,
  THB: 35.5,
  PHP: 56.0,
  MYR: 4.72,
  IDR: 15600.0,
  VND: 24500.0,
  BDT: 110.0,
  NGN: 890.0,
  KES: 155.0,
  ARS: 830.0,
  CLP: 940.0,
  COP: 3920.0,
  PEN: 3.75,
  UAH: 38.0,
};

export interface CurrencyContextType {
  /** The currency code (e.g. 'USD', 'EUR', 'AED') */
  currency: string;
  /** The currency symbol (e.g. '$', '€', 'د.إ') — falls back to code */
  currencySymbol: string;
  /**
   * Locale-aware price formatter using Intl.NumberFormat.
   * Respects locale for symbol placement, digit grouping, and decimal separator.
   * Example: formatPrice(1234.5) → "$1,234.50" (en-US) or "1 234,50 $" (fr-FR)
   */
  formatPrice: (amount: number) => string;
  /** Whether the currency is still loading from Settings */
  isLoading: boolean;
  /** Active locale (default 'en-US') */
  locale: string;

  // ── Formatting variants ──
  /** Compact notation: "$1.2K", "$4.5M" */
  formatCompact: (amount: number) => string;
  /** Accounting format: negative values in parentheses, e.g. "($5.00)" */
  formatAccounting: (amount: number) => string;
  /** No decimal places: "$1,235" */
  formatNoDecimals: (amount: number) => string;

  // ── Currency conversion ──
  /** Exchange rates relative to USD */
  exchangeRates: Record<string, number>;
  /** Convert an amount from one currency to another */
  convert: (amount: number, fromCurrency: string, toCurrency: string) => number;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

/** Map common currency codes to their symbols. Falls back to the code itself. */
const CURRENCY_SYMBOLS: Record<string, string> = {
  AED: 'د.إ', AFN: '؋', ALL: 'L', AMD: '֏', ANG: 'ƒ', AOA: 'Kz', ARS: '$',
  AUD: 'A$', AWG: 'ƒ', AZN: '₼', BAM: 'KM', BBD: '$', BDT: '৳', BGN: 'лв',
  BHD: '.د.ب', BIF: 'Fr', BMD: '$', BND: '$', BOB: 'Bs.', BRL: 'R$', BSD: '$',
  BTN: 'Nu.', BWP: 'P', BYN: 'Br', BZD: '$', CAD: 'C$', CDF: 'Fr', CHF: 'Fr',
  CLP: '$', CNY: '¥', COP: '$', CRC: '₡', CUP: '$', CVE: '$', CZK: 'Kč',
  DJF: 'Fr', DKK: 'kr', DOP: '$', DZD: 'د.ج', EGP: '£', ERN: 'Nfk', ETB: 'Br',
  EUR: '€', FJD: '$', FKP: '£', FOK: 'kr', GBP: '£', GEL: '₾', GGP: '£',
  GHS: '₵', GIP: '£', GMD: 'D', GNF: 'Fr', GTQ: 'Q', GYD: '$', HKD: 'HK$',
  HNL: 'L', HRK: 'kn', HUF: 'Ft', IDR: 'Rp', ILS: '₪', IMP: '£', INR: '₹',
  IQD: 'ع.د', IRR: '﷼', ISK: 'kr', JEP: '£', JMD: '$', JOD: 'د.ا', JPY: '¥',
  KES: 'Sh', KGS: 'с', KHR: '៛', KID: '$', KMF: 'Fr', KRW: '₩', KWD: 'د.ك',
  KYD: '$', KZT: '₸', LAK: '₭', LBP: 'ل.ل', LKR: 'Rs', LRD: '$', LSL: 'L',
  LYD: 'ل.د', MAD: 'د.م.', MDL: 'L', MGA: 'Ar', MKD: 'ден', MMK: 'K',
  MNT: '₮', MOP: 'P', MRU: 'UM', MUR: '₨', MVR: '.ރ', MWK: 'MK', MXN: '$',
  MYR: 'RM', MZN: 'MT', NAD: '$', NGN: '₦', NIO: 'C$', NOK: 'kr', NPR: '₨',
  NZD: 'NZ$', OMR: 'ر.ع.', PAB: 'B/.', PEN: 'S/.', PGK: 'K', PHP: '₱',
  PLN: 'zł', PYG: '₲', QAR: 'ر.ق', RON: 'lei', RSD: 'дин.',
  RUB: '₽', RWF: 'Fr', SAR: 'ر.س', SBD: '$', SCR: '₨', SDG: '£', SEK: 'kr',
  SGD: 'S$', SHP: '£', SLE: 'Le', SOS: 'Sh', SRD: '$', SSP: '£', STN: 'Db',
  SYP: '£S', SZL: 'L', THB: '฿', TJS: 'ЅМ', TMT: 'm', TND: 'د.ت', TOP: 'T$',
  TRY: '₺', TTD: '$', TVD: '$', TWD: 'NT$', TZS: 'Sh', UAH: '₴', UGX: 'Sh',
  USD: '$', UYU: '$', UZS: "so'm", VES: 'Bs.', VND: '₫', VUV: 'Vt', WST: 'T',
  XAF: 'Fr', XCD: '$', XDR: 'SDR', XOF: 'Fr', XPF: 'Fr', YER: '﷼', ZAR: 'R',
  ZMW: 'ZK', ZWL: '$',
};

function getCurrencySymbol(code: string): string {
  return CURRENCY_SYMBOLS[code.toUpperCase()] || code;
}

/**
 * Convert an amount between two currencies using the exchange rate map.
 * Rates are relative to USD. Falls back to 1:1 if either currency is unknown.
 */
function convertCurrency(
  amount: number,
  from: string,
  to: string,
  rates: Record<string, number>,
): number {
  const fromRate = rates[from.toUpperCase()] ?? 1;
  const toRate = rates[to.toUpperCase()] ?? 1;
  if (fromRate === 0 || toRate === 0) return amount;
  // Convert from → USD → to
  const usd = amount / fromRate;
  return usd * toRate;
}

/**
 * Safely create an Intl.NumberFormat — falls back to decimal formatting
 * if the currency code is invalid (prevents RangeError crashes).
 */
function safeCurrencyFormatter(
  locale: string,
  currencyCode: string,
  opts: Intl.NumberFormatOptions = {},
): Intl.NumberFormat {
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currencyCode,
      ...opts,
    });
  } catch {
    // Invalid currency code — fall back to decimal formatting
    return new Intl.NumberFormat(locale, {
      style: 'decimal',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      ...opts,
    });
  }
}

export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [currency, setCurrency] = useState('USD');
  const [isLoading, setIsLoading] = useState(true);
  const [locale] = useState(() => {
    try {
      const stored = localStorage.getItem('formint-locale');
      return stored || (typeof navigator !== 'undefined' ? navigator.language : null) || 'en-US';
    } catch {
      return 'en-US';
    }
  });

  // Load exchange rates — starts with static map, can be overridden from Settings
  const [exchangeRates, setExchangeRates] = useState<Record<string, number>>(STATIC_EXCHANGE_RATES);

  useEffect(() => {
    // Browser/deployed Cloud mode has no Tauri IPC bridge. Keep the static
    // USD defaults and finish loading cleanly; the native desktop shell will
    // still hydrate settings through invoke below.
    const isE2EAuthBypass =
      typeof window !== 'undefined' &&
      window.localStorage.getItem('formint-e2e-auth-bypass') === 'true';
    if (typeof window !== 'undefined' && !('__TAURI_INTERNALS__' in window) && isE2EAuthBypass) {
      setIsLoading(false);
      return;
    }

    invoke<{ currency?: string; exchange_rates?: Record<string, number> }>('get_settings')
      .then((settings) => {
        if (settings?.currency) {
          setCurrency(settings.currency);
        }
        if (settings?.exchange_rates && Object.keys(settings.exchange_rates).length > 0) {
          setExchangeRates(prev => ({ ...prev, ...settings.exchange_rates }));
        }
      })
      .catch((error) => {
        console.error('[CurrencyContext] Failed to load settings:', error);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const currencySymbol = getCurrencySymbol(currency);

  // ── Memoized Intl.NumberFormat instances ──
  const priceFormatter = useMemo(
    () => safeCurrencyFormatter(locale, currency, { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
    [locale, currency],
  );

  const compactFormatter = useMemo(
    () => safeCurrencyFormatter(locale, currency, { notation: 'compact', minimumFractionDigits: 1, maximumFractionDigits: 1 }),
    [locale, currency],
  );

  const noDecimalsFormatter = useMemo(
    () => safeCurrencyFormatter(locale, currency, { minimumFractionDigits: 0, maximumFractionDigits: 0 }),
    [locale, currency],
  );

  const formatPrice = useCallback(
    (amount: number) => priceFormatter.format(amount),
    [priceFormatter],
  );

  const formatCompact = useCallback(
    (amount: number) => compactFormatter.format(amount),
    [compactFormatter],
  );

  /** Accounting format: wraps negative values in parentheses. */
  const formatAccounting = useCallback(
    (amount: number) => {
      if (amount < 0) {
        return `(${priceFormatter.format(Math.abs(amount))})`;
      }
      return priceFormatter.format(amount);
    },
    [priceFormatter],
  );

  const formatNoDecimals = useCallback(
    (amount: number) => noDecimalsFormatter.format(amount),
    [noDecimalsFormatter],
  );

  const convert = useCallback(
    (amount: number, fromCurrency: string, toCurrency: string) =>
      convertCurrency(amount, fromCurrency, toCurrency, exchangeRates),
    [exchangeRates],
  );

  const value = useMemo<CurrencyContextType>(() => ({
    currency,
    currencySymbol,
    formatPrice,
    isLoading,
    locale,
    formatCompact,
    formatAccounting,
    formatNoDecimals,
    exchangeRates,
    convert,
  }), [currency, currencySymbol, formatPrice, isLoading, locale, formatCompact, formatAccounting, formatNoDecimals, exchangeRates, convert]);

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrency(): CurrencyContextType {
  const ctx = useContext(CurrencyContext);
  if (!ctx) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return ctx;
}
