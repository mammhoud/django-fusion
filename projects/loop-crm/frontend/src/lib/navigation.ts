export interface NavigationChild {
  id: string;
  label: string;
  href: string;
  active?: boolean;
}

export interface NavigationModule {
  id: string;
  label: string;
  href: string;
  icon: string;
  description: string;
  children: NavigationChild[];
  active?: boolean;
}

/**
 * Build-time route contract used for Astro's first paint. The backend
 * `/api/v1/navigation/`/HTMX fragment is authoritative at runtime; this list
 * only lets static Astro pages compile before Django is running.
 */
export const NAVIGATION: NavigationModule[] = [
  { id: 'overview', label: 'Overview', href: '/overview/', icon: 'overview', description: 'Revenue, publishing, and attribution at a glance.', children: [] },
  { id: 'crm', label: 'CRM', href: '/crm/', icon: 'crm', description: 'Companies, contacts, pipeline, and relationship history.', children: [
    { id: 'companies', label: 'Companies', href: '/crm/companies/' },
    { id: 'contacts', label: 'Contacts', href: '/crm/contacts/' },
    { id: 'pipelines', label: 'Pipelines', href: '/crm/pipelines/' },
    { id: 'deals', label: 'Deals', href: '/crm/deals/' },
    { id: 'activities', label: 'Activities', href: '/crm/activities/' },
  ] },
  { id: 'marketing', label: 'Marketing', href: '/marketing/', icon: 'marketing', description: 'Campaigns, content calendar, channels, and media.', children: [
    { id: 'calendar', label: 'Content calendar', href: '/marketing/calendar/' },
    { id: 'campaigns', label: 'Campaigns', href: '/marketing/campaigns/' },
    { id: 'channels', label: 'Channels', href: '/marketing/channels/' },
    { id: 'media', label: 'Media library', href: '/marketing/media/' },
  ] },
  { id: 'finance', label: 'Finance', href: '/finance/', icon: 'finance', description: 'Invoices, payments, recognized revenue, and cash visibility.', children: [
    { id: 'invoices', label: 'Invoices', href: '/finance/invoices/' },
    { id: 'payments', label: 'Payments', href: '/finance/payments/' },
    { id: 'revenue', label: 'Recognized revenue', href: '/finance/revenue/' },
  ] },
  { id: 'attribution', label: 'Attribution', href: '/attribution/', icon: 'attribution', description: 'Connect social touchpoints to pipeline revenue.', children: [
    { id: 'touchpoints', label: 'Touchpoints', href: '/attribution/touchpoints/' },
    { id: 'reports', label: 'Revenue reports', href: '/attribution/reports/' },
  ] },
  { id: 'tasks', label: 'Tasks', href: '/tasks/', icon: 'tasks', description: 'Background job history — workflows, attribution, publishing, and finance.', children: [] },
  { id: 'workspace', label: 'Workspace', href: '/settings/', icon: 'workspace', description: 'Members, workflows, integrations, and audit history.', children: [
    { id: 'members', label: 'Members & roles', href: '/settings/members/' },
    { id: 'workflows', label: 'Workflows', href: '/settings/workflows/' },
    { id: 'integrations', label: 'Integrations', href: '/settings/integrations/' },
    { id: 'custom-fields', label: 'Custom fields', href: '/settings/custom-fields/' },
    { id: 'audit', label: 'Audit log', href: '/settings/audit/' },
  ] },
];

export function navigationFor(pathname: string): NavigationModule[] {
  return NAVIGATION.map((module) => ({
    ...module,
    children: module.children.map((child) => ({ ...child, active: pathname === child.href || pathname.startsWith(child.href) })),
    active: pathname === module.href || (module.href !== '/' && pathname.startsWith(module.href)),
  }));
}

export function breadcrumbsFor(pathname: string, title: string) {
  if (pathname === '/') return [];
  for (const module of NAVIGATION.slice(1)) {
    if (pathname === module.href || pathname.startsWith(module.href)) {
      return [
        { label: 'Home', href: '/' },
        ...(pathname !== module.href ? [{ label: module.label, href: module.href }] : []),
        { label: title, href: pathname },
      ];
    }
  }
  return [{ label: 'Home', href: '/' }, { label: title, href: pathname }];
}
