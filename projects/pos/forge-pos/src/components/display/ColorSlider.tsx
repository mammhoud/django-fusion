import { useCallback, useState, useRef } from 'react';

interface ColorSliderProps {
  /** Slider label (e.g. 'Lightness', 'Chroma', 'Hue') */
  label: string;
  /** Current value */
  value: number;
  /** Minimum value */
  min: number;
  /** Maximum value */
  max: number;
  /** Step increment */
  step: number;
  /** Display suffix (%, °, or '') */
  suffix: string;
  /** Called on every drag */
  onChange: (value: number) => void;
  /** CSS color for the slider track fill */
  trackColor?: string;
}

export default function ColorSlider({
  label,
  value,
  min,
  max,
  step,
  suffix,
  onChange,
  trackColor,
}: ColorSliderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const trackRef = useRef<HTMLDivElement>(null);

  const pct = ((value - min) / (max - min)) * 100;

  const handlePointerMove = useCallback(
    (e: PointerEvent) => {
      if (!trackRef.current) return;
      const rect = trackRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const raw = min + x * (max - min);
      const snapped = Math.round(raw / step) * step;
      onChange(Math.max(min, Math.min(max, snapped)));
    },
    [min, max, step, onChange]
  );

  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
    document.removeEventListener('pointermove', handlePointerMove);
    document.removeEventListener('pointerup', handlePointerUp);
  }, [handlePointerMove]);

  const handlePointerDown = useCallback(() => {
    setIsDragging(true);
    document.addEventListener('pointermove', handlePointerMove);
    document.addEventListener('pointerup', handlePointerUp);
  }, [handlePointerMove, handlePointerUp]);

  return (
    <div className="flex items-center gap-3 py-1 group">
      <span className="text-[10px] font-medium text-base-content/60 w-12 shrink-0 text-right">
        {label}
      </span>
      <div
        ref={trackRef}
        className="relative flex-1 h-5 flex items-center cursor-pointer select-none"
        onPointerDown={handlePointerDown}
        role="slider"
        tabIndex={0}
        aria-label={label}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        onKeyDown={(e) => {
          let delta = 0;
          if (e.key === 'ArrowRight' || e.key === 'ArrowUp') delta = step;
          else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') delta = -step;
          else if (e.key === 'Home') delta = min - value;
          else if (e.key === 'End') delta = max - value;
          if (delta) {
            e.preventDefault();
            onChange(Math.max(min, Math.min(max, value + delta)));
          }
        }}
      >
        {/* Track background */}
        <div className="absolute inset-x-0 h-1.5 rounded-full bg-base-300/60" />
        {/* Track fill */}
        <div
          className="absolute left-0 h-1.5 rounded-full transition-colors"
          style={{
            width: `${pct}%`,
            backgroundColor: trackColor || 'var(--color-primary, oklch(54.61% 0.2152 262.88))',
          }}
        />
        {/* Thumb */}
        <div
          className={`absolute w-3.5 h-3.5 rounded-full bg-base-100 border-2 shadow-sm transition-all ${
            isDragging
              ? 'border-primary scale-125 shadow-md'
              : 'border-base-content/30 group-hover:border-primary/60'
          }`}
          style={{ left: `calc(${pct}% - 7px)` }}
        />
      </div>
      <span className="text-[11px] font-mono text-base-content/70 w-14 shrink-0 text-left tabular-nums">
        {value.toFixed(step < 0.01 ? 2 : step < 0.1 ? 2 : 1)}{suffix}
      </span>
    </div>
  );
}
