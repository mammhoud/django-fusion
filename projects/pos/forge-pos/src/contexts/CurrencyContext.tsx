import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';
import { invoke } from '@tauri-apps/api/core';

interface CurrencyContextType {
  /** The currency code (e.g. 'USD', 'EUR', 'AED') */
  currency: string;
  /** The currency symbol (e.g. '$', '€', 'د.إ') — defaults to code if no matching symbol */
  currencySymbol: string;
  /** Format a numeric amount with the currency symbol (e.g. "$ 12.50") */
  formatPrice: (amount: number) => string;
  /** Whether the currency is still loading from Settings */
  isLoading: boolean;
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

/** Map common currency codes to their symbols. Falls back to the code itself. */
const CURRENCY_SYMBOLS: Record<string, string> = {
  AED: 'د.إ',
  AFN: '؋',
  ALL: 'L',
  AMD: '֏',
  ANG: 'ƒ',
  AOA: 'Kz',
  ARS: '$',
  AUD: 'A$',
  AWG: 'ƒ',
  AZN: '₼',
  BAM: 'KM',
  BBD: '$',
  BDT: '৳',
  BGN: 'лв',
  BHD: '.د.ب',
  BIF: 'Fr',
  BMD: '$',
  BND: '$',
  BOB: 'Bs.',
  BRL: 'R$',
  BSD: '$',
  BTN: 'Nu.',
  BWP: 'P',
  BYN: 'Br',
  BZD: '$',
  CAD: 'C$',
  CDF: 'Fr',
  CHF: 'Fr',
  CLP: '$',
  CNY: '¥',
  COP: '$',
  CRC: '₡',
  CUP: '$',
  CVE: '$',
  CZK: 'Kč',
  DJF: 'Fr',
  DKK: 'kr',
  DOP: '$',
  DZD: 'د.ج',
  EGP: '£',
  ERN: 'Nfk',
  ETB: 'Br',
  EUR: '€',
  FJD: '$',
  FKP: '£',
  FOK: 'kr',
  GBP: '£',
  GEL: '₾',
  GGP: '£',
  GHS: '₵',
  GIP: '£',
  GMD: 'D',
  GNF: 'Fr',
  GTQ: 'Q',
  GYD: '$',
  HKD: 'HK$',
  HNL: 'L',
  HRK: 'kn',
  HUF: 'Ft',
  IDR: 'Rp',
  ILS: '₪',
  IMP: '£',
  INR: '₹',
  IQD: 'ع.د',
  IRR: '﷼',
  ISK: 'kr',
  JEP: '£',
  JMD: '$',
  JOD: 'د.ا',
  JPY: '¥',
  KES: 'Sh',
  KGS: 'с',
  KHR: '៛',
  KID: '$',
  KMF: 'Fr',
  KRW: '₩',
  KWD: 'د.ك',
  KYD: '$',
  KZT: '₸',
  LAK: '₭',
  LBP: 'ل.ل',
  LKR: 'Rs',
  LRD: '$',
  LSL: 'L',
  LYD: 'ل.د',
  MAD: 'د.م.',
  MDL: 'L',
  MGA: 'Ar',
  MKD: 'ден',
  MMK: 'K',
  MNT: '₮',
  MOP: 'P',
  MRU: 'UM',
  MUR: '₨',
  MVR: '.ރ',
  MWK: 'MK',
  MXN: '$',
  MYR: 'RM',
  MZN: 'MT',
  NAD: '$',
  NGN: '₦',
  NIO: 'C$',
  NOK: 'kr',
  NPR: '₨',
  NZD: 'NZ$',
  OMR: 'ر.ع.',
  PAB: 'B/.',
  PEN: 'S/.',
  PGK: 'K',
  PHP: '₱',
  PKR: '₨',
  PLN: 'zł',
  PYG: '₲',
  QAR: 'ر.ق',
  RON: 'lei',
  RSD: 'дин.',
  RUB: '₽',
  RWF: 'Fr',
  SAR: 'ر.س',
  SBD: '$',
  SCR: '₨',
  SDG: '£',
  SEK: 'kr',
  SGD: 'S$',
  SHP: '£',
  SLE: 'Le',
  SOS: 'Sh',
  SRD: '$',
  SSP: '£',
  STN: 'Db',
  SYP: '£S',
  SZL: 'L',
  THB: '฿',
  TJS: 'ЅМ',
  TMT: 'm',
  TND: 'د.ت',
  TOP: 'T$',
  TRY: '₺',
  TTD: '$',
  TVD: '$',
  TWD: 'NT$',
  TZS: 'Sh',
  UAH: '₴',
  UGX: 'Sh',
  USD: '$',
  UYU: '$',
  UZS: "so'm",
  VES: 'Bs.',
  VND: '₫',
  VUV: 'Vt',
  WST: 'T',
  XAF: 'Fr',
  XCD: '$',
  XDR: 'SDR',
  XOF: 'Fr',
  XPF: 'Fr',
  YER: '﷼',
  ZAR: 'R',
  ZMW: 'ZK',
  ZWL: '$',
};

function getCurrencySymbol(code: string): string {
  return CURRENCY_SYMBOLS[code.toUpperCase()] || code;
}

export function CurrencyProvider({ children }: { children: ReactNode }) {
  const [currency, setCurrency] = useState('USD');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    invoke<{ currency?: string }>('get_settings')
      .then((settings) => {
        if (settings?.currency) {
          setCurrency(settings.currency);
        }
      })
      .catch((error) => {
        console.error('[CurrencyContext] Failed to load settings:', error);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const currencySymbol = getCurrencySymbol(currency);

  const formatPrice = useCallback(
    (amount: number) => `${currencySymbol} ${amount.toFixed(2)}`,
    [currencySymbol]
  );

  return (
    <CurrencyContext.Provider value={{ currency, currencySymbol, formatPrice, isLoading }}>
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
