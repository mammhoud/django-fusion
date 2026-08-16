/**
 * Brand-kit strategy data — the *why* behind each product's mark.
 *
 * Mirrors backend/apps/pages/brand_spec.py (one source per render road; the
 * logo SVG glyphs live in ProductLogo.astro and product_logo.html).
 *
 * Keyed by product slug so the /brand/ page can join cards (from the API)
 * with their brand story. See brandkit strategy: essence (one-line promise),
 * metaphor (symbolic idea), construction (geometry/negative space), voice
 * (typographic character), palette (shared system swatches, accent first).
 */

export interface BrandSpec {
  slug: string;
  brand: string;
  mark: string;
  name: string;
  role: string;
  essence: string;
  metaphor: string;
  construction: string;
  voice: string;
  palette: string[];
}

export const BRAND_SPEC: Record<string, BrandSpec> = {
  'formint-pos': {
    slug: 'formint-pos',
    brand: 'formints',
    mark: 'crest',
    name: 'Formints',
    role: 'Desktop point of sale · Community · Standard · Pro · Cloud',
    essence: 'The till, made trustworthy.',
    metaphor: 'A merchant seal — the shield of a counter you can trust.',
    construction:
      'Shield (trust) + till bar (the counter) + a check cut in negative space (a verified sale).',
    voice: 'Bricolage display for the wordmark · JetBrains Mono for prices.',
    palette: ['formints', 'paper', 'ink', 'line', 'link'],
  },
  lms: {
    slug: 'lms',
    brand: 'precis',
    mark: 'ribbon',
    name: 'Precis LMS',
    role: 'The learning platform behind structa.cloud · courses · enrollments · payments',
    essence: 'Learning, precisely.',
    metaphor: 'An award ribbon — recognition for progress, precisely measured.',
    construction:
      'A ribbon band with tails, an ascending arrow rising from the centre: progress, marked.',
    voice: 'Bricolage display for headings · Public Sans for course copy.',
    palette: ['precis', 'paper', 'ink', 'line', 'live'],
  },
  cms: {
    slug: 'cms',
    brand: 'loop',
    mark: 'isometric',
    name: 'Loop CRM',
    role: 'CRM + social scheduling · Twenty + Postiz merged · coming soon',
    essence: 'From impression to deal.',
    metaphor:
      'A closed loop — every social touchpoint routes through the deal it influenced, one source of truth.',
    construction:
      'An isometric cube (the CRM) orbiting a signal node (social): attribution closing the loop between marketing and sales.',
    voice: 'JetBrains Mono accent — a revenue-ops product, labelled like a dashboard.',
    palette: ['loop', 'paper', 'ink', 'line', 'mark'],
  },
  cypercloud: {
    slug: 'cypercloud',
    brand: 'syntara',
    mark: 'orbit',
    name: 'Syntara',
    role: 'AI chat customizer · ceptor-ai powered · MCP · 2 editions · under development',
    essence: 'Chat, routed around your brand.',
    metaphor:
      'A signal core with crossing conversation orbits — every chat routed around your model, your data.',
    construction:
      'A core node (the model) + two elliptical orbits (conversation paths) + a satellite: customization in motion.',
    voice: 'JetBrains Mono accent — an API product, labelled like one.',
    palette: ['syntara', 'paper', 'ink', 'line', 'link'],
  },
  vresume: {
    slug: 'vresume',
    brand: 'vresume',
    mark: 'ascent',
    name: 'vResume',
    role: 'Portfolio & resume platform · Syntara-powered summaries · cloud hosted',
    essence: 'Your career, on the record.',
    metaphor: 'A staircase — work shown step by step, a check at the summit.',
    construction:
      'A rising stair path with a baseline rule and a verified check at the peak: growth, evidenced.',
    voice: 'Bricolage display for the wordmark · Public Sans for the resume body.',
    palette: ['vresume', 'paper', 'ink', 'line', 'link'],
  },
  'precis-ctc': {
    slug: 'precis-ctc',
    brand: 'precis-ctc',
    mark: 'research',
    name: 'CTC Research',
    role: 'Research workspace · evidence · decisions · team progress',
    essence: 'Evidence, carried forward.',
    metaphor: 'A research signal with a clear centre — questions, evidence, and decisions held in one orbit.',
    construction: 'A focused centre plus intersecting paths: the work stays connected from question to next action.',
    voice: 'Quiet display for findings · JetBrains Mono for status and ownership.',
    palette: ['precis-ctc', 'paper', 'ink', 'line', 'link'],
  },
};

