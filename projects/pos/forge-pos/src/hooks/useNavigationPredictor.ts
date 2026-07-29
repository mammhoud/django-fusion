/**
 * Navigation Predictor
 * ====================
 * Learns common navigation patterns and preloads the most-likely next page chunk
 * so the user never waits for a lazy-loaded page to fetch.
 *
 * The hook tracks the user's navigation history, identifies frequent transitions
 * (e.g., Home → Sale → Kitchen → Transactions), and predicts the next page
 * whenever the current route matches a known pattern.
 *
 * Usage:
 *   import { useNavigationPredictor } from '../hooks/useNavigationPredictor';
 *   useNavigationPredictor(currentRoute);
 *
 * The hook runs silently — errors are swallowed (preloading is a best-effort
 * optimization). Learned patterns persist across sessions via localStorage.
 */

import { useEffect, useRef } from 'react';
import { preloadRoute } from '../utils/preloadRoutes';

// ── Constants ──

/** Max nav history depth kept for pattern learning. */
const HISTORY_SIZE = 15;

/** How many repeats before a transition is considered "learned". */
const CONFIRM_THRESHOLD = 2;

/** localStorage key for persisted patterns + history. */
const STORAGE_KEY = 'forge-pos-nav-predictor';

// ── Types ──

interface NavRecord {
  /** Ordered list of recent route paths, most recent last. */
  history: string[];
  /** Map of "from→to" → count of times this transition was observed. */
  transitions: Record<string, number>;
}

// ── Storage helpers ──

function loadRecord(): NavRecord {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as NavRecord;
      return {
        history: Array.isArray(parsed.history) ? parsed.history : [],
        transitions: parsed.transitions && typeof parsed.transitions === 'object' ? parsed.transitions : {},
      };
    }
  } catch {
    // Corrupted data — start fresh
  }
  return { history: [], transitions: {} };
}

function saveRecord(record: NavRecord): void {
  try {
    // Trim history to max size
    if (record.history.length > HISTORY_SIZE) {
      record.history = record.history.slice(-HISTORY_SIZE);
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
  } catch {
    // localStorage full or unavailable — non-critical
  }
}

/**
 * Returns the predicted next route based on the user's learned navigation patterns.
 * Returns `null` if the current route has no strong predictor.
 */
function predictNextRoute(record: NavRecord, currentRoute: string): string | null {
  // Find all transitions FROM the current route, sorted by frequency
  const candidates: { route: string; count: number }[] = [];
  for (const [key, count] of Object.entries(record.transitions)) {
    const [from, to] = key.split('→');
    if (from === currentRoute && count >= CONFIRM_THRESHOLD) {
      candidates.push({ route: to, count });
    }
  }

  if (candidates.length === 0) return null;

  // Pick the most frequent transition
  candidates.sort((a, b) => b.count - a.count);
  return candidates[0].route;
}

/**
 * React hook that learns navigation patterns and preloads predicted next pages.
 *
 * @param currentRoute - The current route path (e.g., `/sale`). Usually from `useLocation().pathname`.
 * @param options.maxPredictions - Max pages to preload per route (default 1).
 */
export function useNavigationPredictor(
  currentRoute: string,
  options?: { maxPredictions?: number },
): void {
  const maxPredictions = options?.maxPredictions ?? 1;
  const recordRef = useRef<NavRecord>(loadRecord());

  useEffect(() => {
    if (!currentRoute) return;
    const record = recordRef.current;

    // Get the previous route from history
    const prevRoute = record.history.length > 0 ? record.history[record.history.length - 1] : null;

    // Only record a transition if the route actually changed
    if (prevRoute && prevRoute !== currentRoute) {
      const key = `${prevRoute}→${currentRoute}`;
      record.transitions[key] = (record.transitions[key] || 0) + 1;
    }

    // Update history — avoid duplicate consecutive entries
    if (prevRoute !== currentRoute) {
      record.history.push(currentRoute);
    }

    saveRecord(record);

    // Predict and preload
    const predicted = predictNextRoute(record, currentRoute);
    if (predicted) {
      preloadRoute(predicted);
    }

    // If we allow more predictions, try secondary patterns
    if (maxPredictions > 1 && predicted) {
      // Look for common follow-ups to the predicted route as well
      const secondLevel = predictNextRoute(record, predicted);
      if (secondLevel && secondLevel !== predicted) {
        preloadRoute(secondLevel);
      }
    }
  }, [currentRoute, maxPredictions]);
}

/**
 * Returns the current navigation record for debugging or introspection.
 */
export function getNavRecord(): NavRecord {
  return loadRecord();
}

/**
 * Clears all learned navigation patterns.
 */
export function clearNavHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Best-effort
  }
}
