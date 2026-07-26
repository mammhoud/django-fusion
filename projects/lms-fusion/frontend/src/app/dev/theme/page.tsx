'use client';

/**
 * Theme Showcase Page — /dev/theme
 *
 * Renders every CSS custom property, component class, and UI variant
 * on a single page for visual regression testing via Playwright.
 *
 * NOTE: This page is intended for development and testing only.
 * It is excluded from production builds by the NODE_ENV guard below.
 *
 * Sections:
 *  1. Color Swatches — every --ctc-* variable
 *  2. Typography — heading hierarchy + body text
 *  3. Buttons — all variants + states
 *  4. Cards — base, hover, gradient
 *  5. Inputs — default, focus, error, disabled
 *  6. Badges — primary, success, warning
 *  7. UI Components — LoadingSkeleton, ErrorState, EmptyState
 *  8. Progress — track + fill
 *  9. Feature Icons + Service Cards
 * 10. FAQ Accordion
 */

import { notFound } from 'next/navigation';
import { useState } from 'react';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import EmptyState from '@/components/ui/EmptyState';

// ── Color Swatch Data ──────────────────────────────────────────

interface Swatch {
  name: string;
  variable: string;
  rgb: string;
  hex: string;
}

const CTC_SWATCHES: Swatch[] = [
  { name: 'Primary', variable: '--ctc-primary', rgb: '0 161 179', hex: '#00a1b3' },
  { name: 'Primary Dark', variable: '--ctc-primary-dark', rgb: '0 122 136', hex: '#007a88' },
  { name: 'Primary Light', variable: '--ctc-primary-light', rgb: '26 127 212', hex: '#1a7fd4' },
  { name: 'Secondary', variable: '--ctc-secondary', rgb: '0 128 128', hex: '#008080' },
  { name: 'Accent', variable: '--ctc-accent', rgb: '108 99 255', hex: '#6c63ff' },
  { name: 'Accent Alt', variable: '--ctc-accent-alt', rgb: '255 107 139', hex: '#ff6b8b' },
];

// ── Component ──────────────────────────────────────────────────

export default function ThemeShowcasePage() {
  // Guard: exclude from production builds
  if (process.env.NODE_ENV === 'production') {
    notFound();
  }

  const [toggleState, setToggleState] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* ── Header ────────────────────────────────────────── */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            CTC Theme Showcase
          </h1>
          <p className="text-gray-500 text-lg">
            Visual regression reference for all theme tokens, components, and variants
          </p>
        </div>

        {/* ── 1. Color Swatches ──────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">1. CTC Color Palette</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {CTC_SWATCHES.map((swatch) => (
              <div key={swatch.variable} className="card p-4 text-center" data-testid={`swatch-${swatch.name.toLowerCase().replace(/\s+/g, '-')}`}>
                <div
                  className="w-full h-20 rounded-lg mb-3 shadow-inner"
                  style={{ backgroundColor: `rgb(${swatch.rgb})` }}
                />
                <p className="text-sm font-semibold text-gray-900">{swatch.name}</p>
                <p className="text-xs text-gray-500 font-mono">{swatch.variable}</p>
                <p className="text-xs text-gray-400 font-mono">{swatch.hex}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── 2. Typography ──────────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">2. Typography</h2>
          <div className="card p-8 space-y-4">
            <h1 className="text-4xl font-bold">Heading 1 — Urbanist Bold 4xl</h1>
            <h2 className="text-3xl font-bold">Heading 2 — Urbanist Bold 3xl</h2>
            <h3 className="text-2xl font-bold">Heading 3 — Urbanist Bold 2xl</h3>
            <h4 className="text-xl font-bold">Heading 4 — Urbanist Bold xl</h4>
            <p className="text-base text-gray-600 leading-relaxed max-w-2xl">
              Body text — System font stack, 16px, 1.6 line-height. This paragraph
              demonstrates the default body copy styling used across all public and
              dashboard pages in the LMS platform.
            </p>
            <p className="text-sm text-gray-500">Small text — 14px, used for captions and metadata</p>
            <p className="text-xs text-gray-400">Extra small — 12px, used for labels and badges</p>
          </div>
        </section>

        {/* ── 3. Buttons ─────────────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">3. Buttons</h2>
          <div className="card p-8">
            <div className="flex flex-wrap gap-4 items-center mb-4">
              <button className="btn-primary" data-testid="btn-primary">Primary</button>
              <button className="btn-primary" disabled data-testid="btn-primary-disabled">Primary Disabled</button>
              <button className="btn-secondary" data-testid="btn-secondary">Secondary</button>
              <button className="btn-outline" data-testid="btn-outline">Outline</button>
              <button className="btn-accent" data-testid="btn-accent">Accent</button>
              <button className="btn-white" data-testid="btn-white">White</button>
            </div>
            <div className="flex flex-wrap gap-4 items-center mt-4">
              <button className="btn-primary text-sm !px-4 !py-2">Small Primary</button>
              <button className="btn-primary text-lg !px-10 !py-4">Large Primary</button>
              <button className="btn-secondary flex items-center gap-2">
                <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor"><path d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"/></svg>
                With Icon
              </button>
            </div>
          </div>
        </section>

        {/* ── 4. Cards ───────────────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">4. Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6" data-testid="card-base">
              <h3 className="font-semibold text-gray-900 mb-2">Base Card</h3>
              <p className="text-sm text-gray-500">Default card with shadow-sm and border-gray-100</p>
            </div>
            <div className="card-hover p-6" data-testid="card-hover">
              <h3 className="font-semibold text-gray-900 mb-2">Hover Card</h3>
              <p className="text-sm text-gray-500">Lifts on hover with translate-y and shadow-md</p>
            </div>
            <div className="card-gradient p-6 rounded-xl h-32" data-testid="card-gradient">
              <h3 className="font-semibold text-white">Gradient Card</h3>
              <p className="text-sm text-white/80">CTC primary → primary-dark gradient</p>
            </div>
          </div>
        </section>

        {/* ── 5. Inputs ──────────────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">5. Form Inputs</h2>
          <div className="card p-8 space-y-4 max-w-md">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Default Input</label>
              <input type="text" className="input-field" placeholder="Placeholder text..." data-testid="input-default" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Filled Input</label>
              <input type="text" className="input-field" defaultValue="Filled value" data-testid="input-filled" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Disabled Input</label>
              <input type="text" className="input-field" disabled placeholder="Disabled..." data-testid="input-disabled" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Textarea</label>
              <textarea className="input-field" rows={3} placeholder="Multi-line input..." data-testid="textarea" />
            </div>
          </div>
        </section>

        {/* ── 6. Badges ──────────────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">6. Badges</h2>
          <div className="card p-8 flex flex-wrap gap-3">
            <span className="badge-primary" data-testid="badge-primary">Primary</span>
            <span className="badge-success" data-testid="badge-success">Success</span>
            <span className="badge-warning" data-testid="badge-warning">Warning</span>
            <span className="badge bg-red-100 text-red-800">Danger</span>
            <span className="badge bg-gray-100 text-gray-600">Neutral</span>
          </div>
        </section>

        {/* ── 7. UI Components ───────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">7. UI Components</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card p-6" data-testid="component-loading">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm uppercase tracking-wide">Loading Skeleton</h3>
              <LoadingSkeleton variant="card" />
            </div>
            <div className="card p-6" data-testid="component-error">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm uppercase tracking-wide">Error State</h3>
              <ErrorState message="Something went wrong while loading data." />
            </div>
            <div className="card p-6" data-testid="component-empty">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm uppercase tracking-wide">Empty State</h3>
              <EmptyState
                icon="courses"
                title="No items yet"
                description="Create your first item to get started."
                actionLabel="Create Item"
                actionHref="/dev/theme"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="card p-6" data-testid="component-skeleton-list">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm uppercase tracking-wide">Skeleton — List Variant</h3>
              <LoadingSkeleton variant="list" count={3} />
            </div>
            <div className="card p-6" data-testid="component-skeleton-detail">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm uppercase tracking-wide">Skeleton — Detail Variant</h3>
              <LoadingSkeleton variant="detail" />
            </div>
          </div>
        </section>

        {/* ── 8. Progress ────────────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">8. Progress Bars</h2>
          <div className="card p-8 space-y-4 max-w-md">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">0%</span>
                <span className="text-gray-600">50%</span>
              </div>
              <div className="progress-track" data-testid="progress-50">
                <div className="progress-fill" style={{ width: '50%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">75%</span>
              </div>
              <div className="progress-track" data-testid="progress-75">
                <div className="progress-fill" style={{ width: '75%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">100%</span>
              </div>
              <div className="progress-track" data-testid="progress-100">
                <div className="progress-fill" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        </section>

        {/* ── 9. Feature Icons + Stat Cards ──────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">9. Icons &amp; Stats</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="stat-card" data-testid="stat-card">
              <div className="feature-icon mx-auto">
                <svg className="w-6 h-6" viewBox="0 0 20 20" fill="currentColor"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/></svg>
              </div>
              <div className="stat-value">1,234</div>
              <div className="stat-label">Students</div>
            </div>
            <div className="service-card" data-testid="service-card">
              <div className="service-icon">
                <svg className="w-8 h-8" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd"/></svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">Development</h3>
              <p className="text-sm text-gray-500">Full-stack web development courses</p>
            </div>
            <div className="contact-card" data-testid="contact-card">
              <div className="contact-icon">
                <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor"><path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/><path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/></svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 text-sm">Email Us</h4>
                <p className="text-xs text-gray-500">support@structa.cloud</p>
              </div>
            </div>
            <div className="avatar-sm mx-auto" data-testid="avatar">
              SA
            </div>
          </div>
        </section>

        {/* ── 10. FAQ Accordion ──────────────────────────────── */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">10. FAQ Accordion</h2>
          <div className="card p-6 space-y-3 max-w-2xl">
            <div className="faq-item" data-testid="faq-item">
              <button
                className="faq-question"
                onClick={() => setToggleState(!toggleState)}
              >
                <span>What is this theme showcase?</span>
                <svg className={`w-5 h-5 transition-transform ${toggleState ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd"/></svg>
              </button>
              {toggleState && (
                <div className="faq-answer">
                  <p>A comprehensive reference page for visual regression testing of all CTC theme tokens and UI components.</p>
                </div>
              )}
            </div>
            <div className="faq-item">
              <button className="faq-question">
                <span>How do I use this for testing?</span>
                <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd"/></svg>
              </button>
            </div>
          </div>
        </section>

        {/* ── Footer ──────────────────────────────────────────── */}
        <div className="text-center text-xs text-gray-400 mt-16 pt-8 border-t border-gray-200" data-testid="showcase-footer">
          CTC Theme Showcase — Visual Regression Reference — Static Baseline
        </div>
      </div>
    </div>
  );
}
