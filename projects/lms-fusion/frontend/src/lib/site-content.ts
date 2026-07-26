/**
 * Site content adapter — bridges STATIC_PAGES from the Django backend
 * to the Next.js frontend for pages like About, Team, Services, Contact.
 *
 * These pages are fetched via /api/pages/<slug>/ and rendered by the
 * FusionProxy component with site-content-specific block rendering.
 */

import { fusionApi } from './api-client';

export interface SitePageBlock {
  type: string;
  heading?: string;
  intro?: string;
  html?: string;
  items?: SitePageBlockItem[];
  ctas?: SitePageCTA[];
  groups?: SitePageFaqGroup[];
}

export interface SitePageBlockItem {
  heading?: string;
  text?: string;
  label?: string;
  value?: string;
  description?: string;
  href?: string;
  type?: string;
  variant?: string;
}

export interface SitePageCTA {
  label: string;
  href: string;
  variant?: string;
}

export interface SitePageFaqGroup {
  title: string;
  items: { question: string; answer: string }[];
}

export interface SitePage {
  slug: string;
  title: string;
  seo: { title: string; description: string };
  blocks: SitePageBlock[];
  last_updated?: string;
}

/**
 * Fetch a static site page (about, team, services, contact, etc.)
 * from the Fusion CMS API.
 */
export async function fetchSitePage(slug: string): Promise<SitePage | null> {
  try {
    const page = await fusionApi.fetchWagtailPage(slug);
    // If it's a Wagtail page, map it to SitePage format
    return {
      slug: page.slug,
      title: page.title,
      seo: {
        title: page.seo_title || page.title,
        description: page.search_description || '',
      },
      blocks: [
        ...(page.hero_heading ? [{
          type: 'hero' as const,
          heading: page.hero_heading,
          intro: page.hero_subheading || '',
        }] : []),
        ...(page.body ? [{
          type: 'rich_section' as const,
          heading: page.title,
          html: page.body,
        }] : []),
      ],
    };
  } catch {
    // Fall back to static pages from the API
    try {
      const data = await fusionApi.fetchPageData(slug);
      if (data.encoded) {
        const { fusionDecoder } = await import('./fusion-decoder');
        return fusionDecoder.decodeAs<SitePage>(data.encoded);
      }
    } catch {
      // Return null — caller handles 404
    }
  }
  return null;
}

/**
 * Block component renderers map — matches STATIC_PAGES block types
 * to React component renders. Import these from components/site-content/
 * once the component library is built out.
 */
export const BLOCK_RENDERERS: Record<string, string> = {
  hero: 'HeroBlock',
  stats: 'StatsBlock',
  section_header: 'SectionHeaderBlock',
  rich_section: 'RichSectionBlock',
  cta: 'CTABlock',
  faq_groups: 'FAQGroupsBlock',
  contact_methods: 'ContactMethodsBlock',
  form: 'ContactFormBlock',
};

/**
 * Available site pages from STATIC_PAGES.
 */
export const STATIC_PAGE_SLUGS = [
  'home',
  'about',
  'team',
  'services',
  'contact',
  'privacy',
  'faq',
] as const;
