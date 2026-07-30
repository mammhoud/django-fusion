import Modal from '../layout/Modal';
import { useTranslation } from 'react-i18next';

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function KeyboardShortcutsModal({ isOpen, onClose }: KeyboardShortcutsModalProps) {
  const { t } = useTranslation();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={t('transactions.shortcutTitle')}
      size="xl"
    >
      <div className="space-y-3 max-h-[60vh] overflow-y-auto px-1">
        {/* Global Navigation Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <span className="w-1 h-4 rounded-full bg-primary" />
            Navigation
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-slate-50/50 dark:bg-slate-800/30 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">Go to Home / Dashboard</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">G</kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">Go to New Sale</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">S</kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">Go to Settings</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">⌘ + ,</kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">Toggle theme dark/light</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">T</kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">Toggle keyboard shortcuts help</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">?</kbd>
            </div>
          </div>
        </div>

        {/* Sorting Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <span className="w-1 h-4 rounded-full bg-indigo-500" />
            {t('transactions.shortcutSortTitle')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5">
            {[
              { key: 'N', label: `${t('transactions.sortName')} (${t('transactions.sortProductStats')} & ${t('transactions.sortRelated')})` },
              { key: 'Q', label: `${t('transactions.sortQuantity')} (${t('transactions.sortProductStats')})` },
              { key: 'U', label: `${t('transactions.sortUnits')} (${t('transactions.sortRelated')})` },
              { key: 'R', label: `${t('transactions.sortRevenue')} (${t('transactions.sortProductStats')} & ${t('transactions.sortRelated')})` },
              { key: 'D', label: `${t('transactions.sortDate')} (${t('transactions.invoices')})` },
              { key: 'A', label: `${t('transactions.sortAmount')} (${t('transactions.invoices')})` },
              { key: 'O', label: `${t('transactions.sortType')} (${t('transactions.invoices')})` },
            ].map(s => (
              <div key={s.key} className="flex items-center justify-between py-2">
                <span className="text-sm text-base-content/70">{s.label}</span>
                <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">
                  {s.key}
                </kbd>
              </div>
            ))}
          </div>
        </div>

        {/* Product Manager Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider">
            {t('productManager.title')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-blue-50/50 dark:bg-blue-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutPMAdd')}</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">A</kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutPMClose')}</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">Esc</kbd>
            </div>
          </div>
        </div>

        {/* Sale Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-primary uppercase tracking-wider">
            {t('transactions.title')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-violet-50/50 dark:bg-violet-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutTxTabNav')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50 font-mono">1 · 2 · 3 · 4</span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutTxFilters')}</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">F</kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutTxClearFilters')}</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">C</kbd>
            </div>
          </div>
        </div>

        {/* Reports Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider">
            {t('reports.title')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutReportsTabLabel')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50 font-mono">1-9 · 0 · -</span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutDatePresets')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">T</kbd>
                {' '}{t('reports.dateToday')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">W</kbd>
                {' '}{t('reports.date7Days')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">M</kbd>
                {' '}{t('reports.date30Days')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">R</kbd>
                {' '}{t('reports.dateThisMonth')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">C</kbd>
                {' '}{t('common.clear')}
              </span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutExport')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">P</kbd>
                {' '}{t('transactions.shortcutPdf')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">S</kbd>
                {' '}{t('common.csv')}
              </span>
            </div>
          </div>
        </div>

        {/* Inventory Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider">
            {t('inventory.title')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-amber-50/50 dark:bg-amber-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutTabNav')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">1</kbd>
                {' '}{t('inventory.stock')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">2</kbd>
                {' '}{t('inventory.transactions')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">3</kbd>
                {' '}{t('inventory.adjustments')}
              </span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutQuickActions')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">A</kbd>
                {' '}{t('common.add')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">/</kbd>
                {' '}{t('common.search')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">N</kbd>
                {' '}{t('transactions.shortcutRecord')}
              </span>
            </div>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">
            {t('analytics.title')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-purple-50/50 dark:bg-purple-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutHelpDesc')}</span>
              <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">?</kbd>
            </div>
          </div>
        </div>

        {/* Sale Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-primary uppercase tracking-wider">
            {t('sale.title')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-teal-50/50 dark:bg-teal-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('sale.orderType')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">1</kbd>
                {' '}{t('sale.dineIn')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">2</kbd>
                {' '}{t('sale.takeaway')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">3</kbd>
                {' '}{t('sale.delivery')}
              </span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutActionsRow')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">Enter</kbd>
                {' '}{t('transactions.shortcutSell')} ·{' '}
                <kbd className="px-1.5 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">Esc</kbd>
                {' '}{t('common.clear')}
              </span>
            </div>
          </div>
        </div>

        {/* Multi-Column Sort Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
            {t('transactions.shortcutMultiSortTitle')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5 bg-indigo-50/50 dark:bg-indigo-900/10 rounded-lg px-3 py-2">
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutShiftClick')}</span>
              <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">
                ⇧ + key
              </kbd>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutChainPriority')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                <span className="inline-flex items-center gap-1">
                  <span className="text-[10px] font-bold text-indigo-500 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-800/40 px-1 rounded">1</span>
                  <span className="text-[10px] font-bold text-indigo-500 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-800/40 px-1 rounded">2</span>
                  <span className="text-[10px] font-bold text-indigo-500 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-800/40 px-1 rounded">3</span>
                </span>
              </span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutRemoveFromChain')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">{t('transactions.shortcutPress')} <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">{t('common.clear')}</kbd></span>
            </div>
            <div className="flex items-center justify-between py-1.5">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutPerTab')}</span>
              <span className="text-[10px] text-slate-400 dark:text-white/50 font-mono">
                N/Q/R · N/U/R · D/A/O
              </span>
            </div>
          </div>
        </div>

        {/* General Section */}
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <span className="w-1 h-4 rounded-full bg-amber-500" />
            {t('transactions.shortcutGeneralTitle')}
          </h4>
          <div className="divide-y divide-slate-100 dark:divide-white/5">
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutHelpDesc')}</span>
              <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">
                ?
              </kbd>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutToggleSort')}</span>
              <span className="text-xs text-slate-400 dark:text-white/50">
                {t('transactions.shortcutPress')} <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">{t('transactions.shortcutSameKey')}</kbd>
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutPrevPage')}</span>
              <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">
                ←
              </kbd>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-base-content/70">{t('transactions.shortcutNextPage')}</span>
              <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">
                →
              </kbd>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-base-content/70">Focus search input</span>
              <kbd className="px-2 py-0.5 rounded bg-base-200/50 text-xs font-mono font-bold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-white/20">
                /
              </kbd>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
}
