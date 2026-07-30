// Allow legacy framer-motion props on HTML elements.
// These are left on elements after the framer-motion → CSS migration
// to avoid JSX breakage from regex-based prop stripping.
// They are inert at runtime — browsers ignore unknown HTML attributes.

import 'react';

declare module 'react' {
  interface HTMLAttributes<T> {
    initial?: unknown;
    animate?: unknown;
    exit?: unknown;
    transition?: unknown;
    variants?: unknown;
    whileHover?: unknown;
    whileTap?: unknown;
    whileInView?: unknown;
    layout?: unknown;
    layoutId?: unknown;
  }
  interface SVGAttributes<T> {
    initial?: unknown;
    animate?: unknown;
    exit?: unknown;
    transition?: unknown;
    variants?: unknown;
    whileHover?: unknown;
    whileTap?: unknown;
    whileInView?: unknown;
    layout?: unknown;
    layoutId?: unknown;
  }
}
