import type { LanguageCode } from './api';

/**
 * Learning-teaser copy per seeded language (en, sv, fr, de, es, ar, pt-br).
 *
 * Mirrors the Django road's gettext catalogs in backend assets/locale so both
 * render roads serve the same copy for the same language.
 *
 * The Astro road is built per language: set PUBLIC_CONTENT_LANGUAGE in the
 * build env (e.g. .env) to sv/fr/de/es/ar/pt-br for a non-English build.
 * English is the fallback when the env var is absent or unknown, so a plain
 * `npm run build` intentionally ships the English teaser.
 */
export interface TeaserCopy {
  /** "[ LEARNING / PREVIEW ]" marker — intentionally identical across locales. */
  marker: string;
  title: string;
  intro: string;
  cta: string;
}

const TEASER_COPY: Record<LanguageCode, TeaserCopy> = {
  en: {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'Courses with visible progress',
    intro: 'Follow serious learning paths with clear content, progress, and a next useful action.',
    cta: 'Open the catalog',
  },
  sv: {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'Kurser med synliga framsteg',
    intro: 'Följ seriösa inlärningsvägar med tydligt innehåll, framsteg och en nästa användbar åtgärd.',
    cta: 'Öppna katalogen',
  },
  fr: {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'Des cours avec une progression visible',
    intro: "Suivez des parcours d'apprentissage sérieux avec un contenu clair, des progrès visibles et une prochaine action utile.",
    cta: 'Ouvrir le catalogue',
  },
  de: {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'Kurse mit sichtbarem Fortschritt',
    intro: 'Folgen Sie ernsthaften Lernpfaden mit klarem Inhalt, sichtbarem Fortschritt und einem nächsten nützlichen Schritt.',
    cta: 'Katalog öffnen',
  },
  es: {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'Cursos con progreso visible',
    intro: 'Sigue rutas de aprendizaje serias con contenido claro, progreso visible y una próxima acción útil.',
    cta: 'Abrir el catálogo',
  },
  ar: {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'دورات تقدّم واضح',
    intro: 'اتبع مسارات تعلّم جادّة بمحتوى واضح وتقدّم ملموس وخطوة تالية مفيدة.',
    cta: 'افتح الكتالوج',
  },
  'pt-br': {
    marker: '[ LEARNING / PREVIEW ]',
    title: 'Cursos com progresso visível',
    intro: 'Siga trilhas de aprendizado sérias com conteúdo claro, progresso visível e uma próxima ação útil.',
    cta: 'Abrir o catálogo',
  },
};

export function teaserCopy(language: LanguageCode): TeaserCopy {
  return TEASER_COPY[language] ?? TEASER_COPY.en;
}
