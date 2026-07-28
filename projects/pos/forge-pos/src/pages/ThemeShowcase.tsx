import { useState } from 'react';
import PageLayout from '../components/PageLayout';
import { useTheme, THEME_VARIANTS, THEME_MAP, type ThemeVariant } from '../contexts/ThemeContext';
import Card from '../components/Card';

// ── Section wrapper ──
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <h2 className="text-lg font-bold text-base-content mb-4 flex items-center gap-2">
        <span className="w-1 h-5 rounded-full bg-primary" />
        {title}
      </h2>
      {children}
    </section>
  );
}

export default function ThemeShowcase() {
  const { mode } = useTheme();
  const [previewVariant, setPreviewVariant] = useState<ThemeVariant>('default');
  const [previewMode, setPreviewMode] = useState<'light' | 'dark'>(mode);
  const [activeTab, setActiveTab] = useState(0);
  const tabs = ['All Items', 'Beverages', 'Food', 'Specials'];

  const currentTheme = THEME_MAP[previewVariant]?.[previewMode] ?? 'light';

  return (
    <PageLayout
      title="Theme Component Showcase"
      background="bg-base-200/50"
      padding="py-8"
    >
      <div className="max-w-5xl mx-auto" data-theme={currentTheme}>
        {/* ── Theme Switcher ── */}
        <Card className="mb-8 sticky top-0 z-50 shadow-lg border border-base-300" padding="md">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="icon-[tabler--palette] w-6 h-6 text-primary" />
              <div>
                <h1 className="text-xl font-bold text-base-content">Theme Component Showcase</h1>
                <p className="text-sm text-base-content/60">
                  Preview all migrated FlyonUI components across every theme variant
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
                    {v.icon} {v.label}
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
            </div>
          </div>
        </Card>

        {/* ── 1. Buttons ── */}
        <Section title="Buttons">
          <Card className="space-y-6">
            {/* Semantic variants */}
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

            {/* Soft variants */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Soft Variants</p>
              <div className="flex flex-wrap gap-2">
                <button type="button" className="btn btn-soft btn-primary">Primary</button>
                <button type="button" className="btn btn-soft btn-secondary">Secondary</button>
                <button type="button" className="btn btn-soft btn-accent">Accent</button>
                <button type="button" className="btn btn-soft btn-info">Info</button>
                <button type="button" className="btn btn-soft btn-success">Success</button>
                <button type="button" className="btn btn-soft btn-warning">Warning</button>
                <button type="button" className="btn btn-soft btn-error">Error</button>
              </div>
            </div>

            {/* Outline + Ghost */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Outline &amp; Ghost</p>
              <div className="flex flex-wrap gap-2">
                <button type="button" className="btn btn-outline btn-primary">Outline</button>
                <button type="button" className="btn btn-ghost">Ghost</button>
                <button type="button" className="btn btn-link">Link</button>
                <button type="button" className="btn btn-dash">Dash</button>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Sizes</p>
              <div className="flex flex-wrap items-center gap-2">
                <button type="button" className="btn btn-xs btn-primary">XS</button>
                <button type="button" className="btn btn-sm btn-primary">SM</button>
                <button type="button" className="btn btn-md btn-primary">MD</button>
                <button type="button" className="btn btn-lg btn-primary">LG</button>
                <button type="button" className="btn btn-xl btn-primary">XL</button>
              </div>
            </div>

            {/* States */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">States</p>
              <div className="flex flex-wrap gap-2">
                <button type="button" className="btn btn-primary" disabled>Disabled</button>
                <button type="button" className="btn btn-primary btn-active">Active</button>
                <button type="button" className="btn btn-primary btn-glass">Glass</button>
                <button type="button" className="btn btn-primary btn-wide">Wide</button>
                <button type="button" className="btn btn-circle btn-primary" aria-label="Circle button">
                  <span className="icon-[tabler--check] w-5 h-5" />
                </button>
                <button type="button" className="btn btn-square btn-primary" aria-label="Square button">
                  <span className="icon-[tabler--menu-2] w-5 h-5" />
                </button>
              </div>
            </div>
          </Card>
        </Section>

        {/* ── 2. Inputs & Form Controls ── */}
        <Section title="Form Controls">
          <Card className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="label"><span className="label-text">Text Input</span></label>
                <input type="text" className="input input-bordered w-full" placeholder="Placeholder" defaultValue="Sample text" />
              </div>
              <div>
                <label className="label"><span className="label-text">Number Input</span></label>
                <input type="number" className="input input-bordered w-full" placeholder="0" defaultValue="42" />
              </div>
              <div>
                <label className="label"><span className="label-text">Select</span></label>
                <select className="select select-bordered w-full">
                  <option>Option 1</option>
                  <option>Option 2</option>
                  <option>Option 3</option>
                </select>
              </div>
              <div>
                <label className="label"><span className="label-text">Textarea</span></label>
                <textarea className="textarea textarea-bordered w-full" rows={2} placeholder="Write something..." defaultValue="Sample text content" />
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Input States</p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="label"><span className="label-text">Success</span></label>
                  <input type="text" className="input input-bordered w-full input-success" defaultValue="Valid input" />
                </div>
                <div>
                  <label className="label"><span className="label-text">Warning</span></label>
                  <input type="text" className="input input-bordered w-full input-warning" defaultValue="Check this" />
                </div>
                <div>
                  <label className="label"><span className="label-text">Error</span></label>
                  <input type="text" className="input input-bordered w-full input-error" defaultValue="Invalid value" />
                </div>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Checkbox, Radio &amp; Toggle</p>
              <div className="flex flex-wrap items-center gap-6">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="checkbox checkbox-primary" defaultChecked />
                  <span className="text-sm">Checkbox</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="checkbox checkbox-secondary" />
                  <span className="text-sm">Unchecked</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="radio" name="radio-demo" className="radio radio-primary" defaultChecked />
                  <span className="text-sm">Radio 1</span>
                </label>
                <label className="flex items-center gap-2">
                  <input type="radio" name="radio-demo" className="radio radio-primary" />
                  <span className="text-sm">Radio 2</span>
                </label>
                <label className="flex items-center gap-2">
                  <span className="text-sm">Toggle</span>
                  <input type="checkbox" className="toggle toggle-primary" defaultChecked />
                </label>
                <label className="flex items-center gap-2">
                  <span className="text-sm">Toggle off</span>
                  <input type="checkbox" className="toggle toggle-primary" />
                </label>
              </div>
            </div>
          </Card>
        </Section>

        {/* ── 3. Alerts ── */}
        <Section title="Alerts">
          <Card className="space-y-3">
            <div role="alert" className="alert alert-info">
              <span className="icon-[tabler--info-circle] w-5 h-5" />
              <span>Info alert — general information message</span>
            </div>
            <div role="alert" className="alert alert-success">
              <span className="icon-[tabler--check] w-5 h-5" />
              <span>Success alert — operation completed</span>
            </div>
            <div role="alert" className="alert alert-warning">
              <span className="icon-[tabler--alert-triangle] w-5 h-5" />
              <span>Warning alert — please review this</span>
            </div>
            <div role="alert" className="alert alert-error">
              <span className="icon-[tabler--alert-circle] w-5 h-5" />
              <span>Error alert — something went wrong</span>
            </div>
            <div role="alert" className="alert alert-neutral">
              <span className="icon-[tabler--bell] w-5 h-5" />
              <span>Neutral alert — system notification</span>
            </div>
          </Card>
        </Section>

        {/* ── 4. Tabs ── */}
        <Section title="Tabs">
          <Card className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Tabs Boxed</p>
              <div className="tabs tabs-boxed gap-1" role="tablist">
                {tabs.map((tab, i) => (
                  <button
                    key={tab}
                    type="button"
                    role="tab"
                    className={`tab ${i === activeTab ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab(i)}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Tabs Lifted</p>
              <div className="tabs tabs-lifted" role="tablist">
                {tabs.map((tab, i) => (
                  <button
                    key={tab}
                    type="button"
                    role="tab"
                    className={`tab ${i === activeTab ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab(i)}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Tabs Bordered</p>
              <div className="tabs tabs-bordered" role="tablist">
                {tabs.map((tab, i) => (
                  <button
                    key={tab}
                    type="button"
                    role="tab"
                    className={`tab ${i === activeTab ? 'tab-active' : ''}`}
                    onClick={() => setActiveTab(i)}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>
          </Card>
        </Section>

        {/* ── 5. Stats ── */}
        <Section title="Stats">
          <Card>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="stat">
                <div className="stat-title">Total Revenue</div>
                <div className="stat-value text-primary">$12,450</div>
                <div className="stat-desc">
                  <span className="text-success">▲ 12.5%</span> vs last month
                </div>
              </div>
              <div className="stat">
                <div className="stat-title">Orders Today</div>
                <div className="stat-value text-secondary">84</div>
                <div className="stat-desc">
                  <span className="text-success">▲ 8.3%</span> vs yesterday
                </div>
              </div>
              <div className="stat">
                <div className="stat-title">Avg Order Value</div>
                <div className="stat-value text-accent">$24.50</div>
                <div className="stat-desc">
                  <span className="text-warning">→ 0.0%</span> unchanged
                </div>
              </div>
              <div className="stat">
                <div className="stat-title">Active Tables</div>
                <div className="stat-value text-info">12</div>
                <div className="stat-desc">
                  <span className="text-error">▼ 2</span> from peak hour
                </div>
              </div>
            </div>
          </Card>
        </Section>

        {/* ── 6. Badges ── */}
        <Section title="Badges">
          <Card className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Semantic Badges</p>
              <div className="flex flex-wrap gap-2">
                <span className="badge badge-primary">Primary</span>
                <span className="badge badge-secondary">Secondary</span>
                <span className="badge badge-accent">Accent</span>
                <span className="badge badge-info">Info</span>
                <span className="badge badge-success">Success</span>
                <span className="badge badge-warning">Warning</span>
                <span className="badge badge-error">Error</span>
                <span className="badge badge-neutral">Neutral</span>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Soft Badges</p>
              <div className="flex flex-wrap gap-2">
                <span className="badge badge-soft badge-primary">Primary</span>
                <span className="badge badge-soft badge-secondary">Secondary</span>
                <span className="badge badge-soft badge-accent">Accent</span>
                <span className="badge badge-soft badge-info">Info</span>
                <span className="badge badge-soft badge-success">Success</span>
                <span className="badge badge-soft badge-warning">Warning</span>
                <span className="badge badge-soft badge-error">Error</span>
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Sizes &amp; Outlines</p>
              <div className="flex flex-wrap items-center gap-2">
                <span className="badge badge-xs badge-primary">XS</span>
                <span className="badge badge-sm badge-primary">SM</span>
                <span className="badge badge-md badge-primary">MD</span>
                <span className="badge badge-lg badge-primary">LG</span>
                <span className="badge badge-outline badge-primary">Outline</span>
                <span className="badge badge-dash badge-primary">Dash</span>
                <span className="badge badge-soft badge-primary gap-1">
                  <span className="icon-[tabler--check] w-3 h-3" /> With Icon
                </span>
              </div>
            </div>
          </Card>
        </Section>

        {/* ── 7. Cards ── */}
        <Section title="Cards">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <h3 className="card-title">Simple Card</h3>
              <p className="text-sm text-base-content/70">Basic card with title and body content. No padding customization.</p>
              <div className="card-actions mt-3">
                <button type="button" className="btn btn-primary btn-sm">Action</button>
              </div>
            </Card>
            <Card padding="lg">
              <h3 className="card-title">Large Padding</h3>
              <p className="text-sm text-base-content/70">Card with extra padding for more breathing room.</p>
              <div className="card-actions mt-3">
                <button type="button" className="btn btn-soft btn-info btn-sm">Learn More</button>
              </div>
            </Card>
            <Card border="base-200">
              <h3 className="card-title text-primary">Bordered Card</h3>
              <p className="text-sm text-base-content/70">Card with a primary border accent.</p>
              <div className="card-actions mt-3">
                <span className="badge badge-primary">Featured</span>
              </div>
            </Card>
          </div>
        </Section>

        {/* ── 8. Tables ── */}
        <Section title="Tables">
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="table w-full">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="font-medium">Classic Burger</td>
                    <td>Burgers</td>
                    <td>$12.99</td>
                    <td><span className="badge badge-success badge-sm">Active</span></td>
                  </tr>
                  <tr>
                    <td className="font-medium">Margherita Pizza</td>
                    <td>Pizza</td>
                    <td>$15.50</td>
                    <td><span className="badge badge-success badge-sm">Active</span></td>
                  </tr>
                  <tr>
                    <td className="font-medium">Caesar Salad</td>
                    <td>Salads</td>
                    <td>$9.99</td>
                    <td><span className="badge badge-warning badge-sm">Seasonal</span></td>
                  </tr>
                  <tr>
                    <td className="font-medium">New Item</td>
                    <td>Specials</td>
                    <td>$0.00</td>
                    <td><span className="badge badge-error badge-sm">Inactive</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>
        </Section>

        {/* ── 9. Progress & Loading ── */}
        <Section title="Progress &amp; Loading">
          <Card className="space-y-4">
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Progress Bars</p>
              <div className="space-y-3">
                <progress className="progress progress-primary w-full" value={70} max={100} />
                <progress className="progress progress-secondary w-full" value={45} max={100} />
                <progress className="progress progress-accent w-full" value={90} max={100} />
                <progress className="progress progress-success w-full" value={60} max={100} />
                <progress className="progress progress-warning w-full" value={30} max={100} />
                <progress className="progress progress-error w-full" value={15} max={100} />
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Loading Spinners</p>
              <div className="flex flex-wrap items-center gap-4">
                <span className="loading loading-spinner loading-xs text-primary" />
                <span className="loading loading-spinner loading-sm text-secondary" />
                <span className="loading loading-spinner loading-md text-accent" />
                <span className="loading loading-spinner loading-lg text-info" />
                <span className="loading loading-dots loading-md text-success" />
                <span className="loading loading-ring loading-md text-warning" />
                <span className="loading loading-infinity loading-md text-error" />
              </div>
            </div>
          </Card>
        </Section>

        {/* ── 10. Modal ── */}
        <Section title="Modals">
          <Card>
            <p className="text-sm text-base-content/70 mb-4">
              Click the button below to open a theme-aware modal dialog.
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => (document.getElementById('showcase-modal') as HTMLDialogElement)?.showModal()}
            >
              <span className="icon-[tabler--window] w-4 h-4" /> Open Modal
            </button>
            <dialog id="showcase-modal" className="modal">
              <div className="modal-box">
                <h3 className="font-bold text-lg">Theme-Aware Modal</h3>
                <p className="py-4 text-sm text-base-content/70">
                  This modal inherits the current preview theme via the <code className="text-primary font-mono text-xs">data-theme</code> attribute.
                  All semantic colors (primary, secondary, accent) adapt to the selected theme.
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="badge badge-primary">Theme</span>
                  <span className="badge badge-secondary">Adaptive</span>
                  <span className="badge badge-accent">FlyonUI</span>
                </div>
                <div className="modal-action">
                  <form method="dialog">
                    <button type="submit" className="btn btn-primary">Close</button>
                  </form>
                </div>
              </div>
              <form method="dialog" className="modal-backdrop">
                <button type="submit">close</button>
              </form>
            </dialog>
          </Card>
        </Section>

        {/* ── 11. Misc ── */}
        <Section title="Additional Components">
          <Card className="space-y-6">
            {/* KBD */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Keyboard Keys</p>
              <div className="flex flex-wrap gap-1 items-center">
                <kbd className="kbd">Ctrl</kbd>
                <span className="text-base-content/40">+</span>
                <kbd className="kbd">Shift</kbd>
                <span className="text-base-content/40">+</span>
                <kbd className="kbd">S</kbd>
              </div>
            </div>

            {/* Collapse / Accordion */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Collapse (Accordion)</p>
              <div className="join join-vertical w-full">
                <div className="collapse collapse-arrow join-item border-base-300 border">
                  <input type="radio" name="showcase-accordion" defaultChecked />
                  <div className="collapse-title text-sm font-semibold">What is Forge POS?</div>
                  <div className="collapse-content text-sm text-base-content/70">
                    Forge POS is a lightweight, offline-first Point of Sale desktop application.
                  </div>
                </div>
                <div className="collapse collapse-arrow join-item border-base-300 border">
                  <input type="radio" name="showcase-accordion" />
                  <div className="collapse-title text-sm font-semibold">Features</div>
                  <div className="collapse-content text-sm text-base-content/70">
                    Inventory management, employee scheduling, sales reporting, and more.
                  </div>
                </div>
                <div className="collapse collapse-arrow join-item border-base-300 border">
                  <input type="radio" name="showcase-accordion" />
                  <div className="collapse-title text-sm font-semibold">Pricing</div>
                  <div className="collapse-content text-sm text-base-content/70">
                    Free and open-source. No subscription required.
                  </div>
                </div>
              </div>
            </div>

            {/* Indicator */}
            <div>
              <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-3">Indicator / Badge on Element</p>
              <div className="flex flex-wrap gap-6">
                <div className="indicator">
                  <span className="indicator-item badge badge-primary badge-xs" />
                  <button type="button" className="btn btn-ghost btn-square">
                    <span className="icon-[tabler--bell] w-5 h-5" />
                  </button>
                </div>
                <div className="indicator">
                  <span className="indicator-item badge badge-error badge-sm">3</span>
                  <button type="button" className="btn btn-ghost btn-square">
                    <span className="icon-[tabler--shopping-cart] w-5 h-5" />
                  </button>
                </div>
                <div className="indicator">
                  <span className="indicator-item badge badge-success badge-xs" />
                  <div className="avatar placeholder">
                    <div className="w-10 rounded-full bg-primary text-primary-content flex items-center justify-center text-sm font-semibold">
                      JD
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </Section>

        {/* Footer */}
        <Card className="text-center py-4" border="base-200">
          <p className="text-sm text-base-content/50">
            All components are rendered using <span className="font-semibold text-base-content">{currentTheme}</span> theme via <code className="text-primary font-mono text-xs">data-theme</code> attribute.
          </p>
        </Card>
      </div>
    </PageLayout>
  );
}
