'use client';

import { useState, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ── Types ──

export interface Tab {
  id: string;
  label: string;
  content: ReactNode;
  /** Optional icon */
  icon?: ReactNode;
  /** Disable this tab */
  disabled?: boolean;
  /** Badge/count to show next to label */
  badge?: number | string;
}

interface TabsProps {
  tabs: Tab[];
  /** Active tab ID (controlled) */
  activeTab?: string;
  /** Default active tab ID (uncontrolled) */
  defaultTab?: string;
  /** Called when tab switches */
  onChange?: (tabId: string) => void;
  /** Visual style */
  variant?: 'underline' | 'pills' | 'buttons';
  /** Size */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes for the tab list */
  className?: string;
  /** Additional CSS classes for the content area */
  contentClassName?: string;
  /** Animation variant for content switching */
  animation?: 'fade' | 'slide' | 'none';
  /** Show content area even when no tabs match */
  showEmptyContent?: boolean;
  /** Right-aligned action element shown in tab bar */
  actions?: ReactNode;
  /** Full width tabs (each tab takes equal space) */
  fullWidth?: boolean;
}

// ── Variants ──

const underlineActiveClass = "text-[rgb(var(--ctc-primary))] border-b-2 border-[rgb(var(--ctc-primary))]";
const pillsActiveClass = "bg-[rgb(var(--ctc-primary))] text-white shadow-sm";
const buttonsActiveClass = "bg-gray-100 text-gray-900";

const contentVariants = {
  fade: {
    enter: { opacity: 0, y: 8 },
    center: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -8 },
  },
  slide: {
    enter: { opacity: 0, x: 20 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
  },
  none: {
    enter: {},
    center: {},
    exit: {},
  },
};

// ── Component ──

export default function Tabs({
  tabs,
  activeTab: controlledTab,
  defaultTab,
  onChange,
  variant = 'underline',
  size = 'md',
  className = '',
  contentClassName = '',
  animation = 'fade',
  showEmptyContent = false,
  actions,
  fullWidth = false,
}: TabsProps) {
  const [internalTab, setInternalTab] = useState(defaultTab || tabs[0]?.id || '');
  const activeTab = controlledTab ?? internalTab;

  const setActive = (tabId: string) => {
    if (controlledTab === undefined) setInternalTab(tabId);
    onChange?.(tabId);
  };

  const activeContent = tabs.find((t) => t.id === activeTab)?.content;

  const sizeClasses = {
    sm: 'text-xs px-3 py-1.5',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-5 py-2.5',
  };
  const sc = sizeClasses[size] || sizeClasses.md;

  const variantClasses = (tab: Tab, isActive: boolean) => {
    switch (variant) {
      case 'underline':
        return `${sc} ${isActive ? underlineActiveClass : 'text-gray-500 hover:text-gray-700 border-b-2 border-transparent'}`;
      case 'pills':
        return `${sc} rounded-lg ${isActive ? pillsActiveClass : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}`;
      case 'buttons':
        return `${sc} rounded-md ${isActive ? buttonsActiveClass : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'}`;
      default:
        return `${sc}`;
    }
  };

  if (!tabs.length) return null;

  return (
    <div>
      {/* Tab List */}
      <div
        className={`flex items-center ${variant === 'underline' ? 'border-b border-gray-200' : ''} 
          ${fullWidth ? 'w-full' : ''} gap-1 ${className}`}
        role="tablist"
        aria-orientation="horizontal"
      >
        <div className={`flex ${fullWidth ? 'w-full' : ''} ${variant !== 'underline' ? 'gap-1' : ''}`}>
          {tabs.map((tab) => {
            const isActive = tab.id === activeTab;
            return (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setActive(tab.id)}
                disabled={tab.disabled}
                role="tab"
                aria-selected={isActive}
                aria-controls={`tab-panel-${tab.id}`}
                tabIndex={isActive ? 0 : -1}
                className={`relative flex items-center gap-2 whitespace-nowrap font-medium 
                  transition-all duration-200 outline-none
                  ${fullWidth ? 'flex-1 justify-center' : ''}
                  ${tab.disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
                  ${variantClasses(tab, isActive)}`}
              >
                {tab.icon && <span className="flex-shrink-0">{tab.icon}</span>}
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                      isActive && variant === 'underline'
                        ? 'bg-[rgb(var(--ctc-primary))] text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
        {actions && <div className="ml-auto flex items-center gap-2 flex-shrink-0">{actions}</div>}
      </div>

      {/* Tab Content */}
      <div className={`mt-4 ${contentClassName}`}>
        {activeContent !== undefined || showEmptyContent ? (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              variants={contentVariants[animation]}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.2, ease: 'easeInOut' }}
              role="tabpanel"
              id={`tab-panel-${activeTab}`}
              aria-labelledby={activeTab}
            >
              {activeContent}
            </motion.div>
          </AnimatePresence>
        ) : null}
      </div>
    </div>
  );
}
