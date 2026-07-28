'use client';

import { motion } from 'framer-motion';

// ── Types ──

interface LoadingSpinnerProps {
  /** Spinner style variant */
  variant?: 'circular' | 'dots' | 'pulse' | 'progress';
  /** Size */
  size?: 'sm' | 'md' | 'lg';
  /** Color - Tailwind color class */
  color?: string;
  /** Label text shown below spinner */
  label?: string;
  /** Progress percentage (0-100) for 'progress' variant */
  progress?: number;
  /** Show as fullscreen page preloader */
  fullscreen?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// ── Size mappings ──

const sizeMap: Record<string, string> = {
  sm: 'w-5 h-5',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
};

const borderMap: Record<string, string> = {
  sm: 'border-2',
  md: 'border-3',
  lg: 'border-4',
};

// ── Circular Spinner ──

function CircularSpinner({ size, color, label }: { size: string; color: string; label?: string }) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div
        className={`${sizeMap[size]} rounded-full ${borderMap[size]} border-t-transparent animate-spin`}
        style={{ borderColor: `${color} transparent transparent transparent` }}
        role="status"
        aria-label="Loading"
      />
      {label && <p className="text-sm text-gray-500 animate-pulse">{label}</p>}
    </div>
  );
}

// ── Dots Spinner ──

function DotsSpinner({ size, label }: { size: string; label?: string }) {
  const dotSize = size === 'sm' ? 'w-2 h-2' : size === 'lg' ? 'w-4 h-4' : 'w-3 h-3';

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex items-center gap-1.5" role="status" aria-label="Loading">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className={`${dotSize} rounded-full bg-[rgb(var(--ctc-primary))]`}
            animate={{
              y: ['0%', '-50%', '0%'],
              opacity: [0.4, 1, 0.4],
            }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.15,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>
      {label && <p className="text-sm text-gray-500">{label}</p>}
    </div>
  );
}

// ── Pulse Spinner ──

function PulseSpinner({ size }: { size: string }) {
  const dim = size === 'sm' ? 'w-8 h-8' : size === 'lg' ? 'w-16 h-16' : 'w-12 h-12';

  return (
    <div className="relative flex items-center justify-center" role="status" aria-label="Loading">
      <motion.div
        className={`${dim} rounded-full bg-[rgb(var(--ctc-primary))]/20`}
        animate={{ scale: [1, 1.5, 1], opacity: [0.3, 0.1, 0.3] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      />
      <div
        className={`absolute ${sizeMap[size]} rounded-full bg-[rgb(var(--ctc-primary))]`}
      />
    </div>
  );
}

// ── Progress Bar ──

function ProgressBar({ progress, label }: { progress: number; label?: string }) {
  const pct = Math.min(100, Math.max(0, progress));

  return (
    <div className="flex flex-col items-center gap-3 w-full max-w-xs">
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-[rgb(var(--ctc-primary))] rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
      </div>
      <div className="flex items-center justify-between w-full">
        {label && <p className="text-sm text-gray-500">{label}</p>}
        <p className="text-sm font-medium text-[rgb(var(--ctc-primary))]">{pct}%</p>
      </div>
    </div>
  );
}

// ── Preloader (fullscreen overlay) ──

function FullscreenPreloader({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[200] flex items-center justify-center bg-white/80 backdrop-blur-sm"
    >
      {children}
    </motion.div>
  );
}

// ── Main Component ──

export default function LoadingSpinner({
  variant = 'circular',
  size = 'md',
  color = 'rgb(var(--ctc-primary))',
  label,
  progress = 0,
  fullscreen = false,
  className = '',
}: LoadingSpinnerProps) {
  const spinner = (() => {
    switch (variant) {
      case 'dots':
        return <DotsSpinner size={size} label={label} />;
      case 'pulse':
        return <PulseSpinner size={size} />;
      case 'progress':
        return <ProgressBar progress={progress} label={label} />;
      case 'circular':
      default:
        return <CircularSpinner size={size} color={color} label={label} />;
    }
  })();

  if (fullscreen) {
    return (
      <FullscreenPreloader>
        <div className={`${className}`}>{spinner}</div>
      </FullscreenPreloader>
    );
  }

  return <div className={`flex items-center justify-center ${className}`}>{spinner}</div>;
}
