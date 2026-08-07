import { useState, useRef, useEffect, useCallback, type ReactNode } from 'react';

interface Props { mode?: 'wait' | 'sync'; children: ReactNode; initial?: boolean; }

/**
 * Stable identity for a child: its React `key` if it has one, otherwise a
 * generic marker. React elements are recreated on every parent render, so
 * comparing element references (`prev !== children`) would treat ANY in-place
 * re-render (e.g. typing in a form) as a step change and play a spurious exit.
 * Keying the comparison lets an in-place re-render of the SAME panel pass
 * through as an update while a real step switch (different key) still exits.
 *
 * Handles arrays (multiple sibling expressions like `{cond && <A/>}{cond && <B/>}`)
 * by resolving to the first truthy element's key, and both string and numeric
 * React keys.
 */
function childKey(child: ReactNode): string {
  if (Array.isArray(child)) {
    for (const c of child) {
      const k = childKey(c);
      if (k !== '__inplace__') return k;
    }
    return '__inplace__';
  }
  if (child !== null && typeof child === 'object' && 'key' in child) {
    const key = (child as { key?: unknown }).key;
    if (typeof key === 'string' || typeof key === 'number') return String(key);
  }
  return '__inplace__';
}

/**
 * Fallback window for the exit animation. Must be ≥ the fade-out duration
 * (`--animation__duration--fast` / `.animate-fade-out`, ~150ms) so the timer
 * never fires before the CSS animation would have ended.
 */
const EXIT_ANIMATION_MS = 200;

/**
 * CSS-based AnimatePresence — handles exit animations via animationend events.
 *
 * Includes a timer fallback: in jsdom, under `prefers-reduced-motion: reduce`,
 * or whenever CSS animations are disabled (`animation: none`), the
 * `animationend` event never fires and a `mode="wait"` exit would hang forever.
 * The fallback timer swaps in the new child after EXIT_ANIMATION_MS regardless.
 *
 * Presence is tracked by *truthiness* of `children` (usage pattern:
 * `{condition && <Element/>}`). Re-rendering an already-present child is an
 * in-place update — NOT an exit — so an open form/modal never leaves a stale
 * duplicate in the DOM.
 */
export default function AnimatePresence({ children, mode = 'sync' }: Props) {
  const [exitingChild, setExitingChild] = useState<ReactNode>(null);
  const [currentChild, setCurrentChild] = useState<ReactNode>(children);
  const exitRef = useRef<HTMLDivElement>(null);
  const prevRef = useRef<ReactNode>(children);
  const childrenRef = useRef<ReactNode>(children);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  // Keep childrenRef in sync every render so the timer callback always sees the
  // latest children (the classic stale-closure trap for timeout-based swaps).
  childrenRef.current = children;

  const completeExit = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = undefined;
    }
    setExitingChild(null);
    if (mode === 'wait') setCurrentChild(childrenRef.current);
  }, [mode]);

  useEffect(() => {
    // Clear any previously scheduled fallback timer before arming a new one so
    // rapid children changes can't leave orphaned timers behind.
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = undefined;
    }

    const prev = prevRef.current;
    const prevShown = !!prev;
    const nextShown = !!children;

    if (!nextShown) {
      // Child is being removed (or was never shown) — play the exit animation.
      if (prevShown) {
        setExitingChild(prev);
        if (mode === 'wait') setCurrentChild(null);
        else setCurrentChild(children);
        // Fallback: remove the exiting child after the exit window even if the
        // animationend event never fires (jsdom / reduced motion / animation:none).
        timerRef.current = setTimeout(completeExit, EXIT_ANIMATION_MS);
      } else {
        setCurrentChild(children);
        setExitingChild(null);
      }
    } else if (mode === 'wait' && prevShown && childKey(prev) !== childKey(children)) {
      // Switching between two mounted children with DIFFERENT keys in wait
      // mode: run the old child's exit animation, then swap in the new one.
      // Same-key re-renders (e.g. typing in a form) fall through to the
      // in-place update branch below and never trigger an exit.
      setExitingChild(prev);
      timerRef.current = setTimeout(completeExit, EXIT_ANIMATION_MS);
    } else {
      // Child is present — either appearing or re-rendering in place. Just show
      // the latest render without a spurious exit (keeps an open form/modal
      // from duplicating its DOM on every parent re-render).
      setCurrentChild(children);
      setExitingChild(null);
    }
    prevRef.current = children;
  }, [children, mode, completeExit]);

  // Clear any pending fallback timer on unmount.
  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current);
  }, []);

  return (
    <>
      {exitingChild && (
        <div ref={exitRef} className="animate-fade-out"
          onAnimationEnd={completeExit}
          style={{ pointerEvents: 'none' }}>
          {exitingChild}
        </div>
      )}
      {mode === 'wait' && exitingChild ? null : currentChild}
    </>
  );
}
