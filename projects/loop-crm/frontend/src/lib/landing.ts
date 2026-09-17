// Landing page contract — GET /apis/pages/<slug>/ (Wagtail → JSON road).
// The Astro landing renders exclusively from this payload; when the backend
// is unreachable the pages show an explicit empty state, never hard-coded copy.

export interface ButtonData {
  label: string;
  href: string;
  style: string;
  page: { id: number; title: string; url: string } | null;
}

export interface HeroData {
  badge: string;
  title: string;
  accent: string;
  subtitle: string;
  primary_cta: ButtonData | null;
  secondary_cta: ButtonData | null;
  note: string;
}

export interface DnaItem {
  label: string;
  value: string;
}

export interface FeatureItem {
  icon: string;
  label: string;
  title: string;
  description: string;
  href: string;
  page: { id: number; title: string; url: string } | null;
}

export interface StepItem {
  number: string;
  title: string;
  copy: string;
}

export interface StatItem {
  value: string;
  suffix: string;
  label: string;
}

export interface PricingTier {
  name: string;
  description: string;
  price: string;
  period: string;
  features: string[];
  cta_label: string;
  cta_href: string;
  cta_page: { id: number; title: string; url: string } | null;
  featured: boolean;
}

export interface FaqItem {
  question: string;
  answer: string;
}

export interface CtaData {
  title: string;
  subtitle: string;
  primary_cta: ButtonData | null;
  secondary_cta: ButtonData | null;
}

export interface SectionHead {
  eyebrow: string;
  title: string;
  description: string;
}

export interface PagePayload {
  id: number;
  slug: string;
  title: string;
  type: string;
  show_in_nav: boolean;
  seo_title: string;
  search_description: string;
  hero?: HeroData;
  dna?: DnaItem[];
  features?: FeatureItem[];
  features_head?: SectionHead;
  steps?: StepItem[];
  steps_head?: SectionHead;
  stats?: StatItem[];
  stats_head?: SectionHead;
  pricing?: PricingTier[];
  pricing_head?: SectionHead;
  faq?: FaqItem[];
  faq_head?: SectionHead;
  cta?: CtaData;
  body?: string;
}

export interface PageResult {
  ok: boolean;
  page: PagePayload | null;
  error?: string;
}

// Use the same-origin proxy in every browser environment. The Astro dev proxy
// and production Traefik route `/apis/pages/` to Django; no localhost or
// alternate content source is allowed to silently replace Wagtail data.
const BACKEND_URL: string =
  ((import.meta.env as Record<string, unknown>).PUBLIC_BACKEND_URL as string | undefined ?? '').replace(/\/$/, '');

export async function fetchPage(slug: string, signal?: AbortSignal): Promise<PageResult> {
  try {
    const res = await fetch(`${BACKEND_URL}/apis/pages/${encodeURIComponent(slug)}/`, {
      signal,
      headers: { Accept: 'application/json' },
    });
    if (!res.ok) {
      return { ok: false, page: null, error: `API ${res.status}` };
    }
    const data = (await res.json()) as PagePayload;
    return { ok: true, page: data };
  } catch (err) {
    return {
      ok: false,
      page: null,
      error: err instanceof Error ? err.message : 'Backend unreachable',
    };
  }
}
