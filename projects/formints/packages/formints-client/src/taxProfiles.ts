import type { FormintsClient } from './core';

export interface TaxProfile {
  id: number;
  name: string;
  rate: string;
  is_default: boolean;
  is_active: boolean;
}

export async function listTaxProfiles(client: FormintsClient): Promise<{ count: number; items: TaxProfile[] }> {
  return client.request('/api/v1/tax-profiles');
}
