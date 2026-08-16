import { describe, expect, it } from 'vitest';
import { validAmount } from '../../app/pages/admin/CashRegister';

describe('CashRegister helpers', () => {
  it('accepts zero and finite non-negative amounts', () => {
    expect(validAmount('0')).toBe(true);
    expect(validAmount('125.50')).toBe(true);
  });

  it('rejects negative, empty, and non-finite amounts', () => {
    expect(validAmount('-1')).toBe(false);
    expect(validAmount('')).toBe(false);
    expect(validAmount('not-a-number')).toBe(false);
    expect(validAmount('Infinity')).toBe(false);
  });
});
