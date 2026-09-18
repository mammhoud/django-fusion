/**
 * Project config — frontend view of the config cascade.
 *
 * `site-config.json` is generated from the project configs (configs/*.yml + Env
 * overrides) by `make config-front`. Regenerate it after editing configs:
 *
 *     cd projects/structa.cloud && make config-front
 *
 * Only YAML defaults are baked here — runtime env vars (PUBLIC_*) still win
 * in the browser/server, matching the backend cascade contract.
 */

import project from './site-config.json';

export interface SiteIdentity {
  name: string;
  aliases?: string[];
  primary_domain: string;
  domains: string[];
  allowed_hosts?: string[];
  default_email?: string;
  module?: string;
  wagtail_site_name?: string;
  base_url?: string;
  side?: string;
}

export interface AdminConfig {
  panel_path?: string;
  django_admin_path?: string;
  wagtailadmin_base_url?: string;
  csrf_trusted_origins?: string[];
  cors_allowed_origins?: string[];
}

export interface CssPanel {
  source?: string;
  compiled?: string;
  build_command?: string;
  served_at?: string;
  tailwind?: boolean;
  tokens_reference?: string;
}

export interface StaticPlan {
  read_dirs?: string[];
  output_dir?: string;
  media_dir?: string;
  bundle_stats?: string;
  css_path?: string;
  deploy?: Record<string, string>;
}

interface ProjectConfigData {
  SITE?: SiteIdentity;
  ADMIN?: AdminConfig;
  CSS_PANEL?: CssPanel;
  STATIC?: StaticPlan;
  DEBUG?: boolean;
  FUSION_RENDER_FIRST?: boolean;
  FRONTEND_PORT?: number;
}

const data = project as ProjectConfigData;

/** Site identity (from configs/site.yml + Env/_site.yml). */
export const siteConfig: SiteIdentity = data.SITE ?? { name: 'precis-main', primary_domain: 'structa.cloud', domains: ['structa.cloud'] };

/** Admin panel configuration (from configs/admin.yml). */
export const adminConfig: AdminConfig = data.ADMIN ?? {};

/** Design-system / CSS panel configuration (from configs/admin.yml). */
export const cssPanel: CssPanel = data.CSS_PANEL ?? {};

/** Static-files reference (from configs/defaults.yml → STATIC:). */
export const staticPlan: StaticPlan = data.STATIC ?? {};

/** Primary public domain, e.g. `structa.cloud`. */
export const primaryDomain: string = siteConfig.primary_domain ?? 'structa.cloud';

/** Canonical site origin, e.g. `https://structa.cloud`. */
export const siteUrl: string = `https://${primaryDomain}`;

/** Admin origin (backend-owned /admin + /django-admin). */
export const adminUrl: string =
  adminConfig.wagtailadmin_base_url ?? `https://${primaryDomain}`;

/** Compiled design-system stylesheet URL (served after collectstatic). */
export const fusionCssUrl: string =
  cssPanel.served_at ?? '/static/css/fusion.css';

/** Dual-mode render flag (mirrors backend FUSION_RENDER_FIRST). */
export const renderFirst: boolean = Boolean(data.FUSION_RENDER_FIRST);

/** Frontend dev port (matches docker-compose override). */
export const frontendPort: number = data.FRONTEND_PORT ?? 3000;

/** Build an absolute URL on the primary domain for a site path. */
export function absoluteUrl(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return new URL(normalized, siteUrl).href;
}
