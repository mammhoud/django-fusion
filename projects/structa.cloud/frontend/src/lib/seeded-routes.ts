/**
 * Known public detail routes used as a build-time resilience layer.
 * Wagtail remains authoritative whenever the page API is reachable.
 */
export const SEEDED_FALLBACK_SLUGS = {
  products: ['formint-pos', 'lms', 'cms', 'precis-ctc'],
  blog: ['why-landing-pages-as-documents', 'htmx-fragments-vs-json-apis'],
} as const;
