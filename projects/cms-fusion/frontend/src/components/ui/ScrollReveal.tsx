'use client';

import { useRef, useState, useEffect, type ReactNode } from 'react';
import { motion, useInView } from 'framer-motion';

// ── Types ──

interface ScrollRevealProps {
  children: ReactNode;
  /** Animation type */
  animation?: 'fadeIn' | 'fadeUp' | 'fadeDown' | 'fadeLeft' | 'fadeRight' | 'zoomIn' | 'zoomOut' | 'flipUp' | 'flipDown' | 'none';
  /** Delay in seconds */
  delay?: number;
  /** Duration in seconds */
  duration?: number;
  /** Threshold for triggering (0-1) */
  threshold?: number;
  /** Once only (don't re-trigger) */
  once?: boolean;
  /** Stagger children (for lists) */
  stagger?: boolean;
  /** Stagger delay between children in seconds */
  staggerDelay?: number;
  /** Additional CSS classes */
  className?: string;
  /** As HTML element tag */
  as?: 'div' | 'section' | 'article' | 'span' | 'li';
}

// ── Animation Variants ──

const getVariants = (animation: string, delay: number, duration: number) => {
  const base = {
    hidden: {},
    visible: {
      transition: { delay, duration, ease: 'easeOut' },
    },
  };

  switch (animation) {
    case 'fadeIn':
      return {
        hidden: { opacity: 0 },
        visible: { opacity: 1, ...base.visible },
      };
    case 'fadeUp':
      return {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0, ...base.visible },
      };
    case 'fadeDown':
      return {
        hidden: { opacity: 0, y: -30 },
        visible: { opacity: 1, y: 0, ...base.visible },
      };
    case 'fadeLeft':
      return {
        hidden: { opacity: 0, x: -30 },
        visible: { opacity: 1, x: 0, ...base.visible },
      };
    case 'fadeRight':
      return {
        hidden: { opacity: 0, x: 30 },
        visible: { opacity: 1, x: 0, ...base.visible },
      };
    case 'zoomIn':
      return {
        hidden: { opacity: 0, scale: 0.9 },
        visible: { opacity: 1, scale: 1, ...base.visible },
      };
    case 'zoomOut':
      return {
        hidden: { opacity: 0, scale: 1.1 },
        visible: { opacity: 1, scale: 1, ...base.visible },
      };
    case 'flipUp':
      return {
        hidden: { opacity: 0, rotateX: 90 },
        visible: { opacity: 1, rotateX: 0, ...base.visible },
      };
    case 'flipDown':
      return {
        hidden: { opacity: 0, rotateX: -90 },
        visible: { opacity: 1, rotateX: 0, ...base.visible },
      };
    case 'none':
    default:
      return {
        hidden: {},
        visible: { ...base.visible },
      };
  }
};

// ── Stagger variants ──

const staggerVariants = (animation: string, staggerDelay: number) => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren: staggerDelay,
    },
  },
});

// ── Single element reveal ──

function SingleReveal({
  children,
  animation = 'fadeUp',
  delay = 0,
  duration = 0.5,
  threshold = 0.1,
  once = true,
  className = '',
  as: Tag = 'div',
}: ScrollRevealProps) {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once, amount: threshold });

  const variants = getVariants(animation, delay, duration);

  const MotionComponent = motion[Tag as keyof typeof motion] ?? motion.div;

  return (
    <MotionComponent
      ref={ref}
      variants={variants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      className={className}
    >
      {children}
    </MotionComponent>
  );
}

// ── Stagger container ──

function StaggerReveal({
  children,
  animation = 'fadeUp',
  delay = 0,
  duration = 0.5,
  threshold = 0.1,
  once = true,
  staggerDelay = 0.1,
  className = '',
  as: Tag = 'div',
}: ScrollRevealProps) {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once, amount: threshold });

  const itemVariants = getVariants(animation, delay, duration);
  const MotionComponent = motion[Tag as keyof typeof motion] ?? motion.div;

  return (
    <MotionComponent
      ref={ref}
      variants={staggerVariants(animation, staggerDelay)}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      className={className}
    >
      {children}
    </MotionComponent>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Animated Counter
// ═══════════════════════════════════════════════════════════════════

interface AnimatedCounterProps {
  from?: number;
  to: number;
  duration?: number;
  suffix?: string;
  prefix?: string;
  className?: string;
  /** Show when in view */
  inView?: boolean;
  threshold?: number;
  /** Format with commas */
  format?: boolean;
}

export function AnimatedCounter({
  from = 0,
  to,
  duration = 2,
  suffix = '',
  prefix = '',
  className = '',
  inView = true,
  threshold = 0.5,
  format = true,
}: AnimatedCounterProps) {
  const [count, setCount] = useState(from);
  const ref = useRef<HTMLElement>(null);
  const isVisible = useInView(ref, { once: true, amount: threshold });
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    if (!inView || (isVisible && !hasStarted)) {
      setHasStarted(true);
      const startTime = performance.now();
      const range = to - from;

      const animate = (currentTime: number) => {
        const elapsed = (currentTime - startTime) / 1000;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out quad
        const eased = 1 - (1 - progress) * (1 - progress);
        const current = Math.round(from + range * eased);
        setCount(current);

        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };

      requestAnimationFrame(animate);
    }
  }, [isVisible, from, to, duration, inView, hasStarted]);

  const display = format ? count.toLocaleString() : count.toString();

  return (
    <div ref={ref} className={className}>
      {prefix}{display}{suffix}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Animated Progress Bar
// ═══════════════════════════════════════════════════════════════════

interface AnimatedProgressProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  color?: string;
  height?: number;
  className?: string;
  threshold?: number;
}

export function AnimatedProgress({
  value,
  max = 100,
  label,
  showPercentage = true,
  color,
  height = 8,
  className = '',
  threshold = 0.3,
}: AnimatedProgressProps) {
  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once: true, amount: threshold });
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div ref={ref} className={className}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-medium text-[rgb(var(--fu-primary))]">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      <div
        className="bg-gray-200 rounded-full overflow-hidden"
        style={{ height }}
      >
        <motion.div
          className="h-full rounded-full bg-[rgb(var(--fu-primary))]"
          style={color ? { backgroundColor: color } : undefined}
          initial={{ width: 0 }}
          animate={{ width: isInView ? `${percentage}%` : 0 }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Main ScrollReveal export
// ═══════════════════════════════════════════════════════════════════

export default function ScrollReveal(props: ScrollRevealProps) {
  if (props.stagger) {
    return <StaggerReveal {...props} />;
  }
  return <SingleReveal {...props} />;
}


