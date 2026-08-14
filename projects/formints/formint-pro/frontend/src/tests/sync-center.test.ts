import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

const root = dirname(fileURLToPath(import.meta.url));
const read = (p: string) => readFileSync(join(root, '..', p), 'utf8');

describe('Sync Center page — transport + components + wizard', () => {
  const page = read('pages/ops/sync/index.astro');

  it('imports the reusable FusionTable, FusionForm and WizardForm components', () => {
    expect(page).toContain("import FusionTable from '../../../components/ui/FusionTable.astro';");
    expect(page).toContain("import FusionForm from '../../../components/ui/FusionForm.astro';");
    expect(page).toContain("import WizardForm from '../../../components/ui/WizardForm.astro';");
  });

  it('loads product catalog from the Components API', () => {
    expect(page).toContain('resource="products"');
  });

  it('declares a three-step supplier onboarding wizard', () => {
    expect(page).toContain("{ title: 'Supplier', description: 'Business details' }");
    expect(page).toContain("{ title: 'Catalog', description: 'First products' }");
    expect(page).toContain("{ title: 'Review', description: 'Confirm & sync' }");
    expect(page).toContain('slot="step-0"');
    expect(page).toContain('slot="step-1"');
    expect(page).toContain('slot="step-2"');
  });

  it('reports transport status (api/invoke/snapshot)', () => {
    expect(page).toContain("transportStatus");
    expect(page).toContain('Live API');
    expect(page).toContain('Offline snapshot');
  });
});

describe('FusionTable component contract', () => {
  const component = read('components/ui/FusionTable.astro');

  it('is data-driven from the server Components API', () => {
    expect(component).toContain("import('../../lib/fusion-api')");
    expect(component).toContain('fusionTable(this.resource');
  });

  it('renders skeleton rows while loading', () => {
    expect(component).toContain('fusion-skeleton--table');
    expect(component).toContain('x-show="loading"');
  });

  it('supports client-side pagination and search', () => {
    expect(component).toContain('pagedRows');
    expect(component).toContain('filteredRows');
  });
});

describe('FusionForm component contract', () => {
  const component = read('components/ui/FusionForm.astro');

  it('renders fields from the server form schema', () => {
    expect(component).toContain("import('../../lib/fusion-api')");
    expect(component).toContain('fieldType(name)');
    expect(component).toContain('fieldChoices(name)');
  });

  it('performs per-field validation', () => {
    expect(component).toContain('validate()');
    expect(component).toContain('is required');
  });
});

describe('WizardForm component contract', () => {
  const component = read('components/ui/WizardForm.astro');

  it('declares a progress rail and progress bar', () => {
    expect(component).toContain('wizard__rail');
    expect(component).toContain('wizard__progress-bar');
  });

  it('supports next/back/finish with per-step validation', () => {
    expect(component).toContain('goNext()');
    expect(component).toContain('goBack()');
    expect(component).toContain('validateStep');
  });

  it('animates with cubic-bezier (no linear/ease-in-out)', () => {
    expect(component).toContain('cubic-bezier(0.32, 0.72, 0, 1)');
    expect(component).not.toContain('ease-in-out');
  });
});

describe('Skeleton component — wizard-step variant', () => {
  const component = read('components/ui/Skeleton.astro');

  it('supports the wizard-step variant', () => {
    expect(component).toContain("variant === 'wizard-step'");
    expect(component).toContain('fusion-skeleton--wizard');
  });
});

describe('Layout transport wiring', () => {
  const layout = read('layouts/Layout.astro');

  it('registers the unified API transport as an Alpine store', () => {
    expect(layout).toContain("import * as api from '../lib/fusion-api';");
    expect(layout).toContain("Alpine.store('api', api);");
  });

  it('fetches navigation through the transport (not raw fetch)', () => {
    expect(layout).toContain('api.fusionNavigation()');
    expect(layout).not.toContain("fetch('/api/v1/navigation/')");
  });

  it('keeps the fallback nav for offline mode', () => {
    expect(layout).toContain('Sync Center');
  });
});

describe('fusion-api transport lib', () => {
  const lib = read('lib/fusion-api.ts');

  it('defines the three-tier fallback (api → invoke → snapshot)', () => {
    expect(lib).toContain("source: 'api' | 'invoke' | 'snapshot'");
    expect(lib).toContain('startServer()');
    expect(lib).toContain('readSnapshot');
  });

  it('exposes typed helpers for health, stats, components, sync', () => {
    expect(lib).toContain('export async function fusionHealth()');
    expect(lib).toContain('export async function fusionComponents()');
    expect(lib).toContain('export async function syncStatus()');
    expect(lib).toContain('export async function syncPushProducts(');
  });

  it('surfaces the Tauri bridge and native capabilities', () => {
    expect(lib).toContain('isTauri()');
    expect(lib).toContain('nativeCapabilities()');
    expect(lib).toContain('formint_server_status');
  });
});
