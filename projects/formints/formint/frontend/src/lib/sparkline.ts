/**
 * Formint POS — shared sparkline path helpers (pure TS, framework-agnostic).
 *
 * Used by the Data & Analytics dashboard (KPI sparklines) and the Reports
 * page (Sales Summary sparkline + Daily Sales Trend chart). All functions are
 * pure — feed them plain series/rows, get back SVG path strings or points.
 *
 * The default geometry is the classic 120×36 viewBox with a 2-unit vertical
 * pad, matching the KPI sparkline cards. Pass `{ width, height, padY }` for
 * other spaces (e.g. a 0–100 percentage viewBox for full-width charts).
 */

export type Row = Record<string, unknown>;

export const SPARK_WIDTH = 120;
export const SPARK_HEIGHT = 36;
export const SPARK_PAD_Y = 2;

export interface SparkOptions {
  width?: number;
  height?: number;
  padY?: number;
}

/** Resolve a numeric metric from a daily row. `revenue` falls back to `total`
 *  (reports use `{ date, total, orders }`, the dashboard uses `{ revenue }`). */
export function metric(key: string, row: Row | null | undefined): number {
  if (!row) return 0;
  if (key === 'revenue') return Number(row.revenue ?? row.total ?? 0);
  if (key === 'orders') return Number(row.orders ?? 0);
  if (key === 'aov') {
    const orders = Number(row.orders ?? 0);
    return orders > 0 ? Number(row.revenue ?? row.total ?? 0) / orders : 0;
  }
  return Number(row[key] ?? 0);
}

/** Map rows → numeric values for a metric key. */
export function values(rows: Row[], key: string): number[] {
  return rows.map((r) => metric(key, r));
}

/** Floor-1 max so flat / all-zero series stay renderable. */
export function seriesMax(vals: number[]): number {
  return Math.max(...vals.map((v) => Number(v || 0)), 1);
}

/**
 * Normalize a numeric series into `[x, y]` points across the viewBox.
 *
 * x is spread evenly across the width; y maps `v ∈ [0, max]` to
 * `[height - padY, padY]` (top-down), with a `padY` floor so tiny values
 * render at the baseline instead of jittering. Values are rounded to 2
 * decimals to keep path strings compact (and to kill float drift like
 * `36 - 29.47 = 6.530000000000001`).
 */
export function seriesPoints(
  vals: number[],
  max: number,
  opts: SparkOptions = {},
): number[][] {
  if (!vals.length) return [];
  const { width = SPARK_WIDTH, height = SPARK_HEIGHT, padY = SPARK_PAD_Y } = opts;
  max = Math.max(max, 1); // guard direct callers (seriesMax already floors)
  const stepX = vals.length > 1 ? width / (vals.length - 1) : width;
  const inner = height - padY; // travel range; bottom padY units stay free
  return vals.map((v, i) => {
    const x = Math.round(i * stepX * 100) / 100;
    const y = Math.round((height - Math.max(padY, (Number(v) / max) * inner)) * 100) / 100;
    return [x, y];
  });
}

/**
 * Catmull-Rom → cubic-bezier smoothing (uniform tension 1/6). The curve
 * passes exactly through every data point; control points are derived from
 * neighboring points, with edge points clamped to themselves.
 *
 *   segment i→i+1: c1 = P[i] + (P[i+1] − P[i−1])/6
 *                  c2 = P[i+1] − (P[i+2] − P[i])/6
 */
export function smoothLine(pts: number[][]): string {
  if (!pts.length) return '';
  if (pts.length === 1) return `M ${pts[0][0]},${pts[0][1]}`;
  const n = pts.length;
  const d = [`M ${pts[0][0]},${pts[0][1]}`];
  for (let i = 0; i < n - 1; i++) {
    const prev = pts[Math.max(i - 1, 0)];
    const cur = pts[i];
    const next = pts[i + 1];
    const after = pts[Math.min(i + 2, n - 1)];
    const c1x = cur[0] + (next[0] - prev[0]) / 6;
    const c1y = cur[1] + (next[1] - prev[1]) / 6;
    const c2x = next[0] - (after[0] - cur[0]) / 6;
    const c2y = next[1] - (after[1] - cur[1]) / 6;
    d.push(
      `C ${c1x.toFixed(2)},${c1y.toFixed(2)} ${c2x.toFixed(2)},${c2y.toFixed(2)} ${next[0]},${next[1]}`,
    );
  }
  return d.join(' ');
}

/** Smooth line path for a raw series (normalizes internally). */
export function linePath(vals: number[], max: number, opts: SparkOptions = {}): string {
  return smoothLine(seriesPoints(vals, max, opts));
}

/** Smooth area path: the line closed down to the baseline and back. */
export function areaPath(vals: number[], max: number, opts: SparkOptions = {}): string {
  const pts = seriesPoints(vals, max, opts);
  if (!pts.length) return '';
  const { height = SPARK_HEIGHT } = opts;
  const lastX = pts[pts.length - 1][0];
  return `${smoothLine(pts)} L ${lastX},${height} L 0,${height} Z`;
}
