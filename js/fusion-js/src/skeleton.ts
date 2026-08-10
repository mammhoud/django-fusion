/**
 * FusionSkeletonBridge — consumes window.__FUSION_SKELETON_MANIFEST__
 * and renders skeleton placeholders for each component on the page.
 *
 * The manifest is embedded by the Django backend via
 * {% fusion_page_skeleton template_path="pages/home.html" %}.
 *
 * Usage::
 *
 *   import { FusionSkeletonBridge } from 'fusion-js/skeleton';
 *
 *   if (window.__FUSION_SKELETON_MANIFEST__) {
 *     const bridge = new FusionSkeletonBridge(
 *       window.__FUSION_SKELETON_MANIFEST__
 *     );
 *     bridge.renderAll();
 *     window.__fusionSkeletonBridge = bridge;
 *   }
 */

// ── types ─────────────────────────────────────────────────────────────

export interface SkeletonEntry {
  variant: string;
  component: string;
  order: number;
  props: Record<string, unknown>;
  skeletonConfig?: Record<string, unknown>;
}

export interface SkeletonManifest {
  skeletons: SkeletonEntry[];
}

// ── variant → BEM template ────────────────────────────────────────────

/** BEM class prefix shared with globals.css and Skeleton.astro. */
const B = 'fusion-skeleton';

/** Supported variants — mirrors the 16 variants in Skeleton.astro. */
const VARIANT_TEMPLATES: Record<string, (props: Record<string, unknown>) => string> = {
  'hero-section': (p) => `
    <div class="${B} ${B}--hero-section" aria-hidden="true" data-skeleton>
      <div class="${B}--hero-section__inner">
        <span class="${B}__line--tag" style="width:14rem"></span>
        <span class="${B}__line--hero"></span>
        <span class="${B}__line" style="width:60%"></span>
        <div class="${B}__cta-row">
          <span class="${B}__line--btn" style="width:10rem"></span>
          <span class="${B}__line--btn" style="width:9rem"></span>
        </div>
      </div>
    </div>`,

  'stats-row': (p) => `
    <div class="${B} ${B}--stats py-14" aria-hidden="true" data-skeleton>
      <div class="container-fusion">
        <div class="${B}--card grid-cols-2 md:grid-cols-4">
          ${repeat(p.count, '<span class="' + B + '__stat"></span>')}
        </div>
      </div>
    </div>`,

  'features-grid': (p) => `
    <div class="${B} ${B}--features py-14" aria-hidden="true" data-skeleton>
      <div class="container-fusion">
        <span class="${B}__line" style="width:30%;margin:0 auto 2rem"></span>
        <div class="${B}--card grid-cols-1 md:grid-cols-3 gap-6">
          ${repeat(p.count || 6,
            '<div class="' + B + '__feature"><span class="' + B + '__feature-icon"></span>'
            + '<span class="' + B + '__line" style="width:70%"></span>'
            + '<span class="' + B + '__line" style="width:90%"></span></div>'
          )}
        </div>
      </div>
    </div>`,

  'testimonial': () => `
    <div class="${B} ${B}--testimonial py-10" aria-hidden="true" data-skeleton>
      <span class="${B}__line" style="width:60%;margin:0 auto 1rem;height:1.5rem"></span>
      <span class="${B}__line" style="width:30%;margin:0 auto;height:0.75rem"></span>
    </div>`,

  'testimonials-carousel': (p) => `
    <div class="${B} ${B}--testimonials py-14" aria-hidden="true" data-skeleton>
      <div class="container-fusion">
        <div class="flex gap-6 justify-center">
          ${repeat(p.count || 3,
            '<div class="' + B + '__testimonial-card">'
            + '<span class="' + B + '__line" style="width:80%"></span>'
            + '<span class="' + B + '__line" style="width:50%"></span></div>'
          )}
        </div>
      </div>
    </div>`,

  'pricing-grid': (p) => `
    <div class="${B} ${B}--pricing py-14" aria-hidden="true" data-skeleton>
      <div class="container-fusion">
        <span class="${B}__line" style="width:20%;margin:0 auto 2rem"></span>
        <div class="grid-cols-1 md:grid-cols-3 gap-6">
          ${repeat(p.count || 3,
            '<div class="' + B + '__pricing-card">'
            + '<span class="' + B + '__line" style="width:50%"></span>'
            + '<span class="' + B + '__line--hero" style="width:60%"></span>'
            + '<span class="' + B + '__line" style="width:100%"></span></div>'
          )}
        </div>
      </div>
    </div>`,

  'faq-list': (p) => `
    <div class="${B} ${B}--faq py-10" aria-hidden="true" data-skeleton>
      ${repeat(p.count || 5,
        '<div class="' + B + '__faq-row">'
        + '<span class="' + B + '__line" style="width:80%"></span></div>'
      )}
    </div>`,

  'cta-banner': () => `
    <div class="${B} ${B}--cta py-12 text-center" aria-hidden="true" data-skeleton>
      <span class="${B}__line" style="width:40%;margin:0 auto 1rem"></span>
      <span class="${B}__line" style="width:25%;margin:0 auto"></span>
    </div>`,

  'contact-form': () => `
    <div class="${B} ${B}--contact py-10" aria-hidden="true" data-skeleton>
      ${repeat(4, '<span class="' + B + '__line--input"></span>')}
      <span class="' + B + '__line--btn" style="width:8rem"></span>
    </div>`,

  'timeline': (p) => `
    <div class="${B} ${B}--timeline py-10" aria-hidden="true" data-skeleton>
      ${repeat(p.count || 4,
        '<div class="' + B + '__timeline-dot"><span class="' + B + '__line" style="width:70%"></span></div>'
      )}
    </div>`,

  'team-grid': (p) => `
    <div class="${B} ${B}--team py-10" aria-hidden="true" data-skeleton>
      <div class="grid-cols-2 md:grid-cols-4 gap-6">
        ${repeat(p.count || 4,
          '<div class="text-center"><span class="' + B + '__avatar"></span>'
          + '<span class="' + B + '__line" style="width:50%;margin:0.5rem auto"></span></div>'
        )}
      </div>
    </div>`,

  'blog-grid': (p) => `
    <div class="${B} ${B}--blog py-10" aria-hidden="true" data-skeleton>
      <div class="grid-cols-1 md:grid-cols-3 gap-6">
        ${repeat(p.count || 3,
          '<div><span class="' + B + '__line" style="height:10rem"></span>'
          + '<span class="' + B + '__line" style="width:70%;margin-top:0.5rem"></span>'
          + '<span class="' + B + '__line" style="width:40%"></span></div>'
        )}
      </div>
    </div>`,

  'card': () => `
    <div class="${B} ${B}--card" aria-hidden="true" data-skeleton>
      <span class="${B}__line" style="height:8rem"></span>
      <span class="${B}__line" style="width:60%"></span>
      <span class="${B}__line" style="width:90%"></span>
    </div>`,

  'line': () => `<span class="${B}__line" aria-hidden="true" data-skeleton></span>`,
};

/** Fallback variant when no template is registered. */
function fallbackTemplate(): string {
  return `<span class="${B}__line" aria-hidden="true" data-skeleton></span>`;
}

// ── helpers ────────────────────────────────────────────────────────────

function repeat(count: unknown, html: string): string {
  const n = typeof count === 'number' ? Math.max(1, Math.round(count)) : 1;
  return Array.from({ length: n }, () => html).join('');
}

// ── skeleton bridge ─────────────────────────────────────────────────────

export class FusionSkeletonBridge {
  private entries: SkeletonEntry[];

  constructor(private manifest: SkeletonManifest) {
    this.entries = manifest.skeletons ?? [];
  }

  /**
   * Render skeleton placeholders for every component in the manifest.
   * Each skeleton is inserted as the first child of its target container.
   */
  renderAll(): void {
    for (const entry of this.entries) {
      const selector = `[data-fusion-skeleton="${entry.component}"]`;
      const target = document.querySelector(selector);
      if (target) {
        target.innerHTML = this.renderSkeleton(entry.variant, entry.props ?? {});
      }
    }
  }

  /**
   * Swap a skeleton placeholder with real content after an HTMX settle
   * or hydration event.
   */
  swap(componentPath: string, html: string): void {
    const el = document.querySelector(`[data-fusion-skeleton="${componentPath}"]`);
    if (el) {
      el.outerHTML = html;
    }
  }

  /** Return the raw entries for programmatic inspection. */
  getEntries(): SkeletonEntry[] {
    return this.entries;
  }

  // ── internal ──────────────────────────────────────────────────────

  private renderSkeleton(variant: string, props: Record<string, unknown>): string {
    const template = VARIANT_TEMPLATES[variant] ?? fallbackTemplate;
    try {
      return template(props);
    } catch {
      return fallbackTemplate();
    }
  }
}

// ── auto-init from embedded manifest ───────────────────────────────────

declare global {
  interface Window {
    __FUSION_SKELETON_MANIFEST__?: SkeletonManifest;
    __fusionSkeletonBridge?: FusionSkeletonBridge;
  }
}

if (typeof window !== 'undefined' && window.__FUSION_SKELETON_MANIFEST__) {
  const bridge = new FusionSkeletonBridge(window.__FUSION_SKELETON_MANIFEST__);
  bridge.renderAll();
  window.__fusionSkeletonBridge = bridge;
}
