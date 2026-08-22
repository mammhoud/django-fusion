/**
 * @formints/design-system — Motion Choreography Example
 * 
 * Demonstrates all motion presets and cubic-bezier transitions
 * for CRUD interactions.
 */

import React, { useState } from 'react';
import {
  BentoGrid,
  BentoItem,
  BezelCard,
  BezelWidget,
  CompactButton,
  CompactBadge,
  CompactInput,
  useScrollReveal,
} from '../src';

export default function MotionChoreographyExample() {
  const [activeTab, setActiveTab] = useState('transitions');
  const scrollRef = useScrollReveal({ stagger: true });

  return (
    <div className="p-6 space-y-8">
      {/* ── Eyebrow Tag ── */}
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-primary/10 text-primary">
          <span className="ri-sparkling-line ri-12px" />
          Motion Choreography
        </span>
      </div>

      {/* ── Section 1: Premium Easing Functions ── */}
      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-base-content/50">
          Premium Easing Functions
        </h2>
        
        <BentoGrid variant="dense" gap="md">
          <BentoItem hover>
            <div className="space-y-3">
              <h3 className="text-xs font-semibold">Fluid</h3>
              <div className="space-y-2">
                <div className="h-8 bg-primary/20 rounded-lg transition-all duration-500 ease-[var(--ease-fluid)] hover:bg-primary/40 hover:translate-x-2" />
                <p className="text-[10px] text-base-content/50">cubic-bezier(0.32, 0.72, 0, 1)</p>
              </div>
            </div>
          </BentoItem>

          <BentoItem hover>
            <div className="space-y-3">
              <h3 className="text-xs font-semibold">Bounce</h3>
              <div className="space-y-2">
                <div className="h-8 bg-success/20 rounded-lg transition-all duration-500 ease-[var(--ease-bounce)] hover:bg-success/40 hover:translate-x-2" />
                <p className="text-[10px] text-base-content/50">cubic-bezier(0.34, 1.56, 0.64, 1)</p>
              </div>
            </div>
          </BentoItem>

          <BentoItem hover>
            <div className="space-y-3">
              <h3 className="text-xs font-semibold">Spring</h3>
              <div className="space-y-2">
                <div className="h-8 bg-info/20 rounded-lg transition-all duration-500 ease-[var(--ease-spring)] hover:bg-info/40 hover:translate-x-2" />
                <p className="text-[10px] text-base-content/50">cubic-bezier(0.175, 0.885, 0.32, 1.275)</p>
              </div>
            </div>
          </BentoItem>

          <BentoItem hover>
            <div className="space-y-3">
              <h3 className="text-xs font-semibold">Elastic</h3>
              <div className="space-y-2">
                <div className="h-8 bg-warning/20 rounded-lg transition-all duration-500 ease-[var(--ease-elastic)] hover:bg-warning/40 hover:translate-x-2" />
                <p className="text-[10px] text-base-content/50">cubic-bezier(0.68, -0.55, 0.265, 1.55)</p>
              </div>
            </div>
          </BentoItem>
        </BentoGrid>
      </section>

      {/* ── Section 2: CRUD Interactions ── */}
      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-base-content/50">
          CRUD Interactions
        </h2>

        <BentoGrid variant="asymmetric" gap="md">
          {/* Card hover */}
          <BentoItem colSpan={6} hover>
            <BezelCard size="md" accent="primary">
              <div className="space-y-3">
                <h3 className="text-sm font-semibold">Card Hover</h3>
                <p className="text-xs text-base-content/50">
                  Double-Bezel lift effect with premium fluid transition
                </p>
                <div className="flex gap-2">
                  <CompactBadge variant="primary" size="sm">Lift</CompactBadge>
                  <CompactBadge variant="soft" size="sm">500ms</CompactBadge>
                </div>
              </div>
            </BezelCard>
          </BentoItem>

          {/* Button press */}
          <BentoItem colSpan={6} hover>
            <div className="space-y-4">
              <h3 className="text-sm font-semibold">Button Press</h3>
              <div className="flex flex-wrap gap-3">
                <CompactButton
                  variant="primary"
                  size="sm"
                  icon={<span className="ri-add-line" />}
                  label="Primary"
                />
                <CompactButton
                  variant="secondary"
                  size="sm"
                  icon={<span className="ri-check-line" />}
                  label="Secondary"
                />
                <CompactButton
                  variant="danger"
                  size="sm"
                  icon={<span className="ri-delete-bin-line" />}
                  label="Danger"
                />
                <CompactButton
                  variant="success"
                  size="sm"
                  icon={<span className="ri-save-line" />}
                  label="Success"
                />
              </div>
              <p className="text-[10px] text-base-content/50">
                Physical press feel with 100ms scale(0.98) transition
              </p>
            </div>
          </BentoItem>

          {/* Input focus */}
          <BentoItem colSpan={4} hover>
            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Input Focus</h3>
              <CompactInput
                label="Field Name"
                placeholder="Type here..."
              />
              <p className="text-[10px] text-base-content/50">
                Border color + ring with 200ms fluid transition
              </p>
            </div>
          </BentoItem>

          {/* Badge pop */}
          <BentoItem colSpan={4} hover>
            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Badge Pop</h3>
              <div className="flex flex-wrap gap-2">
                <CompactBadge variant="primary" size="sm">Primary</CompactBadge>
                <CompactBadge variant="success" size="sm">Success</CompactBadge>
                <CompactBadge variant="warning" size="sm">Warning</CompactBadge>
                <CompactBadge variant="error" size="sm">Error</CompactBadge>
                <CompactBadge variant="info" size="sm">Info</CompactBadge>
                <CompactBadge variant="soft" size="sm">Soft</CompactBadge>
              </div>
              <p className="text-[10px] text-base-content/50">
                Bounce scale animation with 200ms spring easing
              </p>
            </div>
          </BentoItem>

          {/* Icon spin */}
          <BentoItem colSpan={4} hover>
            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Icon Spin</h3>
              <div className="flex gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center crud-icon-spin cursor-pointer">
                  <span className="ri-settings-3-line text-primary" />
                </div>
                <div className="w-10 h-10 rounded-xl bg-success/10 flex items-center justify-center crud-icon-spin cursor-pointer">
                  <span className="ri-refresh-line text-success" />
                </div>
                <div className="w-10 h-10 rounded-xl bg-info/10 flex items-center justify-center crud-icon-spin cursor-pointer">
                  <span className="ri-restart-line text-info" />
                </div>
              </div>
              <p className="text-[10px] text-base-content/50">
                90deg rotation on hover with 300ms fluid easing
              </p>
            </div>
          </BentoItem>
        </BentoGrid>
      </section>

      {/* ── Section 3: Staggered Entry ── */}
      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-base-content/50">
          Staggered Entry
        </h2>

        <div ref={scrollRef} className="scroll-reveal-stagger">
          <BentoGrid variant="dense" gap="md">
            {[
              { title: 'Item 1', color: 'primary' },
              { title: 'Item 2', color: 'success' },
              { title: 'Item 3', color: 'info' },
              { title: 'Item 4', color: 'warning' },
              { title: 'Item 5', color: 'error' },
              { title: 'Item 6', color: 'neutral' },
            ].map((item, idx) => (
              <BentoItem key={idx} hover>
                <BezelWidget
                  title={item.title}
                  value={`#${idx + 1}`}
                  color={item.color as any}
                  icon={<span className="ri-checkbox-circle-line" />}
                />
              </BentoItem>
            ))}
          </BentoGrid>
        </div>

        <p className="text-[10px] text-base-content/50">
          Items reveal with 75ms stagger delay using Intersection Observer
        </p>
      </section>

      {/* ── Section 4: Duration Tokens ── */}
      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-base-content/50">
          Duration Tokens
        </h2>

        <BentoGrid variant="standard" gap="sm">
          {[
            { name: 'Fast', duration: '100ms', class: 'duration-fast' },
            { name: 'Normal', duration: '200ms', class: 'duration-normal' },
            { name: 'Slow', duration: '300ms', class: 'duration-slow' },
            { name: 'Slower', duration: '500ms', class: 'duration-slower' },
            { name: 'Slowest', duration: '700ms', class: 'duration-slowest' },
          ].map((item, idx) => (
            <BentoItem key={idx} hover>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium">{item.name}</span>
                  <CompactBadge variant="soft" size="xs">{item.duration}</CompactBadge>
                </div>
                <div className={`h-2 bg-primary/20 rounded-full ${item.class} hover:bg-primary/60 cursor-pointer`} />
              </div>
            </BentoItem>
          ))}
        </BentoGrid>
      </section>
    </div>
  );
}
