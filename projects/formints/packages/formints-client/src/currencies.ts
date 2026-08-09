import type { FormintsClient } from './core.js';

export interface Currency {
  id: number;
  code: string;
  name: string;
  symbol: string;
  exchange_rate: string;
  is_default: boolean;
  is_active: boolean;
}

export interface CurrencyInput {
  code: string;
  name: string;
  symbol?: string;
  exchange_rate?: string;
  is_default?: boolean;
}

export async function listCurrencies(client: FormintsClient): Promise<{ count: number; items: Currency[] }> {
  return client.request('/api/v1/currencies');
}

export async function createCurrency(client: FormintsClient, input: CurrencyInput): Promise<Currency> {
  return client.request('/api/v1/currencies', { method: 'POST', body: JSON.stringify(input) });
}
