/**
 * Landing-fusion translations — the single source of truth for every visible
 * UI string.  Each page imports ``t(lang, key)`` to resolve the active language.
 *
 * Adding a language:
 *   1. Add the new column to every table below.
 *   2. Add the flag entry to ``LANG_META``.
 *   3. Add ``(code, name)`` to ``LANGUAGES`` in Django settings.
 *
 * Supported: English (en), Arabic (ar · RTL), Swedish (sv),
 *            French (fr), German (de), Spanish (es), Portuguese (pt)
 */

export type LangCode = 'en' | 'ar' | 'sv' | 'fr' | 'de' | 'es' | 'pt';

export interface LangMeta {
  code: LangCode;
  label: string;
  native: string;
  flag: string;   // emoji flag (used in the switcher)
  dir: 'ltr' | 'rtl';
}

export const LANG_META: Record<LangCode, LangMeta> = {
  en: { code: 'en', label: 'English',    native: 'English',    flag: '🇬🇧', dir: 'ltr' },
  ar: { code: 'ar', label: 'Arabic',     native: 'العربية',     flag: '🇸🇦', dir: 'rtl' },
  sv: { code: 'sv', label: 'Swedish',    native: 'Svenska',    flag: '🇸🇪', dir: 'ltr' },
  fr: { code: 'fr', label: 'French',     native: 'Français',   flag: '🇫🇷', dir: 'ltr' },
  de: { code: 'de', label: 'German',     native: 'Deutsch',    flag: '🇩🇪', dir: 'ltr' },
  es: { code: 'es', label: 'Spanish',    native: 'Español',    flag: '🇪🇸', dir: 'ltr' },
  pt: { code: 'pt', label: 'Portuguese', native: 'Português',  flag: '🇧🇷', dir: 'ltr' },
};

/** All supported language codes (ordered). */
export const LANG_CODES: LangCode[] = ['en', 'ar', 'sv', 'fr', 'de', 'es', 'pt'];

/** Detect the best initial language: localStorage → browser → English fallback. */
export function detectLang(): LangCode {
  try {
    const stored = localStorage.getItem('fusion-lang') as LangCode | null;
    if (stored && LANG_META[stored]) return stored;
  } catch { /* localStorage unavailable */ }

  if (typeof navigator !== 'undefined') {
    const browser = navigator.language?.split('-')[0] as LangCode;
    if (browser && LANG_META[browser]) return browser;
  }
  return 'en';
}

/** Apply language to the DOM: <html lang>, dir, and persist. */
export function applyLang(code: LangCode): void {
  document.documentElement.lang = code;
  document.documentElement.dir = LANG_META[code].dir;
  try { localStorage.setItem('fusion-lang', code); } catch { /* noop */ }
}

// ── Translation tables ─────────────────────────────────────────────────────
// Key: translation key (snake_case, mirrors what gets displayed).
// Each row holds the translated string per language.

interface TranslationTable {
  [key: string]: Record<LangCode, string>;
}

export const T: TranslationTable = {
  // ── Navigation ──
  'nav_home':        { en:'Home',       ar:'الرئيسية',     sv:'Hem',        fr:'Accueil',    de:'Start',      es:'Inicio',     pt:'Início' },
  'nav_services':    { en:'Services',   ar:'الخدمات',      sv:'Tjänster',   fr:'Services',   de:'Dienste',    es:'Servicios',  pt:'Serviços' },
  'nav_products':    { en:'Products',   ar:'المنتجات',     sv:'Produkter',  fr:'Produits',   de:'Produkte',   es:'Productos',  pt:'Produtos' },
  'nav_learning':    { en:'Learn',      ar:'تعلّم',         sv:'Lär dig',    fr:'Apprendre',  de:'Lernen',     es:'Aprender',   pt:'Aprender' },
  'nav_blog':        { en:'Blog',       ar:'المدونة',      sv:'Blogg',      fr:'Blog',       de:'Blog',       es:'Blog',       pt:'Blog' },
  'nav_pricing':     { en:'Pricing',    ar:'الأسعار',      sv:'Priser',     fr:'Tarifs',     de:'Preise',     es:'Precios',    pt:'Preços' },
  'nav_about':       { en:'About',      ar:'حول',          sv:'Om',         fr:'À propos',   de:'Über',       es:'Acerca de',  pt:'Sobre' },
  'nav_contact':     { en:'Contact',    ar:'اتصل بنا',     sv:'Kontakt',    fr:'Contact',    de:'Kontakt',    es:'Contacto',   pt:'Contato' },
  'nav_faq':         { en:'FAQ',        ar:'الأسئلة',      sv:'FAQ',        fr:'FAQ',        de:'FAQ',        es:'FAQ',        pt:'FAQ' },
  'nav_brand':       { en:'Brand',      ar:'العلامة',      sv:'Varumärke',  fr:'Marque',     de:'Marke',      es:'Marca',      pt:'Marca' },
  'nav_features':    { en:'Features',   ar:'الميزات',      sv:'Funktioner', fr:'Fonctions',  de:'Funktionen', es:'Funciones',  pt:'Recursos' },
  'nav_login':       { en:'Log In',     ar:'تسجيل الدخول', sv:'Logga in',   fr:'Connexion',  de:'Anmelden',   es:'Iniciar',    pt:'Entrar' },
  'nav_get_started': { en:'Get Started',ar:'ابدأ الآن',    sv:'Kom igång',  fr:'Démarrer',   de:'Loslegen',   es:'Empezar',    pt:'Começar' },
  'nav_sign_out':    { en:'Sign out',   ar:'تسجيل الخروج', sv:'Logga ut',   fr:'Déconnexion',de:'Abmelden',   es:'Salir',      pt:'Sair' },
  'nav_profile':     { en:'Profile',    ar:'الملف الشخصي', sv:'Profil',     fr:'Profil',     de:'Profil',     es:'Perfil',     pt:'Perfil' },

  // ── Auth ──
  'auth_sign_in':          { en:'Sign in',            ar:'تسجيل الدخول',   sv:'Logga in',        fr:'Connexion',       de:'Anmelden',        es:'Iniciar sesión',    pt:'Entrar' },
  'auth_create_account':   { en:'Create an account',  ar:'إنشاء حساب',    sv:'Skapa konto',     fr:'Créer un compte', de:'Konto erstellen', es:'Crear cuenta',      pt:'Criar conta' },
  'auth_forgot_password':  { en:'Forgot password?',   ar:'نسيت كلمة المرور؟',sv:'Glömt lösenord?',fr:'Mot de passe oublié?',de:'Passwort vergessen?',es:'¿Olvidó su contraseña?',pt:'Esqueceu a senha?' },
  'auth_email':            { en:'Email',              ar:'البريد الإلكتروني',sv:'E-post',        fr:'Email',           de:'E-Mail',          es:'Correo',            pt:'Email' },
  'auth_password':         { en:'Password',           ar:'كلمة المرور',    sv:'Lösenord',        fr:'Mot de passe',    de:'Passwort',        es:'Contraseña',        pt:'Senha' },
  'auth_signing_in':       { en:'Signing in…',        ar:'جاري التسجيل…',  sv:'Loggar in…',      fr:'Connexion…',      de:'Anmeldung…',      es:'Iniciando…',        pt:'Entrando…' },

  // ── Header status ──
  'status_online':  { en:'online',  ar:'متصل',       sv:'online',    fr:'en ligne',  de:'online',    es:'en línea',  pt:'online' },

  // ── Footer ──
  'footer_newsletter':  { en:'Newsletter',    ar:'النشرة البريدية', sv:'Nyhetsbrev',  fr:'Newsletter',  de:'Newsletter',  es:'Boletín',     pt:'Newsletter' },
  'footer_subscribe':   { en:'Subscribe',     ar:'اشترك',           sv:'Prenumerera', fr:'S\'abonner',  de:'Abonnieren',  es:'Suscribirse', pt:'Inscrever' },
  'footer_subscribed':  { en:'Subscribed. Welcome aboard.', ar:'تم الاشتراك. مرحباً بك.', sv:'Prenumererad. Välkommen.', fr:'Abonné. Bienvenue.', de:'Abonniert. Willkommen.', es:'Suscrito. Bienvenido.', pt:'Inscrito. Bem-vindo.' },
  'footer_rights':      { en:'All rights reserved.', ar:'جميع الحقوق محفوظة.', sv:'Alla rättigheter förbehållna.', fr:'Tous droits réservés.', de:'Alle Rechte vorbehalten.', es:'Todos los derechos reservados.', pt:'Todos os direitos reservados.' },

  // ── Profile page ──
  'profile_title':        { en:'Profile',          ar:'الملف الشخصي',  sv:'Profil',         fr:'Profil',          de:'Profil',          es:'Perfil',          pt:'Perfil' },
  'profile_manage':       { en:'Manage your account, email addresses, security settings, and social connections.', ar:'إدارة حسابك وعناوين البريد الإلكتروني وإعدادات الأمان والاتصالات الاجتماعية.', sv:'Hantera ditt konto, e-postadresser, säkerhetsinställningar och sociala anslutningar.', fr:'Gérez votre compte, vos adresses email, vos paramètres de sécurité et vos connexions sociales.', de:'Verwalten Sie Ihr Konto, E-Mail-Adressen, Sicherheitseinstellungen und soziale Verbindungen.', es:'Administre su cuenta, direcciones de correo, configuración de seguridad y conexiones sociales.', pt:'Gerencie sua conta, endereços de email, configurações de segurança e conexões sociais.' },
  'profile_sign_in_prompt':{ en:'Sign in to view your profile', ar:'سجل الدخول لعرض ملفك الشخصي', sv:'Logga in för att se din profil', fr:'Connectez-vous pour voir votre profil', de:'Melden Sie sich an, um Ihr Profil zu sehen', es:'Inicie sesión para ver su perfil', pt:'Faça login para ver seu perfil' },
  'profile_email_addresses':{ en:'Email addresses', ar:'عناوين البريد الإلكتروني', sv:'E-postadresser', fr:'Adresses email', de:'E-Mail-Adressen', es:'Direcciones de correo', pt:'Endereços de email' },
  'profile_change_password':{ en:'Change password', ar:'تغيير كلمة المرور', sv:'Ändra lösenord', fr:'Changer le mot de passe', de:'Passwort ändern', es:'Cambiar contraseña', pt:'Alterar senha' },
  'profile_security_mfa':{ en:'Security & MFA', ar:'الأمان والمصادقة', sv:'Säkerhet & MFA', fr:'Sécurité & MFA', de:'Sicherheit & MFA', es:'Seguridad & MFA', pt:'Segurança & MFA' },
  'profile_social':     { en:'Social connections', ar:'الاتصالات الاجتماعية', sv:'Sociala anslutningar', fr:'Connexions sociales', de:'Soziale Verbindungen', es:'Conexiones sociales', pt:'Conexões sociais' },
  'profile_api_access': { en:'API access', ar:'الوصول إلى API', sv:'API-åtkomst', fr:'Accès API', de:'API-Zugriff', es:'Acceso API', pt:'Acesso API' },

  // ── Cookie consent ──
  'cookie_title':   { en:'This site uses cookies', ar:'يستخدم هذا الموقع ملفات تعريف الارتباط', sv:'Denna webbplats använder cookies', fr:'Ce site utilise des cookies', de:'Diese Website verwendet Cookies', es:'Este sitio usa cookies', pt:'Este site usa cookies' },
  'cookie_accept':  { en:'Accept',  ar:'قبول',     sv:'Acceptera', fr:'Accepter',  de:'Akzeptieren', es:'Aceptar',  pt:'Aceitar' },
  'cookie_deny':    { en:'Deny',    ar:'رفض',      sv:'Neka',      fr:'Refuser',   de:'Ablehnen',    es:'Rechazar', pt:'Recusar' },

  // ── Blog ──
  'blog_all_posts': { en:'All posts', ar:'جميع المنشورات', sv:'Alla inlägg', fr:'Tous les articles', de:'Alle Beiträge', es:'Todas las publicaciones', pt:'Todos os posts' },
  'blog_post_comment':{ en:'Post comment', ar:'نشر تعليق', sv:'Skicka kommentar', fr:'Publier', de:'Kommentieren', es:'Publicar', pt:'Publicar' },
  'blog_posting':   { en:'Posting…', ar:'جاري النشر…', sv:'Skickar…', fr:'Publication…', de:'Senden…', es:'Publicando…', pt:'Publicando…' },
  'blog_share_thoughts':{ en:'Share your thoughts...', ar:'شارك بأفكارك...', sv:'Dela dina tankar...', fr:'Partagez vos réflexions...', de:'Teilen Sie Ihre Gedanken...', es:'Comparta sus ideas...', pt:'Compartilhe seus pensamentos...' },

  // ── FAQ ──
  'faq_general':    { en:'General',  ar:'عام',       sv:'Allmänt',   fr:'Général',   de:'Allgemein',  es:'General',   pt:'Geral' },
  'faq_search':     { en:'Search the FAQ…', ar:'ابحث في الأسئلة…', sv:'Sök i FAQ…', fr:'Rechercher…', de:'FAQ durchsuchen…', es:'Buscar…', pt:'Pesquisar…' },
  'faq_no_results': { en:'No questions yet. Ask us one.', ar:'لا توجد أسئلة بعد. اسألنا.', sv:'Inga frågor än. Fråga oss.', fr:'Pas encore de questions. Posez-en une.', de:'Noch keine Fragen. Fragen Sie uns.', es:'Aún no hay preguntas. Pregúntenos.', pt:'Nenhuma pergunta ainda. Pergunte-nos.' },

  // ── CTA / General ──
  'cta_github':     { en:'View on GitHub', ar:'عرض على GitHub', sv:'Visa på GitHub', fr:'Voir sur GitHub', de:'Auf GitHub ansehen', es:'Ver en GitHub', pt:'Ver no GitHub' },
  'cta_contact':    { en:'Contact us', ar:'اتصل بنا', sv:'Kontakta oss', fr:'Contactez-nous', de:'Kontaktieren Sie uns', es:'Contáctenos', pt:'Fale conosco' },
  'cta_products':   { en:'Explore products', ar:'استكشف المنتجات', sv:'Utforska produkter', fr:'Explorer les produits', de:'Produkte entdecken', es:'Explorar productos', pt:'Explorar produtos' },
  'cta_about':      { en:'About the engineer', ar:'عن المهندس', sv:'Om ingenjören', fr:'À propos', de:'Über den Entwickler', es:'Sobre el ingeniero', pt:'Sobre o engenheiro' },
  'cta_meet_team':  { en:'Meet the team', ar:'تعرف على الفريق', sv:'Möt teamet', fr:'Rencontrez l\'équipe', de:'Team kennenlernen', es:'Conozca al equipo', pt:'Conheça a equipe' },

  // ── Theme ──
  'theme_light':  { en:'Light mode', ar:'الوضع الفاتح', sv:'Ljust läge', fr:'Mode clair', de:'Heller Modus', es:'Modo claro', pt:'Modo claro' },
  'theme_dark':   { en:'Dark mode',  ar:'الوضع الداكن', sv:'Mörkt läge', fr:'Mode sombre', de:'Dunkler Modus', es:'Modo oscuro', pt:'Modo escuro' },

  // ── Comments ──
  'comments_title':       { en:'Comments', ar:'تعليقات', sv:'Kommentarer', fr:'Commentaires', de:'Kommentare', es:'Comentarios', pt:'Comentários' },
  'comments_sign_in':     { en:'Sign in to join the conversation.', ar:'سجل الدخول للانضمام إلى المحادثة.', sv:'Logga in för att delta i konversationen.', fr:'Connectez-vous pour participer.', de:'Melden Sie sich an, um teilzunehmen.', es:'Inicie sesión para participar.', pt:'Faça login para participar.' },
  'comments_as':          { en:'Commenting as', ar:'التعليق باسم', sv:'Kommenterar som', fr:'Commentaire en tant que', de:'Kommentar als', es:'Comentando como', pt:'Comentando como' },
};

/** Resolve a single translation key for the active language. */
export function t(lang: LangCode, key: string): string {
  return T[key]?.[lang] || T[key]?.en || key;
}

/** Resolve with variable interpolation:  t('en', 'hello_name', { name: 'Ali' }) */
export function tx(lang: LangCode, key: string, vars: Record<string, string>): string {
  let s = t(lang, key);
  for (const [k, v] of Object.entries(vars)) {
    s = s.replace(`{${k}}`, v);
  }
  return s;
}
