import { useState } from 'react';
import { useTheme, THEME_VARIANTS, THEME_MAP, type ThemeVariant } from '../../contexts/ThemeContext';
import Card from '../layout/Card';

// ── Section wrapper ──
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="text-base font-bold text-base-content mb-3 flex items-center gap-2">
        <span className="w-1 h-4 rounded-full bg-primary" />
        {title}
      </h2>
      {children}
    </section>
  );
}

interface ThemePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ThemePreviewModal({ isOpen, onClose }: ThemePreviewModalProps) {
  const { mode } = useTheme();
  const [previewVariant, setPreviewVariant] = useState<ThemeVariant>('default');
  const [previewMode, setPreviewMode] = useState<'light' | 'dark'>(mode);
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['All Items', 'Beverages', 'Food', 'Specials'];

  const currentTheme = THEME_MAP[previewVariant]?.[previewMode] ?? 'light';

  if (!isOpen) return null;

  return (
    <dialog open className="modal modal-open">
      <div className="modal-box w-11/12 max-w-6xl max-h-[90vh] overflow-y-auto" data-theme={currentTheme}>
        {/* Header */}
        <div className="flex items-center justify-between mb-6 sticky top-0 z-10 bg-base-100/95 backdrop-blur-sm py-3 -mx-1 px-1 border-b border-base-300/50">
          <div className="flex items-center gap-3">
            <span className="icon-[tabler--palette] w-6 h-6 text-primary" />
            <div>
              <h3 className="font-bold text-lg">Theme Component Preview</h3>
              <p className="text-xs text-base-content/50">
                Preview all components across every theme variant
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            {/* Variant selector */}
            <div className="flex items-center gap-1 bg-base-300/50 rounded-lg p-0.5">
              {THEME_VARIANTS.map(v => (
                <button
                  key={v.id}
                  type="button"
                  onClick={() => setPreviewVariant(v.id)}
                  className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                    previewVariant === v.id
                      ? 'bg-base-100 text-base-content shadow-sm'
                      : 'text-base-content/50 hover:text-base-content'
                  }`}
                >
                  <span className={`icon-[${v.icon}] w-3.5 h-3.5 mr-1`} />
                  {v.label}
                </button>
              ))}
            </div>
            {/* Mode toggle */}
            <div className="flex items-center gap-1 bg-base-300/50 rounded-lg p-0.5">
              <button
                type="button"
                onClick={() => setPreviewMode('light')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                  previewMode === 'light'
                    ? 'bg-base-100 text-base-content shadow-sm'
                    : 'text-base-content/50 hover:text-base-content'
                }`}
              >
                <span className="icon-[tabler--sun] w-3.5 h-3.5" /> Light
              </button>
              <button
                type="button"
                onClick={() => setPreviewMode('dark')}
                className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                  previewMode === 'dark'
                    ? 'bg-base-100 text-base-content shadow-sm'
                    : 'text-base-content/50 hover:text-base-content'
                }`}
              >
                <span className="icon-[tabler--moon] w-3.5 h-3.5" /> Dark
              </button>
            </div>
            {/* Theme badge */}
            <span className="badge badge-soft badge-primary text-xs font-mono">{currentTheme}</span>
            {/* Close */}
            <button onClick={onClose} className="btn btn-ghost btn-sm btn-square ml-2">
              <span className="icon-[tabler--x] w-4 h-4" />
            </button>
          </div>
        </div>

        {/* ── Buttons ── */}
        <Section title="Buttons">
          <Card className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Semantic Variants</p>
              <div className="flex flex-wrap gap-2">
                <button type="button" className="btn btn-primary">Primary</button>
                <button type="button" className="btn btn-secondary">Secondary</button>
                <button type="button" className="btn btn-accent">Accent</button>
                <button type="button" className="btn btn-info">Info</button>
                <button type="button" className="btn btn-success">Success</button>
                <button type="button" className="btn btn-warning">Warning</button>
                <button type="button" className="btn btn-error">Error</button>
                <button type="button" className="btn btn-neutral">Neutral</button>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Soft &amp; Outline</p>
              <div className="flex flex-wrap gap-2">
                <button type="button" className="btn btn-soft btn-primary">Soft</button>
                <button type="button" className="btn btn-outline btn-primary">Outline</button>
                <button type="button" className="btn btn-ghost">Ghost</button>
                <button type="button" className="btn btn-dash">Dash</button>
                <button type="button" className="btn btn-primary" disabled>Disabled</button>
                <button type="button" className="btn btn-primary btn-glass">Glass</button>
              </div>
            </div>
          </Card>
        </Section>

        {/* ── Forms ── */}
        <Section title="Form Controls">
          <Card>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="label"><span className="label-text">Text Input</span></label>
                <input type="text" className="input input-bordered w-full" placeholder="Sample" defaultValue="Editable" />
              </div>
              <div>
                <label className="label"><span className="label-text">Select</span></label>
                <select className="select select-bordered w-full">
                  <option>Option 1</option>
                  <option>Option 2</option>
                </select>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <label className="flex items-center gap-2"><input type="checkbox" className="checkbox checkbox-primary" defaultChecked /><span className="text-sm">Checkbox</span></label>
              <label className="flex items-center gap-2"><input type="radio" name="preview-radio" className="radio radio-primary" defaultChecked /><span className="text-sm">Radio</span></label>
              <label className="flex items-center gap-2"><span className="text-sm">Toggle</span><input type="checkbox" className="toggle toggle-primary" defaultChecked /></label>
            </div>
          </Card>
        </Section>

        {/* ── Alerts ── */}
        <Section title="Alerts">
          <div className="space-y-2">
            <div role="alert" className="alert alert-info"><span className="icon-[tabler--info-circle] w-5 h-5" /><span>Info alert — general information</span></div>
            <div role="alert" className="alert alert-success"><span className="icon-[tabler--check] w-5 h-5" /><span>Success — operation completed</span></div>
            <div role="alert" className="alert alert-warning"><span className="icon-[tabler--alert-triangle] w-5 h-5" /><span>Warning — please review</span></div>
            <div role="alert" className="alert alert-error"><span className="icon-[tabler--alert-circle] w-5 h-5" /><span>Error — something went wrong</span></div>
          </div>
        </Section>

        {/* ── Tabs ── */}
        <Section title="Tabs">
          <Card>
            <div className="tabs tabs-boxed gap-1 mb-3" role="tablist">
              {tabs.map((tab, i) => (
                <button key={tab} type="button" role="tab" className={`tab ${i === activeTab ? 'tab-active' : ''}`} onClick={() => setActiveTab(i)}>{tab}</button>
              ))}
            </div>
            <div className="tabs tabs-lifted" role="tablist">
              {tabs.map((tab, i) => (
                <button key={tab} type="button" role="tab" className={`tab ${i === activeTab ? 'tab-active' : ''}`} onClick={() => setActiveTab(i)}>{tab}</button>
              ))}
            </div>
          </Card>
        </Section>

        {/* ── Stats ── */}
        <Section title="Stats">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="stat"><div className="stat-title">Revenue</div><div className="stat-value text-primary">$12,450</div><div className="stat-desc"><span className="text-success">▲ 12.5%</span> vs last month</div></div>
            <div className="stat"><div className="stat-title">Orders</div><div className="stat-value text-secondary">84</div><div className="stat-desc"><span className="text-success">▲ 8.3%</span> vs yesterday</div></div>
            <div className="stat"><div className="stat-title">Avg Order</div><div className="stat-value text-accent">$24.50</div><div className="stat-desc"><span className="text-warning">→ 0.0%</span> unchanged</div></div>
            <div className="stat"><div className="stat-title">Tables</div><div className="stat-value text-info">12</div><div className="stat-desc"><span className="text-error">▼ 2</span> from peak</div></div>
          </div>
        </Section>

        {/* ── Badges ── */}
        <Section title="Badges">
          <div className="flex flex-wrap gap-2">
            <span className="badge badge-primary">Primary</span>
            <span className="badge badge-soft badge-secondary">Soft</span>
            <span className="badge badge-outline badge-accent">Outline</span>
            <span className="badge badge-success">Success</span>
            <span className="badge badge-warning">Warning</span>
            <span className="badge badge-error">Error</span>
            <span className="badge badge-neutral">Neutral</span>
          </div>
        </Section>

        {/* ── Progress ── */}
        <Section title="Progress &amp; Loading">
          <div className="space-y-3">
            <progress className="progress progress-primary w-full" value={70} max={100} />
            <progress className="progress progress-success w-full" value={45} max={100} />
            <progress className="progress progress-error w-full" value={20} max={100} />
          </div>
          <div className="flex flex-wrap items-center gap-3 mt-3">
            <span className="loading loading-spinner loading-sm text-primary" />
            <span className="loading loading-spinner loading-md text-secondary" />
            <span className="loading loading-dots loading-md text-accent" />
            <span className="loading loading-ring loading-md text-info" />
          </div>
        </Section>

        {/* ── Cards ── */}
        <Section title="Cards">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <h3 className="card-title">Simple Card</h3>
              <p className="text-sm text-base-content/70">Basic card with title and content.</p>
              <div className="card-actions mt-3">
                <button type="button" className="btn btn-primary btn-sm">Action</button>
              </div>
            </Card>
            <Card padding="lg">
              <h3 className="card-title">Large Padding</h3>
              <p className="text-sm text-base-content/70">More breathing room.</p>
              <div className="card-actions mt-3">
                <button type="button" className="btn btn-soft btn-info btn-sm">Learn More</button>
              </div>
            </Card>
            <Card border="base-200">
              <h3 className="card-title text-primary">Bordered Card</h3>
              <p className="text-sm text-base-content/70">With accent border.</p>
              <div className="card-actions mt-3">
                <span className="badge badge-primary">Featured</span>
              </div>
            </Card>
          </div>
        </Section>

        {/* ── Table ── */}
        <Section title="Table">
          <Card className="overflow-hidden p-0">
            <table className="table w-full">
              <thead>
                <tr><th>Name</th><th>Category</th><th>Price</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr><td className="font-medium">Classic Burger</td><td>Burgers</td><td>$12.99</td><td><span className="badge badge-success badge-sm">Active</span></td></tr>
                <tr><td className="font-medium">Margherita Pizza</td><td>Pizza</td><td>$15.50</td><td><span className="badge badge-success badge-sm">Active</span></td></tr>
                <tr><td className="font-medium">Caesar Salad</td><td>Salads</td><td>$9.99</td><td><span className="badge badge-warning badge-sm">Seasonal</span></td></tr>
              </tbody>
            </table>
          </Card>
        </Section>

        {/* Footer */}
        <div className="text-center py-3 mt-4 border-t border-base-300/50">
          <p className="text-xs text-base-content/40">
            All components rendered using <span className="font-semibold text-base-content/60">{currentTheme}</span> via <code className="text-primary font-mono text-xs">data-theme</code> attribute.
          </p>
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button type="button" onClick={onClose}>close</button>
      </form>
    </dialog>
  );
}
