import type { Variants, Transition } from 'framer-motion';

// ── Shared transitions ──

const springGentle: Transition = {
  type: 'spring' as const,
  stiffness: 200,
  damping: 22,
  mass: 0.8,
};

const springSnappy: Transition = {
  type: 'spring' as const,
  stiffness: 300,
  damping: 25,
  mass: 0.5,
};

const easeOut: Transition = {
  duration: 0.2,
  ease: [0.25, 0.1, 0.25, 1],
};

const easeOutQuick: Transition = {
  duration: 0.2,
  ease: 'easeOut',
};

// ── Page-level entrance ──

/** Standard page entrance: fades in and slides up slightly. */
export const pageSlideUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: easeOut,
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: { duration: 0.2 },
  },
};

/** Simple fade-in for sub-sections and content panels. */
export const pageFadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: easeOut,
  },
  exit: {
    opacity: 0,
    transition: { duration: 0.15 },
  },
};

/** Slide-in from the right (e.g. tab content panels, detail panels). */
export const pageSlideRight: Variants = {
  enter: { opacity: 0, x: 20 },
  center: { opacity: 1, x: 0, transition: easeOutQuick },
  exit: { opacity: 0, x: -20, transition: { duration: 0.15 } },
};

/** Slide-in from the left (for back-navigation or reveal panels). */
export const pageSlideLeft: Variants = {
  enter: { opacity: 0, x: -20 },
  center: { opacity: 1, x: 0, transition: easeOutQuick },
  exit: { opacity: 0, x: 20, transition: { duration: 0.15 } },
};

// ── Staggered list animations ──

/** Parent container that staggers its children. */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

/** Individual item in a staggered list. */
export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: springGentle,
  },
};

// ── Dialog / overlay entrance ──

/** Dialog backdrop overlay. */
export const dialogBackdrop: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: easeOutQuick },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

/** Dialog content panel (scale + fade). */
export const dialogContent: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: springGentle,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15 },
  },
};

// ── Small-element animations ──

/** Icon pop-in (spring scale from 0). */
export const iconSpring = {
  initial: { scale: 0 },
  animate: {
    scale: 1,
    transition: springSnappy,
  },
} as const;

/** Dropdown menu entrance (grow down). */
export const dropdownMenu: Variants = {
  hidden: { opacity: 0, y: -8, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 4,
    scale: 1,
    transition: easeOutQuick,
  },
  exit: {
    opacity: 0,
    y: -8,
    scale: 0.95,
    transition: { duration: 0.12 },
  },
};

/** Toast/notification slide-in from top. */
export const toastSlideIn: Variants = {
  hidden: { opacity: 0, y: -24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: springGentle,
  },
  exit: {
    opacity: 0,
    y: -24,
    transition: { duration: 0.15 },
  },
};

/** Toast/notification slide-in from bottom. */
export const toastSlideUp: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: springGentle,
  },
  exit: {
    opacity: 0,
    y: 20,
    scale: 0.95,
    transition: { duration: 0.15 },
  },
};
