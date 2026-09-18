import { useEffect, useId, useRef, useState } from 'react';
import crest from '@formints-assets/images/formint-crest.svg';

const RING_RADIUS = 52;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

interface BrandLoaderProps {
  /** 'dark' is used on the auth-boot screen (slate-900 backdrop). */
  variant?: 'default' | 'dark';
}

/**
 * Branded full-page loader.
 *
 * The Formint crest logo sits inside a progress ring that fills 0 → 100% while
 * a percentage counter counts up with ease-out easing. It replaces BOTH legacy
 * full-page loading UIs (the route-level Suspense fallback and the auth-boot
 * screen) so every page navigation shows one consistent branded loading state
 * instead of duplicated plain spinners.
 */
export default function BrandLoader({ variant = 'default' }: BrandLoaderProps) {
  const dark = variant === 'dark';
  const gradientId = useId();
  const [progress, setProgress] = useState(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const duration = 1600; // ms to reach 100%
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      // ease-out cubic — fast start, decelerating toward 100%
      const eased = 1 - Math.pow(1 - t, 3);
      setProgress(Math.round(eased * 100));
      if (t < 1) rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  const dashOffset = RING_CIRCUMFERENCE * (1 - progress / 100);

  return (
    <div
      role="status"
      aria-live="polite"
      aria-label="Loading Formint"
      className={`min-h-[100dvh] w-full flex flex-col items-center justify-center gap-5
        transition-colors duration-300 ${dark ? 'bg-slate-900' : 'bg-base-100'}`}
    >
      {/* Crest logo inside an animated progress ring. The live-updating ring and
          percentage are decorative — hidden from the a11y tree so screen readers
          only announce the static "Loading…" text once (no 0%, 1%, 2%… chatter). */}
      <div className="relative w-28 h-28 sm:w-32 sm:h-32" aria-hidden="true">
        <svg viewBox="0 0 120 120" className="absolute inset-0 -rotate-90">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FB923C" />
              <stop offset="100%" stopColor="#EA580C" />
            </linearGradient>
          </defs>
          {/* track */}
          <circle
            cx="60" cy="60" r={RING_RADIUS} fill="none" strokeWidth="4"
            className={dark ? 'stroke-white/15' : 'stroke-base-200/80'}
          />
          {/* fill — dashoffset shrinks as the percentage rises */}
          <circle
            cx="60" cy="60" r={RING_RADIUS} fill="none" strokeWidth="4"
            strokeLinecap="round" stroke={`url(#${gradientId})`}
            strokeDasharray={RING_CIRCUMFERENCE}
            strokeDashoffset={dashOffset}
            className="transition-[stroke-dashoffset] duration-75 ease-linear"
          />
        </svg>
        <img
          src={crest as unknown as string}
          alt=""
          className="absolute inset-0 w-full h-full object-contain drop-shadow-lg animate-scale-in"
        />
      </div>

      {/* Wordmark + percentage — decorative */}
      <div className="flex flex-col items-center gap-1" aria-hidden="true">
        <span className={`text-xl font-bold tracking-tight ${dark ? 'text-white/90' : 'text-base-content'}`}>
          Formint
        </span>
        <div className="flex items-baseline gap-0.5">
          <span className={`text-3xl font-extrabold tabular-nums ${dark ? 'text-orange-400' : 'text-primary'}`}>
            {progress}
          </span>
          <span className={`text-sm font-medium ${dark ? 'text-white/50' : 'text-base-content/50'}`}>%</span>
        </div>
      </div>

      <span className={`text-xs animate-pulse ${dark ? 'text-white/40' : 'text-base-content/40'}`}>
        Loading…
      </span>
    </div>
  );
}
