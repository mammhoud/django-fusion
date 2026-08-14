/**
 * Formint Café — django-fusion site contract client.
 *
 * The backend exposes /fusion/navigation/, /fusion/branding/ and
 * /fusion/assets/ (see backend/shop/fusion.py). The storefront consumes them
 * so the header/footer branding and versions stay in sync with the Django
 * site config instead of hardcoded copies. Build-time fetches fall back to
 * the static site config when the backend is offline (astro build never
 * blocks); the Alpine shell re-fetches live in the browser.
 */
import { API_BASE, SHOP_NAME, SHOP_TAGLINE } from './site';

export interface FusionNavRoute {
  label: string;
  href: string;
  icon?: string;
  active?: boolean;
}

export interface FusionNavModule {
  id: string;
  label: string;
  icon?: string;
  active?: boolean;
  routes: FusionNavRoute[];
}

export interface FusionNavigation {
  brand: { label: string; href: string; tag: string };
  modules: FusionNavModule[];
}

export interface FusionBranding {
  site: { name: string; tagline: string; language: string };
  palette: Record<string, string>;
}

export interface FusionAssets {
  version: string;
  static_url: string;
  fusion_render_first: boolean;
  enabled: boolean;
  webpack_enabled: boolean;
  webpack_bundle_dir: string;
  top: Record<string, unknown>;
  bottom: Record<string, unknown>;
  fonts: string[];
  preconnect: string[];
}

/** One craft accordion panel (the roast / the kitchen / the pickup). */
export interface CraftPanel {
  title: string;
  caption: string;
  body: string;
  img: string;
  alt: string;
}

/** One testimonial voice. */
export interface EditorialVoice {
  name: string;
  role: string;
  quote: string;
  img: string;
}

export interface FusionEditorial {
  craft: CraftPanel[];
  voices: EditorialVoice[];
}

/**
 * Editorial content mirror — exact copy of the backend's SHOP_EDITORIAL
 * settings payload (backend/settings.py). The storefront uses the live
 * /fusion/editorial/ payload when the backend is reachable and this mirror
 * only for build-time resilience. Real seeded image URLs — no placeholders.
 */
export const FALLBACK_EDITORIAL: FusionEditorial = {
  craft: [
    {
      title: 'The roast',
      caption: 'Weekly batches',
      body: "Single-origin beans roasted in-house every Monday. The menu follows the season, not the other way around.",
      img: 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&w=1200&q=80',
      alt: 'Freshly roasted coffee beans',
    },
    {
      title: 'The kitchen',
      caption: 'Before sunrise',
      body: 'Pastry lamination starts at 4 a.m. Everything from the shakshuka to the cardamom buns is made on the premises.',
      img: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=80',
      alt: 'Pastry being laminated in the kitchen',
    },
    {
      title: 'The pickup',
      caption: 'Eight minutes',
      body: 'Order ahead and your ticket is queued before you arrive. Average wait from door to cup is under eight minutes.',
      img: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80',
      alt: 'A finished order ready for pickup',
    },
  ],
  voices: [
    {
      name: 'Priya Raghavan',
      role: 'Regular since 2022',
      quote: 'The pour-over changes weekly and the board always tells you exactly what you are getting. I have never once been handed a lukewarm cup.',
      img: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80',
    },
    {
      name: 'Tomás Herrera',
      role: 'Rides past on the commute',
      quote: 'I order the flat white from the bus stop and it is ready when I walk in. Eight minutes, every single time.',
      img: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80',
    },
    {
      name: 'Aisha Okafor',
      role: 'Brings the whole team',
      quote: 'The harissa chicken bowl is the reason our office meetings happen here now. Half the order list is on the wall of fame.',
      img: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=400&q=80',
    },
  ],
};

async function fetchJSON<T>(path: string): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) {
    throw new Error(`API ${path} returned ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchFusionNavigation(): Promise<FusionNavigation | null> {
  try {
    return await fetchJSON<FusionNavigation>('/fusion/navigation/');
  } catch {
    return null;
  }
}

export async function fetchFusionBranding(): Promise<FusionBranding | null> {
  try {
    return await fetchJSON<FusionBranding>('/fusion/branding/');
  } catch {
    return {
      site: { name: SHOP_NAME, tagline: SHOP_TAGLINE, language: 'en' },
      palette: {},
    };
  }
}

export async function fetchFusionAssets(): Promise<FusionAssets | null> {
  try {
    return await fetchJSON<FusionAssets>('/fusion/assets/');
  } catch {
    return null;
  }
}

/** Fetch the editorial craft/testimonial payload (fallback to the mirror). */
export async function fetchFusionEditorial(): Promise<FusionEditorial> {
  try {
    const data = await fetchJSON<FusionEditorial>('/fusion/editorial/');
    return data.craft?.length || data.voices?.length ? data : FALLBACK_EDITORIAL;
  } catch {
    return FALLBACK_EDITORIAL;
  }
}
