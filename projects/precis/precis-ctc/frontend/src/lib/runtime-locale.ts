/**
 * runtime-locale — shared client-side localization for the static Astro shell.
 *
 * The CTC frontend is intentionally static: pages ship as English build
 * artifacts and the backend (Wagtail/django-fusion) is the authoritative
 * content source. This module gives EVERY page the same runtime localization
 * that /about/ already had:
 *
 *   1. Resolve the requested language (query → storage → cookie → build lang).
 *   2. Fetch the localized page payload from `/apis/pages/<slug>/?lang=X`
 *      (bounded retry + no-store so transient backend latency never leaves
 *      the English shell visible).
 *   3. Swap the visible copy via `[data-l10n]` attribute selectors and
 *      translate static UI chrome via the bundled UI_COPY dictionary.
 *   4. Set `lang` / `dir` / `data-language` / `data-localized-ready` on
 *      <html> so CSS, SEO, and tests all agree on the active locale.
 *
 * Pages opt in with `data-l10n` attributes (or the shared chrome selectors);
 * pages without any localized blocks still get the dictionary + document
 * metadata treatment.
 */

import type { LanguageCode } from './api';

export const SUPPORTED_LOCALES: readonly LanguageCode[] = ['en', 'sv', 'fr', 'de', 'es', 'ar', 'pt-br'];
export const STORAGE_KEY = 'ctc_lang';

export function isSupportedLocale(value: string | null | undefined): value is LanguageCode {
  return !!value && (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

/** Same priority as LanguageSwitcher: query → sessionStorage → localStorage → cookie. */
export function resolveRequestedLanguage(fallback: LanguageCode = 'en'): LanguageCode {
  if (typeof window === 'undefined') return fallback;
  try {
    const query = new URLSearchParams(window.location.search).get('lang');
    const stored = window.sessionStorage.getItem(STORAGE_KEY)
      || window.localStorage.getItem(STORAGE_KEY)
      || document.cookie.match(/(?:^|; )django_language=([^;]+)/)?.[1];
    const candidate = query || stored || document.documentElement.getAttribute('lang');
    return isSupportedLocale(candidate) ? candidate : fallback;
  } catch {
    return fallback;
  }
}

/** True when a ?lang= (or stored) preference differs from the baked build language. */
export function shouldLocalize(buildLanguage: LanguageCode = 'en'): boolean {
  return resolveRequestedLanguage(buildLanguage) !== buildLanguage;
}

interface LocalizedPagePayload {
  language?: string;
  available_languages?: string[];
  title?: string;
  mission_intro?: string;
  seo?: { description?: string };
  [key: string]: unknown;
}

/** Payload of GET /apis/contact/?lang=X (see ContactData in api.ts). */
export interface ContactPagePayload {
  language?: string;
  title?: string;
  description?: string;
  form_title?: string;
  form_description?: string;
  button_text?: string;
  success_message?: string;
  error_message?: string;
  fields?: Array<{
    name?: string;
    label?: string;
    placeholder?: string;
    [key: string]: unknown;
  }>;
  [key: string]: unknown;
}

/**
 * Fetch the localized page payload with bounded retry + no-store. Returns null
 * when the backend is unreachable so callers keep the static English shell
 * (better a usable page than a broken one).
 */
export async function fetchLocalizedPage(
  slug: string,
  language: LanguageCode,
): Promise<LocalizedPagePayload | null> {
  if (typeof window === 'undefined') return null;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const response: Response = await window.fetch(
        `/apis/pages/${encodeURIComponent(slug)}/?lang=${encodeURIComponent(language)}&locale_refresh=1`,
        { cache: 'no-store', headers: { Accept: 'application/json' } },
      );
      if (response.ok) {
        const candidate = (await response.json()) as LocalizedPagePayload;
        if (candidate.language === language) return candidate;
      }
    } catch {
      // transient network failure — retry below
    }
    if (attempt < 2) await new Promise((resolve) => setTimeout(resolve, 250 * (attempt + 1)));
  }
  return null;
}

/**
 * Fetch the localized contact payload (`/apis/contact/?lang=X`). The contact
 * page renders from this endpoint (form fields, messages, contact info) so
 * the runtime swap must use it instead of the generic page payload.
 * Same bounded retry + no-store contract as fetchLocalizedPage.
 */
export async function fetchLocalizedContact(language: LanguageCode): Promise<ContactPagePayload | null> {
  if (typeof window === 'undefined') return null;
  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      const response: Response = await window.fetch(
        `/apis/contact/?lang=${encodeURIComponent(language)}&locale_refresh=1&_=${Date.now()}`,
        { cache: 'no-store', headers: { Accept: 'application/json' } },
      );
      if (response.ok) {
        const candidate = (await response.json()) as ContactPagePayload;
        if (candidate.language === language) return candidate;
      }
    } catch {
      // transient network failure — retry below
    }
    if (attempt < 2) await new Promise((resolve) => setTimeout(resolve, 250 * (attempt + 1)));
  }
  return null;
}

// ── Shared UI chrome dictionary ──────────────────────────────────────────
// Mirrors the Django road's gettext catalogs where they exist; the keys below
// cover the static chrome (header auth labels, footer, catalog/course chrome)
// that the backend never serves.

export interface UiCopy {
  nav_login: string;
  nav_profile: string;
  nav_email_addresses: string;
  nav_change_password: string;
  nav_security_mfa: string;
  nav_sign_out: string;
  nav_get_started: string;
  cta_talk_to_sales: string;
  catalog_search: string;
  catalog_grid: string;
  catalog_list: string;
  catalog_filters: string;
  catalog_clear: string;
  catalog_sort: string;
  catalog_difficulty: string;
  catalog_language: string;
  catalog_specialization: string;
  catalog_topics: string;
  catalog_offer: string;
  catalog_extras: string;
  catalog_certificate: string;
  catalog_all_languages: string;
  catalog_all_specializations: string;
  catalog_free_paid: string;
  catalog_free_only: string;
  catalog_paid_only: string;
  catalog_no_matches: string;
  course_enroll: string;
  course_enroll_free: string;
  course_back: string;
  course_students: string;
  course_modules: string;
  course_duration: string;
  course_certificate: string;
  course_overview: string;
  course_why: string;
  course_learn: string;
  course_audience: string;
  course_requirements: string;
  course_preview: string;
  course_watch_preview: string;
  course_facts: string;
  course_free: string;
  course_included: string;
  course_level: string;
  course_language: string;
  course_rating: string;
  course_syllabus: string;
  course_lessons: string;
  course_instructor: string;
  course_related: string;
  course_view: string;
}

const UI_COPY: Record<LanguageCode, UiCopy> = {
  en: {
    nav_login: 'Log In',
    nav_profile: 'Profile',
    nav_email_addresses: 'Email addresses',
    nav_change_password: 'Change password',
    nav_security_mfa: 'Security & MFA',
    nav_sign_out: 'Sign out',
    nav_get_started: 'Get Started',
    cta_talk_to_sales: 'Talk to sales',
    catalog_search: 'Search courses…',
    catalog_grid: 'Grid',
    catalog_list: 'List',
    catalog_filters: 'Filters',
    catalog_clear: 'Clear all filters',
    catalog_sort: 'Sort by',
    catalog_difficulty: 'Difficulty',
    catalog_language: 'Language',
    catalog_specialization: 'Specialization',
    catalog_topics: 'Topics',
    catalog_offer: 'Offer',
    catalog_extras: 'Extras',
    catalog_certificate: 'Certificate included',
    catalog_all_languages: 'All languages',
    catalog_all_specializations: 'All specializations',
    catalog_free_paid: 'Free & paid',
    catalog_free_only: 'Free only',
    catalog_paid_only: 'Paid only',
    catalog_no_matches: 'No courses match your filters',
    course_enroll: 'Enroll now',
    course_enroll_free: 'Enroll for free',
    course_back: '← Back to catalog',
    course_students: 'Students',
    course_modules: 'Modules',
    course_duration: 'Duration',
    course_certificate: 'Certificate',
    course_overview: 'course overview',
    course_why: 'Why this course matters',
    course_learn: 'What you\'ll learn',
    course_audience: 'Who this course is for',
    course_requirements: 'Requirements',
    course_preview: 'Course preview',
    course_watch_preview: 'Watch preview →',
    course_facts: 'course facts',
    course_free: 'Free',
    course_included: 'Included',
    course_level: 'Level',
    course_language: 'Language',
    course_rating: 'Rating',
    course_syllabus: 'Course syllabus',
    course_lessons: 'lessons',
    course_instructor: 'instructor',
    course_related: 'More courses from the catalog',
    course_view: 'View →',
  },
  sv: {
    nav_login: 'Logga in',
    nav_profile: 'Profil',
    nav_email_addresses: 'E-postadresser',
    nav_change_password: 'Ändra lösenord',
    nav_security_mfa: 'Säkerhet och MFA',
    nav_sign_out: 'Logga ut',
    nav_get_started: 'Kom igång',
    cta_talk_to_sales: 'Kontakta sälj',
    catalog_search: 'Sök kurser…',
    catalog_grid: 'Rutnät',
    catalog_list: 'Lista',
    catalog_filters: 'Filter',
    catalog_clear: 'Rensa alla filter',
    catalog_sort: 'Sortera efter',
    catalog_difficulty: 'Svårighetsgrad',
    catalog_language: 'Språk',
    catalog_specialization: 'Inriktning',
    catalog_topics: 'Ämnen',
    catalog_offer: 'Erbjudande',
    catalog_extras: 'Extra',
    catalog_certificate: 'Intyg ingår',
    catalog_all_languages: 'Alla språk',
    catalog_all_specializations: 'Alla inriktningar',
    catalog_free_paid: 'Gratis och betald',
    catalog_free_only: 'Endast gratis',
    catalog_paid_only: 'Endast betald',
    catalog_no_matches: 'Inga kurser matchar dina filter',
    course_enroll: 'Anmäl dig nu',
    course_enroll_free: 'Anmäl dig gratis',
    course_back: '← Tillbaka till katalogen',
    course_students: 'Studenter',
    course_modules: 'Moduler',
    course_duration: 'Längd',
    course_certificate: 'Intyg',
    course_overview: 'kursöversikt',
    course_why: 'Varför den här kursen är viktig',
    course_learn: 'Vad du lär dig',
    course_audience: 'För vem kursen är',
    course_requirements: 'Förkunskaper',
    course_preview: 'Kurspreview',
    course_watch_preview: 'Se preview →',
    course_facts: 'kursfakta',
    course_free: 'Gratis',
    course_included: 'Ingår',
    course_level: 'Nivå',
    course_language: 'Språk',
    course_rating: 'Betyg',
    course_syllabus: 'Kursens upplägg',
    course_lessons: 'lektioner',
    course_instructor: 'instruktör',
    course_related: 'Fler kurser i katalogen',
    course_view: 'Visa →',
  },
  fr: {
    nav_login: 'Connexion',
    nav_profile: 'Profil',
    nav_email_addresses: 'Adresses e-mail',
    nav_change_password: 'Changer le mot de passe',
    nav_security_mfa: 'Sécurité et MFA',
    nav_sign_out: 'Déconnexion',
    nav_get_started: 'Commencer',
    cta_talk_to_sales: 'Contacter les ventes',
    catalog_search: 'Rechercher des cours…',
    catalog_grid: 'Grille',
    catalog_list: 'Liste',
    catalog_filters: 'Filtres',
    catalog_clear: 'Effacer tous les filtres',
    catalog_sort: 'Trier par',
    catalog_difficulty: 'Difficulté',
    catalog_language: 'Langue',
    catalog_specialization: 'Spécialisation',
    catalog_topics: 'Sujets',
    catalog_offer: 'Offre',
    catalog_extras: 'Extras',
    catalog_certificate: 'Certificat inclus',
    catalog_all_languages: 'Toutes les langues',
    catalog_all_specializations: 'Toutes les spécialisations',
    catalog_free_paid: 'Gratuit et payant',
    catalog_free_only: 'Gratuit uniquement',
    catalog_paid_only: 'Payant uniquement',
    catalog_no_matches: 'Aucun cours ne correspond à vos filtres',
    course_enroll: 'S\'inscrire',
    course_enroll_free: 'S\'inscrire gratuitement',
    course_back: '← Retour au catalogue',
    course_students: 'Étudiants',
    course_modules: 'Modules',
    course_duration: 'Durée',
    course_certificate: 'Certificat',
    course_overview: 'aperçu du cours',
    course_why: 'Pourquoi ce cours compte',
    course_learn: 'Ce que vous apprendrez',
    course_audience: 'À qui s\'adresse ce cours',
    course_requirements: 'Prérequis',
    course_preview: 'Aperçu du cours',
    course_watch_preview: 'Voir l\'aperçu →',
    course_facts: 'informations du cours',
    course_free: 'Gratuit',
    course_included: 'Inclus',
    course_level: 'Niveau',
    course_language: 'Langue',
    course_rating: 'Note',
    course_syllabus: 'Programme du cours',
    course_lessons: 'leçons',
    course_instructor: 'instructeur',
    course_related: 'Plus de cours du catalogue',
    course_view: 'Voir →',
  },
  de: {
    nav_login: 'Anmelden',
    nav_profile: 'Profil',
    nav_email_addresses: 'E-Mail-Adressen',
    nav_change_password: 'Passwort ändern',
    nav_security_mfa: 'Sicherheit und MFA',
    nav_sign_out: 'Abmelden',
    nav_get_started: 'Loslegen',
    cta_talk_to_sales: 'Vertrieb kontaktieren',
    catalog_search: 'Kurse suchen…',
    catalog_grid: 'Raster',
    catalog_list: 'Liste',
    catalog_filters: 'Filter',
    catalog_clear: 'Alle Filter zurücksetzen',
    catalog_sort: 'Sortieren nach',
    catalog_difficulty: 'Schwierigkeitsgrad',
    catalog_language: 'Sprache',
    catalog_specialization: 'Spezialisierung',
    catalog_topics: 'Themen',
    catalog_offer: 'Angebot',
    catalog_extras: 'Extras',
    catalog_certificate: 'Zertifikat enthalten',
    catalog_all_languages: 'Alle Sprachen',
    catalog_all_specializations: 'Alle Spezialisierungen',
    catalog_free_paid: 'Kostenlos und kostenpflichtig',
    catalog_free_only: 'Nur kostenlos',
    catalog_paid_only: 'Nur kostenpflichtig',
    catalog_no_matches: 'Keine Kurse passen zu Ihren Filtern',
    course_enroll: 'Jetzt einschreiben',
    course_enroll_free: 'Kostenlos einschreiben',
    course_back: '← Zurück zum Katalog',
    course_students: 'Teilnehmer',
    course_modules: 'Module',
    course_duration: 'Dauer',
    course_certificate: 'Zertifikat',
    course_overview: 'Kursübersicht',
    course_why: 'Warum dieser Kurs wichtig ist',
    course_learn: 'Was Sie lernen',
    course_audience: 'Für wen dieser Kurs ist',
    course_requirements: 'Voraussetzungen',
    course_preview: 'Kursvorschau',
    course_watch_preview: 'Vorschau ansehen →',
    course_facts: 'Kursfakten',
    course_free: 'Kostenlos',
    course_included: 'Inklusive',
    course_level: 'Niveau',
    course_language: 'Sprache',
    course_rating: 'Bewertung',
    course_syllabus: 'Kurslehrplan',
    course_lessons: 'Lektionen',
    course_instructor: 'Dozent',
    course_related: 'Weitere Kurse aus dem Katalog',
    course_view: 'Ansehen →',
  },
  es: {
    nav_login: 'Iniciar sesión',
    nav_profile: 'Perfil',
    nav_email_addresses: 'Direcciones de correo',
    nav_change_password: 'Cambiar contraseña',
    nav_security_mfa: 'Seguridad y MFA',
    nav_sign_out: 'Cerrar sesión',
    nav_get_started: 'Empezar',
    cta_talk_to_sales: 'Hablar con ventas',
    catalog_search: 'Buscar cursos…',
    catalog_grid: 'Cuadrícula',
    catalog_list: 'Lista',
    catalog_filters: 'Filtros',
    catalog_clear: 'Limpiar todos los filtros',
    catalog_sort: 'Ordenar por',
    catalog_difficulty: 'Dificultad',
    catalog_language: 'Idioma',
    catalog_specialization: 'Especialización',
    catalog_topics: 'Temas',
    catalog_offer: 'Oferta',
    catalog_extras: 'Extras',
    catalog_certificate: 'Certificado incluido',
    catalog_all_languages: 'Todos los idiomas',
    catalog_all_specializations: 'Todas las especializaciones',
    catalog_free_paid: 'Gratis y de pago',
    catalog_free_only: 'Solo gratis',
    catalog_paid_only: 'Solo de pago',
    catalog_no_matches: 'Ningún curso coincide con tus filtros',
    course_enroll: 'Inscríbete ahora',
    course_enroll_free: 'Inscríbete gratis',
    course_back: '← Volver al catálogo',
    course_students: 'Estudiantes',
    course_modules: 'Módulos',
    course_duration: 'Duración',
    course_certificate: 'Certificado',
    course_overview: 'resumen del curso',
    course_why: 'Por qué importa este curso',
    course_learn: 'Lo que aprenderás',
    course_audience: 'Para quién es este curso',
    course_requirements: 'Requisitos',
    course_preview: 'Vista previa del curso',
    course_watch_preview: 'Ver vista previa →',
    course_facts: 'datos del curso',
    course_free: 'Gratis',
    course_included: 'Incluido',
    course_level: 'Nivel',
    course_language: 'Idioma',
    course_rating: 'Valoración',
    course_syllabus: 'Plan de estudios',
    course_lessons: 'lecciones',
    course_instructor: 'instructor',
    course_related: 'Más cursos del catálogo',
    course_view: 'Ver →',
  },
  ar: {
    nav_login: 'تسجيل الدخول',
    nav_profile: 'الملف الشخصي',
    nav_email_addresses: 'عناوين البريد الإلكتروني',
    nav_change_password: 'تغيير كلمة المرور',
    nav_security_mfa: 'الأمان والمصادقة الثنائية',
    nav_sign_out: 'تسجيل الخروج',
    nav_get_started: 'ابدأ الآن',
    cta_talk_to_sales: 'تواصل مع المبيعات',
    catalog_search: 'ابحث في الدورات…',
    catalog_grid: 'شبكة',
    catalog_list: 'قائمة',
    catalog_filters: 'فلاتر',
    catalog_clear: 'مسح جميع الفلاتر',
    catalog_sort: 'ترتيب حسب',
    catalog_difficulty: 'المستوى',
    catalog_language: 'اللغة',
    catalog_specialization: 'التخصص',
    catalog_topics: 'المواضيع',
    catalog_offer: 'العرض',
    catalog_extras: 'إضافات',
    catalog_certificate: 'شهادة مرفقة',
    catalog_all_languages: 'كل اللغات',
    catalog_all_specializations: 'كل التخصصات',
    catalog_free_paid: 'مجاني ومدفوع',
    catalog_free_only: 'مجاني فقط',
    catalog_paid_only: 'مدفوع فقط',
    catalog_no_matches: 'لا توجد دورات تطابق فلاترك',
    course_enroll: 'سجّل الآن',
    course_enroll_free: 'سجّل مجاناً',
    course_back: '← العودة إلى الكتالوج',
    course_students: 'الطلاب',
    course_modules: 'الوحدات',
    course_duration: 'المدة',
    course_certificate: 'الشهادة',
    course_overview: 'نظرة عامة على الدورة',
    course_why: 'لماذا هذه الدورة مهمة',
    course_learn: 'ما ستتعلمه',
    course_audience: 'لمن هذه الدورة',
    course_requirements: 'المتطلبات',
    course_preview: 'معاينة الدورة',
    course_watch_preview: 'شاهد المعاينة ←',
    course_facts: 'معلومات الدورة',
    course_free: 'مجاني',
    course_included: 'مشمول',
    course_level: 'المستوى',
    course_language: 'اللغة',
    course_rating: 'التقييم',
    course_syllabus: 'منهج الدورة',
    course_lessons: 'دروس',
    course_instructor: 'المدرّب',
    course_related: 'مزيد من الدورات في الكتالوج',
    course_view: 'عرض ←',
  },
  'pt-br': {
    nav_login: 'Entrar',
    nav_profile: 'Perfil',
    nav_email_addresses: 'Endereços de e-mail',
    nav_change_password: 'Alterar senha',
    nav_security_mfa: 'Segurança e MFA',
    nav_sign_out: 'Sair',
    nav_get_started: 'Começar',
    cta_talk_to_sales: 'Falar com vendas',
    catalog_search: 'Buscar cursos…',
    catalog_grid: 'Grade',
    catalog_list: 'Lista',
    catalog_filters: 'Filtros',
    catalog_clear: 'Limpar todos os filtros',
    catalog_sort: 'Ordenar por',
    catalog_difficulty: 'Dificuldade',
    catalog_language: 'Idioma',
    catalog_specialization: 'Especialização',
    catalog_topics: 'Tópicos',
    catalog_offer: 'Oferta',
    catalog_extras: 'Extras',
    catalog_certificate: 'Certificado incluído',
    catalog_all_languages: 'Todos os idiomas',
    catalog_all_specializations: 'Todas as especializações',
    catalog_free_paid: 'Grátis e pago',
    catalog_free_only: 'Somente grátis',
    catalog_paid_only: 'Somente pago',
    catalog_no_matches: 'Nenhum curso corresponde aos seus filtros',
    course_enroll: 'Matricule-se agora',
    course_enroll_free: 'Matricule-se grátis',
    course_back: '← Voltar ao catálogo',
    course_students: 'Estudantes',
    course_modules: 'Módulos',
    course_duration: 'Duração',
    course_certificate: 'Certificado',
    course_overview: 'visão geral do curso',
    course_why: 'Por que este curso é importante',
    course_learn: 'O que você vai aprender',
    course_audience: 'Para quem é este curso',
    course_requirements: 'Requisitos',
    course_preview: 'Prévia do curso',
    course_watch_preview: 'Ver prévia →',
    course_facts: 'informações do curso',
    course_free: 'Grátis',
    course_included: 'Incluído',
    course_level: 'Nível',
    course_language: 'Idioma',
    course_rating: 'Avaliação',
    course_syllabus: 'Ementa do curso',
    course_lessons: 'aulas',
    course_instructor: 'instrutor',
    course_related: 'Mais cursos do catálogo',
    course_view: 'Ver →',
  },
};

export function uiCopy(language: LanguageCode): UiCopy {
  return UI_COPY[language] ?? UI_COPY.en;
}

/** Swap `[data-i18n="<key>"]` text + `[data-i18n-placeholder]` from the dictionary. */
export function applyUiCopy(language: LanguageCode): void {
  const copy = uiCopy(language);
  document.querySelectorAll<HTMLElement>('[data-i18n]').forEach((node) => {
    const key = node.getAttribute('data-i18n');
    if (key && key in copy) node.textContent = copy[key as keyof UiCopy];
  });
  document.querySelectorAll<HTMLInputElement>('[data-i18n-placeholder]').forEach((node) => {
    const key = node.getAttribute('data-i18n-placeholder');
    if (key && key in copy) node.placeholder = copy[key as keyof UiCopy];
  });
}

// ── Generic selector-based page hydration ─────────────────────────────────
//
// A page declares `data-l10n` attributes on the elements it wants localized:
//
//   <h1 data-l10n="hero.title">English fallback</h1>
//   <p  data-l10n="hero.subtitle">…</p>
//
// The mapper below flattens the backend payload (hero.title, cta.label, …)
// and writes each value into the matching element. Elements whose key is
// missing from the payload keep their baked English text — the static shell
// is never made worse.

const SELECTOR = '[data-l10n]';

export function applyLocalizedPayload(payload: LocalizedPagePayload | null): void {
  if (!payload) return;
  const nodes = Array.from(document.querySelectorAll<HTMLElement>(SELECTOR));
  if (!nodes.length) return;

  const getValue = (key: string): unknown => {
    // Key sections are 2-part (`hero.title`) or 3+ part for CMS chrome
    // (`home_chrome.slider_head.title`, `home_chrome.evidence_panel.stats.0.label`).
    // Destructure the full remainder — `[section, ...rest]` — so nested
    // chrome paths keep every segment after the section token.
    const [section, ...rest] = key.split('.');
    const field = rest.join('.');
    // CMS section chrome (HomePage.home_chrome → slider_head.title, …).
    // Paths like `home_chrome.evidence_panel.stats.0.label` walk nested
    // objects/lists via numeric indices.
    if (section === 'home_chrome') {
      const chrome = (payload.home_chrome ?? {}) as Record<string, unknown>;
      let node: unknown = chrome;
      for (const segment of field.split('.')) {
        if (!segment) return '';
        if (node && typeof node === 'object') {
          const obj = node as Record<string, unknown>;
          node = obj[segment];
        } else if (Array.isArray(node) && /^\d+$/.test(segment)) {
          node = node[Number(segment)];
        } else {
          return '';
        }
      }
      return typeof node === 'string' ? node : '';
    }
    if (section === 'contact' && payload.contact) {
      const contact = payload.contact as Record<string, unknown>;
      if (field === 'description') return contact.description ?? '';
      if (field === 'form_title') return contact.form_title ?? '';
      if (field === 'form_description') return contact.form_description ?? '';
      if (field === 'button_text') return contact.button_text ?? '';
      return '';
    }
    if (section === 'hero' && payload.hero) {
      const hero = payload.hero as Record<string, unknown>;
      if (field === 'title' && hero.title) return hero.title;
      if (field === 'subtitle') return hero.subtitle ?? '';
      if (field === 'badge') return hero.badge ?? '';
      if (field === 'accent' && hero.accent) return hero.accent;
      if (field === 'cta1') {
        const cta = (hero.primary_cta ?? {}) as { label?: string };
        return cta.label ?? '';
      }
      if (field === 'cta2') {
        const cta = (hero.secondary_cta ?? {}) as { label?: string };
        return cta.label ?? '';
      }
      return '';
    }
    if (section === 'cta' && payload.cta) {
      const cta = payload.cta as Record<string, unknown>;
      if (field === 'title') return cta.title ?? '';
      if (field === 'subtitle') return cta.subtitle ?? '';
      if (field === 'label') {
        const primary = (cta.primary_cta ?? {}) as { label?: string };
        return primary.label ?? '';
      }
      return '';
    }
    return (payload as Record<string, unknown>)[key] ?? '';
  };

  nodes.forEach((node) => {
    const key = node.getAttribute('data-l10n') || '';
    const value = getValue(key);
    if (typeof value === 'string' && value.trim()) node.textContent = value.trim();
  });
}

/**
 * Localize the contact page from the dedicated /apis/contact/ payload.
 *
 * The contact road is a static Astro artifact like every other page, but its
 * copy comes from the dedicated contact endpoint (form fields, button,
 * success/error messages, heading). This applies:
 *
 *   - `[data-l10n="contact.title"]`, `contact.description`, `contact.form_title`,
 *     `contact.form_description`, `contact.button_text` → textContent
 *   - `[data-l10n="contact.fields.<name>.label"]` / `.placeholder` → text /
 *     placeholder (each form field carries its own name in the selector)
 */
export function applyContactPayload(payload: ContactPagePayload | null): void {
  if (!payload) return;
  const nodes = Array.from(document.querySelectorAll<HTMLElement>('[data-l10n]'));
  if (!nodes.length) return;

  const setText = (node: HTMLElement, key: string) => {
    const [section, ...rest] = key.split('.');
    if (section !== 'contact') return;
    const field = rest.join('.');
    if (field === 'title') return node.textContent = payload.title ?? '';
    if (field === 'description') return node.textContent = payload.description ?? '';
    if (field === 'form_title') return node.textContent = payload.form_title ?? '';
    if (field === 'form_description') return node.textContent = payload.form_description ?? '';
    if (field === 'button_text') return node.textContent = payload.button_text ?? '';
    if (field.startsWith('field.')) {
      // contact.field.<name>.label / .placeholder
      const [, name, attr] = field.split('.');
      const entry = (payload.fields ?? []).find((f) => f.name === name);
      if (!entry) return;
      if (attr === 'label') node.textContent = entry.label ?? '';
      if (attr === 'placeholder') {
        (node as HTMLInputElement | HTMLTextAreaElement).placeholder = entry.placeholder ?? '';
      }
    }
  };

  nodes.forEach((node) => setText(node, node.getAttribute('data-l10n') || ''));
}

/** Set document lang/dir + title for the contact page (no meta description here). */
export function applyContactMetadata(payload: ContactPagePayload | null, language: LanguageCode): void {
  const root = document.documentElement;
  root.setAttribute('lang', language);
  root.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
  root.dataset.language = language;
  root.dataset.localizedReady = language;
  if (payload?.title) document.title = String(payload.title);
}

/** Apply the shared document-level metadata for the active locale. */
export function applyDocumentMetadata(payload: LocalizedPagePayload | null, language: LanguageCode): void {
  const root = document.documentElement;
  root.setAttribute('lang', language);
  root.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
  root.dataset.language = language;
  root.dataset.localizedReady = language;
  if (payload?.title) document.title = String(payload.title);
  const description = payload?.seo?.description || (typeof payload?.mission_intro === 'string' ? payload.mission_intro : '');
  if (description) document.querySelector('meta[name="description"]')?.setAttribute('content', description);
}

/**
 * One-call site-wide synchronizer for any static page.
 *
 * @param slug        backend page slug ('' or 'home' for the landing page)
 * @param buildLang   language the artifact was baked in (defaults to 'en')
 */

// Frontend route slug → backend Wagtail slug. The Astro shell routes pages by
// marketing names, but the seeded Wagtail tree uses its own slugs (e.g. the
// course catalog lives at ``all-courses``, not ``courses``).
const ROUTE_PAGE_ALIASES: Record<string, string> = {
  '': 'home',
  courses: 'all-courses',
  'about/founder': 'about',
  'about/research': 'about',
  'about/education': 'about',
};

export function backendSlugFor(routeSlug: string): string {
  return ROUTE_PAGE_ALIASES[routeSlug] || routeSlug || 'home';
}

export async function syncRuntimeLocale(slug: string, buildLang: LanguageCode = 'en'): Promise<void> {
  const language = resolveRequestedLanguage(buildLang);
  if (language === buildLang) {
    applyDocumentMetadata(null, language);
    applyUiCopy(language);
    return;
  }
  const payload = await fetchLocalizedPage(backendSlugFor(slug), language);
  applyLocalizedPayload(payload);
  applyDocumentMetadata(payload, language);
  applyUiCopy(language);
}

export async function syncContactLocale(buildLang: LanguageCode = 'en'): Promise<void> {
  const language = resolveRequestedLanguage(buildLang);
  if (language === buildLang) {
    applyContactMetadata(null, language);
    applyUiCopy(language);
    return;
  }
  const payload = await fetchLocalizedContact(language);
  applyContactPayload(payload);
  applyContactMetadata(payload, language);
  applyUiCopy(language);
}

// Backward-compatible alias used by the About page's inline synchronizer.
export const applyLocalizedText = applyLocalizedPayload;
