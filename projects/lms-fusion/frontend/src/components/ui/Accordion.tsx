'use client';

import { useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HiChevronDown } from 'react-icons/hi';

// ── Types ──

export interface AccordionItem {
  id: string;
  title: string;
  content: ReactNode;
  /** Icon or element shown before title */
  icon?: ReactNode;
}

interface AccordionProps {
  items: AccordionItem[];
  /** Allow multiple items to be open at once */
  multiple?: boolean;
  /** Default open item IDs */
  defaultOpen?: string[];
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Called when an item toggles */
  onToggle?: (itemId: string, isOpen: boolean) => void;
  /** Compact mode without borders between items */
  compact?: boolean;
}

// ── Content variants ──

const contentVariants = {
  collapsed: { height: 0, opacity: 0 },
  expanded: {
    height: 'auto' as unknown as number,
    opacity: 1,
    transition: { height: { duration: 0.3 }, opacity: { duration: 0.2, delay: 0.1 } },
  },
};

// ── Component ──

export default function Accordion({
  items,
  multiple = false,
  defaultOpen = [],
  size = 'md',
  className = '',
  onToggle,
  compact = false,
}: AccordionProps) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set(defaultOpen));

  const toggle = (itemId: string) => {
    setOpenItems((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
        onToggle?.(itemId, false);
      } else {
        if (!multiple) next.clear();
        next.add(itemId);
        onToggle?.(itemId, true);
      }
      return next;
    });
  };

  if (!items.length) return null;

  const sizeClasses = {
    sm: { button: 'px-3 py-2 text-xs', content: 'px-3 py-2 text-xs', icon: 'w-3.5 h-3.5' },
    md: { button: 'px-4 py-3 text-sm', content: 'px-4 py-3 text-sm', icon: 'w-4 h-4' },
    lg: { button: 'px-5 py-4 text-base', content: 'px-5 py-4 text-base', icon: 'w-5 h-5' },
  };

  const sc = sizeClasses[size] || sizeClasses.md;

  return (
    <div
      className={`divide-y divide-gray-200 ${!compact ? 'border border-gray-200 rounded-xl overflow-hidden' : ''} ${className}`}
      role="region"
      aria-label="Accordion"
    >
      {items.map((item) => {
        const isOpen = openItems.has(item.id);
        return (
          <div key={item.id} className="bg-white">
            {/* Header Button */}
            <button
              onClick={() => toggle(item.id)}
              className={`w-full flex items-center justify-between gap-3 text-left 
                ${sc.button} font-medium text-gray-900 hover:bg-gray-50 
                transition-colors duration-150 ${isOpen ? 'bg-gray-50/50' : ''}`}
              aria-expanded={isOpen}
              aria-controls={`accordion-content-${item.id}`}
            >
              <span className="flex items-center gap-2 min-w-0">
                {item.icon && <span className="flex-shrink-0 text-gray-400">{item.icon}</span>}
                <span className="truncate">{item.title}</span>
              </span>
              <motion.span
                animate={{ rotate: isOpen ? 180 : 0 }}
                transition={{ duration: 0.2 }}
                className="flex-shrink-0 text-gray-400"
              >
                <HiChevronDown className={sc.icon} />
              </motion.span>
            </button>

            {/* Content */}
            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  id={`accordion-content-${item.id}`}
                  key={`content-${item.id}`}
                  variants={contentVariants}
                  initial="collapsed"
                  animate="expanded"
                  exit="collapsed"
                  transition={{ duration: 0.3, ease: 'easeInOut' }}
                  className={`${sc.content} text-gray-600 border-t border-gray-100 overflow-hidden`}
                  role="region"
                  aria-labelledby={`accordion-header-${item.id}`}
                >
                  {item.content}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
