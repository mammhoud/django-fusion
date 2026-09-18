/**
 * ProfileCard — the user profile island for the /account/profile/ road.
 *
 * Fetches the session-based /apis/me/ contract (identity + role + effective
 * capabilities) and renders it with the Loop-CRM tactical telemetry design.
 * The Django road renders the same shape in account/profile.html; both roads
 * share the payload contract and never expose tokens.
 */
import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';

interface MeUser {
  id: number;
  email: string;
  username: string;
  name: string;
  role: string;
  title: string;
  workspace_id: number | null;
  workspace_name: string | null;
  is_staff: boolean;
}

interface MePayload {
  user: MeUser;
  capabilities: {
    sales: boolean;
    marketing: boolean;
    revops: boolean;
    manage_deals: boolean;
    manage_posts: boolean;
  };
}

interface SecurityLink {
  label: string;
  href: string;
  note: string;
}

const SECURITY_LINKS: SecurityLink[] = [
  { label: 'Change password', href: '/accounts/password/change/', note: 'Rotate your account password' },
  { label: 'Manage email', href: '/accounts/email/', note: 'Add or remove email addresses' },
  { label: 'Connected accounts', href: '/accounts/social/connections/', note: 'Social sign-in connections' },
  { label: 'Sign out', href: '/accounts/logout/', note: 'End this session' },
];

const CAPABILITY_LABELS: Array<{ key: keyof MePayload['capabilities']; label: string }> = [
  { key: 'sales', label: 'Sales' },
  { key: 'marketing', label: 'Marketing' },
  { key: 'revops', label: 'RevOps' },
  { key: 'manage_deals', label: 'Manage deals' },
  { key: 'manage_posts', label: 'Manage posts' },
];

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  return parts
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('');
}

function RolePill({ role }: { role: string }) {
  return <span className="loop-profile__pill">{role.replace(/_/g, ' ')}</span>;
}

function Board() {
  const [status, setStatus] = useState<'loading' | 'error' | 'ready'>('loading');
  const [payload, setPayload] = useState<MePayload | null>(null);

  const load = useCallback(async () => {
    try {
      const response = await fetch('/apis/me/', { credentials: 'include' });
      if (response.status === 302 || response.status === 401 || response.redirected) {
        window.location.assign('/accounts/login/');
        return;
      }
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setPayload((await response.json()) as MePayload);
      setStatus('ready');
    } catch (err) {
      console.error('Profile load failed', err);
      setStatus('error');
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (status === 'loading') {
    return (
      <div className="loop-profile" aria-busy="true" aria-label="Loading profile">
        <div className="loop-profile__identity">
          <Skeleton className="loop-profile__avatar-skeleton" />
          <div><Skeleton className="loop-profile__line loop-profile__line--name" /><Skeleton className="loop-profile__line" /></div>
        </div>
        <div className="loop-profile__grid">
          <Skeleton className="loop-profile__card-skeleton" />
          <Skeleton className="loop-profile__card-skeleton" />
        </div>
      </div>
    );
  }

  if (status === 'error' || !payload) {
    return (
      <div className="loop-profile loop-profile__error">
        <strong>Could not load your profile.</strong>
        <p>The /apis/me/ endpoint did not respond. Check that the backend is running and you are signed in.</p>
        <Button type="button" variant="outline" onClick={() => { setStatus('loading'); void load(); }}>Retry</Button>
      </div>
    );
  }

  const { user, capabilities } = payload;

  return (
    <div className="loop-profile">
      <section className="loop-profile__identity" aria-label="Identity">
        <span className="loop-profile__avatar" aria-hidden="true">{initials(user.name || user.email)}</span>
        <div>
          <div className="loop-profile__name-row"><h2>{user.name || user.email}</h2><RolePill role={user.role} /></div>
          <p className="loop-profile__email">{user.email}{user.username && user.username !== user.email ? ` · @${user.username}` : ''}</p>
        </div>
      </section>

      <div className="loop-profile__grid">
        <Card className="loop-profile__card">
          <CardHeader>
            <CardTitle>Workspace</CardTitle>
            <CardDescription>Tenant scope resolved from your profile</CardDescription>
          </CardHeader>
          <CardContent>
            <strong className="loop-profile__value">{user.workspace_name ?? 'Unassigned'}</strong>
            <p className="loop-profile__copy">{user.title || 'No title set'}{user.is_staff ? ' · staff' : ''}</p>
          </CardContent>
        </Card>
        <Card className="loop-profile__card">
          <CardHeader>
            <CardTitle>Effective permissions</CardTitle>
            <CardDescription>Live role checks from the Django account</CardDescription>
          </CardHeader>
          <CardContent className="loop-profile__capabilities">
            {CAPABILITY_LABELS.map(({ key, label }) => (
              <span className="loop-profile__capability" key={key}>
                <span>{label}</span>
                <span className={capabilities[key] ? 'loop-profile__ok' : 'loop-profile__no'}>
                  {capabilities[key] ? 'allowed' : 'read only'}
                </span>
              </span>
            ))}
          </CardContent>
        </Card>
      </div>

      <Separator />

      <section className="loop-profile__security" aria-labelledby="profile-security-heading">
        <span className="loop-profile__kicker">Account management</span>
        <h3 id="profile-security-heading">Security & identity</h3>
        <div className="loop-profile__actions">
          {SECURITY_LINKS.map((link) => (
            <a className="loop-profile__action" href={link.href} key={link.href}>
              <strong>{link.label}</strong><span>{link.note}</span><b aria-hidden="true">→</b>
            </a>
          ))}
          <a className="loop-profile__action" href="/settings/members/">
            <strong>Members & roles</strong><span>Manage the workspace team</span><b aria-hidden="true">→</b>
          </a>
        </div>
      </section>
    </div>
  );
}

export default function ProfileCard() {
  return <Board />;
}
