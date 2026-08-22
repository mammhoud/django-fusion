import { useEffect, useMemo, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import PageLayout from '../../../components/layout/PageLayout';
import Card from '../../../components/ui/Card';
import FormModal from '../../../components/ui/FormModal';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';
import { Badge, badgeVariants } from '../../../components/ui/badge';
import type { VariantProps } from 'class-variance-authority';
import StatusToast from '../../../components/ui/StatusToast';
import { useStatusToast } from '../../../hooks/useStatusToast';

type BadgeTone = NonNullable<VariantProps<typeof badgeVariants>['variant']>;

/** Loyalty/reward badge — persisted via the Diesel `badges` table. */
interface RewardBadge {
  id: number;
  name: string;
  description: string;
  /** Remix icon suffix (rendered as `ri-{icon}`). */
  icon: string;
  /** Maps directly to the shared `<Badge variant={tone}>` variants. */
  tone: BadgeTone;
  /** Loyalty points a customer needs to earn this badge. */
  threshold: number;
  is_active: boolean;
}

/** Tone choices exposed in the picker — semantic + soft variants. */
const TONE_OPTIONS: { tone: BadgeTone; label: string }[] = [
  { tone: 'default', label: 'Verdigris' },
  { tone: 'success', label: 'Success' },
  { tone: 'warning', label: 'Warning' },
  { tone: 'info', label: 'Info' },
  { tone: 'neutral', label: 'Neutral' },
  { tone: 'soft', label: 'Soft verdigris' },
  { tone: 'soft-success', label: 'Soft success' },
  { tone: 'soft-warning', label: 'Soft warning' },
  { tone: 'soft-info', label: 'Soft info' },
  { tone: 'secondary', label: 'Secondary' },
];

const ICON_OPTIONS = [
  'star-smile-line',
  'award-line',
  'medal-line',
  'fire-line',
  'vip-crown-line',
  'sparkling-line',
  'trophy-line',
  'gem-line',
];

interface BadgeForm {
  name: string;
  description: string;
  icon: string;
  tone: BadgeTone;
  threshold: string;
  is_active: boolean;
}

const emptyForm: BadgeForm = {
  name: '',
  description: '',
  icon: ICON_OPTIONS[0],
  tone: 'default',
  threshold: '100',
  is_active: true,
};

export default function Badges() {
  const { t } = useTranslation();
  const [badges, setBadges] = useState<RewardBadge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');

  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<RewardBadge | null>(null);
  const [form, setForm] = useState<BadgeForm>(emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [toDelete, setToDelete] = useState<RewardBadge | null>(null);

  const { status, showSuccess, showError, dismiss } = useStatusToast();

  const loadBadges = async () => {
    try {
      setIsLoading(true);
      const data = await invoke<RewardBadge[]>('get_badges');
      setBadges(data ?? []);
    } catch (err) {
      showError(`${t('common.error', 'Error')}: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadBadges();
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return badges;
    return badges.filter((b) =>
      [b.name, b.description].join(' ').toLowerCase().includes(q),
    );
  }, [badges, search]);

  const openAdd = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowForm(true);
  };

  const openEdit = (badge: RewardBadge) => {
    setEditing(badge);
    setForm({
      name: badge.name,
      description: badge.description,
      icon: badge.icon,
      tone: badge.tone,
      threshold: String(badge.threshold),
      is_active: badge.is_active,
    });
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditing(null);
    setForm(emptyForm);
  };

  const handleSubmit = async () => {
    const threshold = Math.max(0, Number(form.threshold) || 0);
    if (!form.name.trim()) return;
    setIsSubmitting(true);

    try {
      const payload = {
        name: form.name.trim(),
        description: form.description.trim(),
        icon: form.icon,
        tone: form.tone,
        threshold,
        is_active: form.is_active,
      };
      if (editing) {
        await invoke<RewardBadge>('update_badge', { id: editing.id, update: payload });
      } else {
        await invoke<RewardBadge>('add_badge', { badge: payload });
      }
      showSuccess(editing ? t('common.saved') : t('badges.created', 'Badge created'));
      closeForm();
      await loadBadges();
    } catch (err) {
      showError(`${t('common.error', 'Error')}: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await invoke('delete_badge', { id: toDelete.id });
      setToDelete(null);
      showSuccess(t('common.deleted'));
      await loadBadges();
    } catch (err) {
      showError(`${t('common.error', 'Error')}: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  return (
    <PageLayout title={t('nav.badges', 'Rewards & Badges')}>
      <div className="space-y-4">
        {/* ── Title + search + add ── */}
        <div className="flex flex-wrap items-center gap-2">
          <h1 className="text-lg font-bold text-base-content shrink-0">
            {t('nav.badges', 'Rewards & Badges')}
          </h1>
          <div className="relative flex-1 max-w-64">
            <span className="ri-search-line absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-base-content/50" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t('badges.searchPlaceholder', 'Search badges…')}
              aria-label={t('badges.searchPlaceholder', 'Search badges')}
              className="input w-full h-8 text-xs pl-8"
            />
          </div>
          <span className="text-[11px] text-base-content/40 whitespace-nowrap shrink-0">
            {filtered.length}/{badges.length}
          </span>
          <button
            onClick={openAdd}
            className="btn btn-primary btn-sm gap-1 shrink-0 active:scale-[0.98] transition-transform"
          >
            <span className="ri-add-line ri-14px" />
            <span className="text-xs">{t('badges.addBadge', 'Add badge')}</span>
          </button>
        </div>

        {/* ── List ── */}
        {isLoading ? (
          <Card padding="2xl" center>
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full inline-block mb-2 animate-spin" />
            <p className="text-base-content/50 text-sm">{t('common.loading')}</p>
          </Card>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-14 h-14 mx-auto mb-3 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <span className="ri-award-line ri-24px" />
            </div>
            <p className="text-base-content/60">
              {search
                ? (t('common.noDataFound') || 'No matches found.')
                : t('badges.empty', 'No badges yet — add your first loyalty reward.')}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filtered.map((badge) => (
              <Card key={badge.id} padding="md" className="group">
                <div className="flex items-start justify-between gap-2">
                  <Badge variant={badge.tone} size="lg" className="gap-2">
                    <span className={`ri-${badge.icon}`} />
                    {badge.name}
                  </Badge>
                  <div className="flex gap-1">
                    <button
                      onClick={() => openEdit(badge)}
                      aria-label={t('common.edit')}
                      className="p-2 text-slate-600 hover:text-primary transition-colors"
                    >
                      <span className="ri-pencil-line" />
                    </button>
                    <button
                      onClick={() => setToDelete(badge)}
                      aria-label={t('common.delete')}
                      className="p-2 text-slate-600 hover:text-error transition-colors"
                    >
                      <span className="ri-delete-bin-line" />
                    </button>
                  </div>
                </div>

                {badge.description && (
                  <p className="mt-2 text-sm text-base-content/60">{badge.description}</p>
                )}

                <div className="mt-3 flex items-center justify-between text-xs">
                  <span className="inline-flex items-center gap-1 text-base-content/50">
                    <span className="ri-star-line text-amber-500" />
                    {t('badges.threshold', '{{points}} points', { points: badge.threshold })}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1 ${
                      badge.is_active ? 'text-success' : 'text-base-content/40'
                    }`}
                  >
                    <span className={`ri-${badge.is_active ? 'checkbox-circle-line' : 'indeterminate-circle-line'}`} />
                    {badge.is_active
                      ? t('badges.active', 'Active')
                      : t('badges.inactive', 'Inactive')}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* ── Add / Edit modal ── */}
      <FormModal
        isOpen={showForm}
        onClose={closeForm}
        title={editing ? t('badges.editTitle', 'Edit badge') : t('badges.addTitle', 'Add badge')}
        submitLabel={editing ? t('common.update') : t('common.add')}
        submitDisabled={!form.name.trim()}
        isSubmitting={isSubmitting}
        onSubmit={handleSubmit}
      >
        <div className="space-y-3">
          <div className="field">
            <label className="label text-xs">{t('badges.name', 'Name')}</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder={t('badges.namePlaceholder', 'Gold regular')}
              className="input w-full"
            />
          </div>
          <div className="field">
            <label className="label text-xs">{t('badges.description', 'Description')}</label>
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder={t('badges.descriptionPlaceholder', 'Earned after 10 visits')}
              className="input w-full"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="field">
              <label className="label text-xs">{t('badges.icon', 'Icon')}</label>
              <div className="flex flex-wrap gap-1.5">
                {ICON_OPTIONS.map((icon) => (
                  <button
                    key={icon}
                    type="button"
                    onClick={() => setForm({ ...form, icon })}
                    aria-label={icon}
                    className={`w-8 h-8 rounded-lg border flex items-center justify-center transition-all active:scale-95 ${
                      form.icon === icon
                        ? 'border-primary bg-primary/10 text-primary'
                        : 'border-base-300 text-base-content/60 hover:border-base-content/30'
                    }`}
                  >
                    <span className={`ri-${icon}`} />
                  </button>
                ))}
              </div>
            </div>
            <div className="field">
              <label className="label text-xs">{t('badges.tone', 'Tone')}</label>
              <select
                value={form.tone}
                onChange={(e) => setForm({ ...form, tone: e.target.value as BadgeTone })}
                className="select w-full"
              >
                {TONE_OPTIONS.map((opt) => (
                  <option key={opt.tone} value={opt.tone}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <div className="mt-2">
                <Badge variant={form.tone}>{form.name || 'Badge'}</Badge>
              </div>
            </div>
          </div>
          <div className="field">
            <label className="label text-xs">{t('badges.thresholdLabel', 'Loyalty points to earn')}</label>
            <input
              type="number"
              min="0"
              value={form.threshold}
              onChange={(e) => setForm({ ...form, threshold: e.target.value })}
              className="input w-full"
            />
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
              className="checkbox checkbox-primary checkbox-sm"
            />
            <span className="text-sm">{t('badges.activeLabel', 'Active')}</span>
          </label>
        </div>
      </FormModal>

      {/* ── Delete confirm ── */}
      <ConfirmDialog
        isOpen={!!toDelete}
        onClose={() => setToDelete(null)}
        onConfirm={handleDelete}
        title={t('badges.deleteTitle', 'Delete badge')}
        message={t('badges.deleteMessage', 'This will permanently remove the badge')}
        itemName={toDelete?.name ?? ''}
        confirmLabel={t('common.delete')}
      />

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}
