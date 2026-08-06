import { describe, expect, it } from 'vitest';
import {
  areaPath,
  linePath,
  metric,
  seriesMax,
  seriesPoints,
  smoothLine,
  values,
} from './sparkline';

describe('metric', () => {
  it('reads revenue from revenue or total', () => {
    expect(metric('revenue', { revenue: 12.5 })).toBe(12.5);
    expect(metric('revenue', { total: 9.99 })).toBe(9.99);
    expect(metric('revenue', {})).toBe(0);
  });

  it('reads orders', () => {
    expect(metric('orders', { orders: 3 })).toBe(3);
    expect(metric('orders', {})).toBe(0);
  });

  it('computes aov with a division guard', () => {
    expect(metric('aov', { revenue: 100, orders: 4 })).toBe(25);
    expect(metric('aov', { revenue: 100, orders: 0 })).toBe(0);
    expect(metric('aov', { total: 80, orders: 2 })).toBe(40);
  });

  it('falls back to raw key access and null rows', () => {
    expect(metric('tax', { tax: 7.5 })).toBe(7.5);
    expect(metric('revenue', null)).toBe(0);
    expect(metric('revenue', undefined)).toBe(0);
  });
});

describe('values', () => {
  it('maps rows to a series', () => {
    const rows = [
      { revenue: 10, orders: 1 },
      { revenue: 20, orders: 2 },
    ];
    expect(values(rows, 'revenue')).toEqual([10, 20]);
    expect(values(rows, 'orders')).toEqual([1, 2]);
  });
});

describe('seriesMax', () => {
  it('floors at 1 so flat/zero series stay renderable', () => {
    expect(seriesMax([])).toBe(1);
    expect(seriesMax([0, 0, 0])).toBe(1);
    expect(seriesMax([3, 9, 5])).toBe(9);
  });
});

describe('seriesPoints', () => {
  it('returns [] for an empty series', () => {
    expect(seriesPoints([], 10)).toEqual([]);
  });

  it('spreads x evenly and maps y top-down across the viewBox', () => {
    // default 120×36, padY 2 → y∈[2,34]
    const pts = seriesPoints([0, 100], 100);
    expect(pts[0]).toEqual([0, 34]);
    expect(pts[1]).toEqual([120, 2]);
  });

  it('single point sits at x=0, mid range', () => {
    // one column → x stays 0; y maps 50% of max into the middle of the range
    expect(seriesPoints([50], 100)[0]).toEqual([0, 19]);
  });

  it('rounds to 2 decimals (no float drift)', () => {
    // 36 - 29.47 = 6.530000000000001 before the rounding pass
    const pts = seriesPoints([0, 120, 300, 90, 210, 150, 260], 300);
    expect(pts[6][1]).toBe(6.53);
  });

  it('honors custom width/height for percentage space', () => {
    const pts = seriesPoints([0, 100], 100, { width: 100, height: 100, padY: 2 });
    expect(pts[0]).toEqual([0, 98]);
    expect(pts[1]).toEqual([100, 2]);
  });

  it('guards max<=0 from direct callers (no NaN)', () => {
    // max is floored to 1 — values then exceed the scale, so coordinates stay
    // finite (never NaN) even if out of bounds; valid SVG either way.
    const pts = seriesPoints([10, 20], 0);
    expect(pts.every(([x, y]) => Number.isFinite(x) && Number.isFinite(y))).toBe(true);
  });
});

describe('smoothLine', () => {
  it('handles empty and single-point series', () => {
    expect(smoothLine([])).toBe('');
    expect(smoothLine([[60, 18]])).toBe('M 60,18');
  });

  it('builds cubic segments that pass through every data point', () => {
    const vals = [0, 120, 300, 90, 210, 150, 260];
    const pts = seriesPoints(vals, 300);
    const line = smoothLine(pts);

    expect(line.startsWith(`M ${pts[0][0]},${pts[0][1]}`)).toBe(true);

    const segEnds = [...line.matchAll(/C \S+ \S+ (\S+),(\S+)/g)].map((m) => `${m[1]},${m[2]}`);
    const expectedEnds = pts.slice(1).map((p) => `${p[0]},${p[1]}`);
    expect(segEnds.length).toBe(expectedEnds.length);
    expectedEnds.forEach((e) => expect(segEnds).toContain(e));

    expect(line).not.toMatch(/ L /); // fully smoothed
    expect(line).toMatch(/ C /);
  });
});

describe('linePath / areaPath', () => {
  const vals = [10, 40, 25, 60];

  it('linePath wraps points into a smooth line', () => {
    const line = linePath(vals, 60);
    expect(line.startsWith('M ')).toBe(true);
    expect(line).toMatch(/ C /);
  });

  it('areaPath closes the smoothed line to the baseline', () => {
    const area = areaPath(vals, 60);
    expect(area).toMatch(/ C /);
    expect(area).toMatch(/ L 120,36 L 0,36 Z$/);
  });

  it('areaPath uses the custom height for other viewBoxes', () => {
    const area = areaPath(vals, 60, { width: 100, height: 100 });
    expect(area).toMatch(/ L 100,100 L 0,100 Z$/);
  });

  it('areaPath returns "" for empty series', () => {
    expect(areaPath([], 60)).toBe('');
    expect(linePath([], 60)).toBe('');
  });
});
