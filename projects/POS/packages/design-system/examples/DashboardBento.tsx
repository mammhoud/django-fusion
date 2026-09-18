/**
 * @formints/design-system — Dashboard Bento Example
 * 
 * Example dashboard layout using the asymmetric bento grid.
 * Demonstrates how to compose BentoGrid, BentoItem, and BezelWidget.
 */

import React from 'react';
import { BentoGrid, BentoItem, BentoSection, BezelWidget, CompactBadge } from '../src';

export default function DashboardBentoExample() {
  return (
    <div className="p-6 space-y-8">
      {/* ── Eyebrow Tag ── */}
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] font-medium bg-primary/10 text-primary">
          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
          Dashboard
        </span>
      </div>

      {/* ── KPI Section — Asymmetric Bento ── */}
      <BentoSection
        title="Live Dashboard"
        eyebrow="Real-time Metrics"
        accentColor="success"
      >
        <BentoGrid variant="asymmetric" gap="md">
          {/* Hero stat - spans 8 cols on desktop */}
          <BentoItem colSpan={8} accent="primary" accentBar>
            <BezelWidget
              title="Today's Revenue"
              value="$4,285"
              desc="+12.5% vs yesterday"
              icon={<span className="ri-money-dollar-box-line" />}
              color="primary"
            />
          </BentoItem>

          {/* Secondary stat - spans 4 cols */}
          <BentoItem colSpan={4} accent="success">
            <BezelWidget
              title="Orders"
              value="42"
              desc="8 pending"
              icon={<span className="ri-shopping-cart-line" />}
              color="success"
            />
          </BentoItem>

          {/* Third stat - spans 4 cols */}
          <BentoItem colSpan={4} accent="warning">
            <BezelWidget
              title="Open Tables"
              value="6"
              desc="3 reserved"
              icon={<span className="ri-table-line" />}
              color="warning"
            />
          </BentoItem>

          {/* Fourth stat - spans 4 cols */}
          <BentoItem colSpan={4} accent="info">
            <BezelWidget
              title="Staff On Duty"
              value="8"
              desc="2 on break"
              icon={<span className="ri-user-line" />}
              color="info"
            />
          </BentoItem>

          {/* Fifth stat - spans 4 cols */}
          <BentoItem colSpan={4} accent="error">
            <BezelWidget
              title="Low Stock Items"
              value="3"
              desc="Needs attention"
              icon={<span className="ri-alert-line" />}
              color="error"
            />
          </BentoItem>
        </BentoGrid>
      </BentoSection>

      {/* ── Quick Actions — Standard Grid ── */}
      <BentoSection
        title="Quick Actions"
        eyebrow="Common Tasks"
      >
        <BentoGrid variant="standard" gap="sm">
          <BentoItem hover>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-success/10 flex items-center justify-center">
                <span className="ri-shopping-cart-line text-success" />
              </div>
              <div>
                <p className="text-sm font-semibold">New Sale</p>
                <p className="text-[10px] text-base-content/50">Start a transaction</p>
              </div>
            </div>
          </BentoItem>

          <BentoItem hover>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-info/10 flex items-center justify-center">
                <span className="ri-box-line text-info" />
              </div>
              <div>
                <p className="text-sm font-semibold">Add Product</p>
                <p className="text-[10px] text-base-content/50">Create new item</p>
              </div>
            </div>
          </BentoItem>

          <BentoItem hover>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-secondary/10 flex items-center justify-center">
                <span className="ri-user-add-line text-secondary" />
              </div>
              <div>
                <p className="text-sm font-semibold">Add Employee</p>
                <p className="text-[10px] text-base-content/50">Register staff</p>
              </div>
            </div>
          </BentoItem>

          <BentoItem hover>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-warning/10 flex items-center justify-center">
                <span className="ri-file-chart-line text-warning" />
              </div>
              <div>
                <p className="text-sm font-semibold">View Reports</p>
                <p className="text-[10px] text-base-content/50">Sales analytics</p>
              </div>
            </div>
          </BentoItem>
        </BentoGrid>
      </BentoSection>

      {/* ── Recent Activity — Editorial Layout ── */}
      <BentoSection
        title="Recent Activity"
        eyebrow="Last 24 Hours"
        actions={
          <CompactBadge variant="soft" size="sm">
            View All
          </CompactBadge>
        }
      >
        <BentoGrid variant="editorial" gap="md">
          {/* Large activity card */}
          <BentoItem colSpan={8} hover>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Top Selling Items</h3>
                <CompactBadge variant="success" size="xs">Today</CompactBadge>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 rounded-lg bg-base-200/50">
                  <span className="text-xs">Classic Burger</span>
                  <span className="text-xs font-medium">24 sold</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-base-200/50">
                  <span className="text-xs">Caesar Salad</span>
                  <span className="text-xs font-medium">18 sold</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-base-200/50">
                  <span className="text-xs">Margherita Pizza</span>
                  <span className="text-xs font-medium">15 sold</span>
                </div>
              </div>
            </div>
          </BentoItem>

          {/* Side activity feed */}
          <BentoItem colSpan={4} hover>
            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Live Feed</h3>
              <div className="space-y-2">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-success mt-1.5" />
                  <div>
                    <p className="text-xs">Order #1234 completed</p>
                    <p className="text-[10px] text-base-content/50">2 min ago</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-info mt-1.5" />
                  <div>
                    <p className="text-xs">New reservation booked</p>
                    <p className="text-[10px] text-base-content/50">15 min ago</p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 rounded-full bg-warning mt-1.5" />
                  <div>
                    <p className="text-xs">Low stock alert: Tomatoes</p>
                    <p className="text-[10px] text-base-content/50">1 hour ago</p>
                  </div>
                </div>
              </div>
            </div>
          </BentoItem>
        </BentoGrid>
      </BentoSection>
    </div>
  );
}
