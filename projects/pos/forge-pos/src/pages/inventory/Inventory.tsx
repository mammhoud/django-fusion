import { motion } from 'framer-motion';
import { useState, useEffect, useCallback, useMemo } from 'react';
import { useKeyboardTabNav } from '../../hooks/useKeyboardTabNav';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Ingredient, NewIngredient, InventoryTransaction, NewInventoryTransaction, InventoryAdjustment } from '../../types';
import PageLayout from '../../components/layout/PageLayout';
import { SkeletonTable, SkeletonList, SkeletonCard } from '../../components/layout/Skeleton';
import Card from '../../components/layout/Card';
import { useTranslation } from 'react-i18next';
import Modal from '../../components/layout/Modal';
import ConfirmDialog from '../../components/display/ConfirmDialog';
import StatusToast from '../../components/data/StatusToast';
import DataTable, { type Column } from '../../components/data/DataTable';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';

type Tab = 'stock' | 'transactions' | 'adjustments';

const TRANSACTION_TYPES = [
  { value: 'purchase', label: 'Purchase', color: 'bg-green-500' },
  { value: 'usage', label: 'Usage', color: 'bg-blue-500' },
  { value: 'waste', label: 'Waste', color: 'bg-red-500' },
  { value: 'adjustment', label: 'Adjustment', color: 'bg-yellow-500' },
  { value: 'return', label: 'Return', color: 'bg-secondary' },
];

export default function Inventory() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('stock');
  const [isLoading, setIsLoading] = useState(true);

  // Tab definition matching Transactions page pattern
  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'stock' as Tab, label: t('inventory.stockLevels'), icon: <span className="icon-[tabler--package] w-5 h-5" /> },
    { key: 'transactions' as Tab, label: t('inventory.transactions'), icon: <span className="icon-[tabler--history] w-5 h-5" /> },
    { key: 'adjustments' as Tab, label: t('inventory.adjustments'), icon: <span className="icon-[tabler--alert-triangle] w-5 h-5" /> },
  ];

  // ── Arrow-key tab nav ──
  const invTabKeys: Tab[] = tabs.map(t => t.key);
  const { onKeyDown: onInvTabKeyDown } = useKeyboardTabNav(invTabKeys, activeTab, setActiveTab);

  // Data states
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [transactions, setTransactions] = useState<InventoryTransaction[]>([]);
  const [adjustments, setAdjustments] = useState<InventoryAdjustment[]>([]);

  // Modal states
  const [showAddIngredient, setShowAddIngredient] = useState(false);
  const [showEditIngredient, setShowEditIngredient] = useState<Ingredient | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<Ingredient | null>(null);
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [ingredientFilter, setIngredientFilter] = useState<number | null>(null);

  // Search states
  const [stockSearch, setStockSearch] = useState('');

  // Form states
  const [newIngredient, setNewIngredient] = useState<NewIngredient>({
    name: '', unit: 'kg', current_quantity: 0, reorder_level: 0, reorder_quantity: 0, cost_per_unit: 0
  });
  const [editForm, setEditForm] = useState<Ingredient | null>(null);
  const [newTransaction, setNewTransaction] = useState<NewInventoryTransaction>({
    ingredient_id: 0, transaction_type: 'purchase', quantity_change: 0
  });
  const [adjustmentReason, setAdjustmentReason] = useState('');
  const [createdBy, setCreatedBy] = useState('');
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);

  // ---- Keyboard Shortcuts ----
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const key = e.key;
      const lower = key.toLowerCase();

      if (key === '?' || key === '/') {
        e.preventDefault();
        setShowShortcutHelp(prev => !prev);
        return;
      }

      if (key === '1') { setActiveTab('stock'); return; }
      if (key === '2') { setActiveTab('transactions'); return; }
      if (key === '3') { setActiveTab('adjustments'); return; }

      if (lower === 'a' && activeTab === 'stock') { setShowAddIngredient(true); return; }
      if (lower === '/' && activeTab === 'stock') {
        e.preventDefault();
        document.querySelector<HTMLInputElement>('input[placeholder]')?.focus();
        return;
      }
      if (lower === 'n' && activeTab === 'transactions') { setShowAddTransaction(true); return; }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab]);

  const loadData = useCallback(async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [ingredientsRes, transactionsRes, adjustmentsRes] = await Promise.all([
        invoke<Ingredient[]>('get_ingredients', { includeInactive: true }),
        invoke<InventoryTransaction[]>('get_inventory_transactions', { ingredientId: null }),
        invoke<InventoryAdjustment[]>('get_inventory_adjustments', { ingredientId: null }),
      ]);
      setIngredients(ingredientsRes);
      setTransactions(transactionsRes);
      setAdjustments(adjustmentsRes);
    } catch (error) {
      console.error('Error loading inventory data:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  // ── Real-time inventory updates from other windows ──
  useEffect(() => {
    const unlisten = listen('inventory-changed', () => {
      loadData({ quiet: true });
    });
    return () => { unlisten.then(fn => fn()); };
  }, [loadData]);

  const showStatus = (type: 'success' | 'error', msg: string) => {
    setToast({ type, message: msg });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Derived Stats ──
  const activeIngredients = useMemo(() => ingredients.filter(i => i.is_active), [ingredients]);

  const totalStockValue = useMemo(() =>
    activeIngredients.reduce((sum, ing) => sum + (ing.current_quantity * ing.cost_per_unit), 0),
  [activeIngredients]);

  const avgCost = useMemo(() => {
    if (activeIngredients.length === 0) return 0;
    return activeIngredients.reduce((sum, ing) => sum + ing.cost_per_unit, 0) / activeIngredients.length;
  }, [activeIngredients]);

  const lowStockCount = useMemo(() =>
    activeIngredients.filter(i => i.current_quantity <= i.reorder_level && i.current_quantity > 0).length,
  [activeIngredients]);

  // Transaction period counts
  const now = new Date();
  const thisMonthTransactions = useMemo(() =>
    transactions.filter(tx => {
      const d = new Date(tx.created_at);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    }).length,
  [transactions]);

  const thisWeekTransactions = useMemo(() => {
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    return transactions.filter(tx => new Date(tx.created_at) >= weekAgo).length;
  }, [transactions]);

  // Filtered stock by search
  const filteredIngredients = useMemo(() => {
    if (!stockSearch.trim()) return ingredients;
    const q = stockSearch.toLowerCase().trim();
    return ingredients.filter(ing => ing.name.toLowerCase().includes(q));
  }, [ingredients, stockSearch]);

  // ── Ingredient CRUD ──
  const handleAddIngredient = async () => {
    if (!newIngredient.name.trim()) return;
    try {
      await invoke('add_ingredient', { ingredient: newIngredient });
      setShowAddIngredient(false);
      setNewIngredient({ name: '', unit: 'kg', current_quantity: 0, reorder_level: 0, reorder_quantity: 0, cost_per_unit: 0 });
      loadData({ quiet: true });
      showStatus('success', t('inventory.successAdded'));
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleUpdateIngredient = async () => {
    if (!editForm || !editForm.name.trim()) return;
    try {
      await invoke('update_ingredient', {
        id: editForm.id,
        update: {
          name: editForm.name,
          unit: editForm.unit,
          current_quantity: editForm.current_quantity,
          reorder_level: editForm.reorder_level,
          reorder_quantity: editForm.reorder_quantity,
          cost_per_unit: editForm.cost_per_unit,
        }
      });
      setShowEditIngredient(null);
      setEditForm(null);
      loadData({ quiet: true });
      showStatus('success', t('inventory.successUpdated'));
    } catch (e) { showStatus('error', String(e)); }
  };

  const handleDeleteIngredient = async () => {
    if (!showDeleteConfirm) return;
    try {
      await invoke('soft_delete_ingredient', { id: showDeleteConfirm.id });
      setShowDeleteConfirm(null);
      loadData({ quiet: true });
      showStatus('success', t('inventory.successDeleted'));
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Transaction ──
  const handleAddTransaction = async () => {
    if (newTransaction.ingredient_id === 0 || newTransaction.quantity_change === 0) return;
    try {
      await invoke('add_inventory_transaction', {
        transaction: newTransaction,
        adjustmentReason: adjustmentReason || null,
        createdBy: createdBy || null,
      });
      setShowAddTransaction(false);
      setNewTransaction({ ingredient_id: 0, transaction_type: 'purchase', quantity_change: 0 });
      setAdjustmentReason('');
      loadData({ quiet: true });
      showStatus('success', t('inventory.successTransaction'));
    } catch (e) { showStatus('error', String(e)); }
  };

  const getTransactionColor = (type: string) => {
    return TRANSACTION_TYPES.find(t => t.value === type)?.color || 'bg-gray-500';
  };

  const getStockStatus = (ing: Ingredient) => {
    if (ing.current_quantity <= 0) return { color: 'text-red-500', bg: 'bg-red-100 dark:bg-red-900/20', label: t('inventory.outOfStock') };
    if (ing.current_quantity <= ing.reorder_level) return { color: 'text-yellow-500', bg: 'bg-yellow-100 dark:bg-yellow-900/20', label: t('inventory.lowStock') };
    return { color: 'text-green-500', bg: 'bg-green-100 dark:bg-green-900/20', label: t('inventory.inStock') };
  };

  const filteredTransactions = ingredientFilter
    ? transactions.filter(t => t.ingredient_id === ingredientFilter)
    : transactions;

  const transactionColumns = useMemo((): Column<InventoryTransaction>[] => [
    {
      key: 'type', label: 'Type', colSpan: 2,
      render: (tx) => {
        const colors: Record<string, string> = { purchase: 'bg-green-500', usage: 'bg-blue-500', waste: 'bg-red-500', adjustment: 'bg-yellow-500', return: 'bg-secondary' };
        const ing = ingredients.find(i => i.id === tx.ingredient_id);
        return <div className="flex items-center gap-2"><span className={`w-2 h-2 rounded-full ${colors[tx.transaction_type] || 'bg-gray-500'}`} /><span className="capitalize font-medium">{tx.transaction_type}</span><span className="text-slate-500 text-sm ml-1">— {ing?.name || `#${tx.ingredient_id}`}</span></div>;
      }
    },
    {
      key: 'quantity', label: 'Qty', colSpan: 1, sortable: true,
      render: (tx) => {
        const ing = ingredients.find(i => i.id === tx.ingredient_id);
        return <span className={`font-semibold ${tx.quantity_change >= 0 ? 'text-green-500' : 'text-red-500'}`}>{tx.quantity_change >= 0 ? '+' : ''}{tx.quantity_change} {ing?.unit || ''}</span>;
      }
    },
    {
      key: 'note', label: 'Note', colSpan: 1, hideOnMobile: true,
      render: (tx) => tx.note ? <span className="text-slate-500 italic text-sm">"{tx.note}"</span> : <span className="text-slate-400 text-sm">—</span>
    },
    {
      key: 'date', label: 'Date', colSpan: 1, sortable: true,
      render: (tx) => <span className="text-slate-400 text-xs">{new Date(tx.created_at).toLocaleDateString()}</span>
    },
  ], [ingredients]);

  if (isLoading) {
    return (
      <PageLayout title={t('inventory.title')}>
        <div className="space-y-6">
          <SkeletonCard count={4} />
          <SkeletonList items={5} />
          <SkeletonTable rows={6} columns={6} />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={<><span className="icon-[tabler--package] text-success" /> {t('inventory.title')}</>}
      background="bg-linear-to-br from-slate-100 via-success/10 to-slate-100 dark:from-slate-900 dark:via-success/10 dark:to-slate-900"
    >
      {/* Tab Navigation — matching Transactions page pattern */}
      <nav className="tabs tabs-boxed gap-1 mb-6 overflow-x-auto" aria-label="Inventory tabs" role="tablist" data-tab-prefix="inv-tab" onKeyDown={onInvTabKeyDown}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            type="button"
            role="tab"
            id={`inv-tab-${tab.key}`}
            aria-controls={`inv-panel-${tab.key}`}
            aria-selected={activeTab === tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`tab ${activeTab === tab.key ? 'tab-active' : ''}`}
          >
            {tab.icon}
            <span className="text-sm sm:text-base">{tab.label}</span>
          </button>
        ))}
      </nav>

      {/* Tab Content with staggered animation */}
      <motion.div
        key={activeTab}
        role="tabpanel"
        id={`inv-panel-${activeTab}`}
        aria-labelledby={`inv-tab-${activeTab}`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {/* ========== TAB 1: STOCK LEVELS ========== */}
        {activeTab === 'stock' && (
          <div className="space-y-6">
            {/* Compact Summary Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.totalIngredients')}</span>
                  <span className="text-lg font-bold text-base-content">{activeIngredients.length}</span>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.stockValue')}</span>
                  <span className="text-lg font-bold text-primary">
                    {totalStockValue.toFixed(2)}
                  </span>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.avgCost')}</span>
                  <span className="text-lg font-bold text-base-content">{avgCost.toFixed(2)}</span>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.lowStockItems')}</span>
                  <span className="text-lg font-bold text-yellow-500">{lowStockCount}</span>
                </div>
              </Card>
            </div>

            {/* Inline heading + search + add button */}
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-base-content shrink-0">{t('inventory.allIngredients')}</h2>
              <div className="relative flex-1 max-w-56">
                <span className="icon-[tabler--search] absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-base-content/50" />
                <input
                  type="text"
                  value={stockSearch}
                  onChange={e => setStockSearch(e.target.value)}
                  placeholder={t('inventory.searchIngredient')}
                  className="input input-bordered w-full h-8 text-xs pl-8"
                />
                {stockSearch && (
                  <button
                    onClick={() => setStockSearch('')}
                    className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors"
                  >
                    <span className="icon-[tabler--x] w-3 h-3" />
                  </button>
                )}
              </div>
              <button
                onClick={() => setShowAddIngredient(true)}
                className="btn btn-success btn-sm gap-1 shrink-0"
              >
                <span className="icon-[tabler--plus] w-3.5 h-3.5" />
                <span className="text-xs">{t('inventory.addIngredient')}</span>
              </button>
            </div>

            {/* Ingredient list */}
            {ingredients.length > 0 && filteredIngredients.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--search] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('inventory.noStockMatch')}</p>
                <button
                  onClick={() => setStockSearch('')}
                  className="text-sm font-medium text-primary dark:text-primary/80 hover:underline transition-colors"
                >
                  {t('common.clear')}
                </button>
              </div>
            ) : (
              <div className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl overflow-hidden">
                {/* Header */}
                <div className="hidden sm:grid grid-cols-12 gap-4 p-4 border-b border-base-300/50 text-base-content font-semibold text-sm">
                  <div className="col-span-3">{t('inventory.name')}</div>
                  <div className="col-span-1 text-center">{t('inventory.unit')}</div>
                  <div className="col-span-2 text-right">{t('inventory.stock')}</div>
                  <div className="col-span-2 text-right">{t('inventory.reorderLevel')}</div>
                  <div className="col-span-2 text-right">{t('inventory.costPerUnit')}</div>
                  <div className="col-span-2 text-center">{t('inventory.status')}</div>
                </div>

                {filteredIngredients.map((ing) => {
                  const status = getStockStatus(ing);
                  return (
                    <motion.div
                      key={ing.id}
                      initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                      className={`sm:grid sm:grid-cols-12 gap-4 p-4 border-b border-base-300/50 
                        hover:bg-base-200/50 transition-colors ${!ing.is_active ? 'opacity-50' : ''}`}
                    >
                      {/* Mobile */}
                      <div className="sm:hidden flex justify-between items-center mb-2">
                        <span className="font-semibold text-base-content">{ing.name}</span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${status.bg} ${status.color}`}>
                          {status.label}
                        </span>
                      </div>
                      <div className="sm:hidden text-sm text-base-content/60 space-y-1 mb-2">
                        <div className="flex justify-between">
                          <span>{t('inventory.stock')}: <strong>{ing.current_quantity} {ing.unit}</strong></span>
                          <span>{t('inventory.costPerUnit')}: {ing.cost_per_unit.toFixed(2)}</span>
                        </div>
                      </div>
                      <div className="sm:hidden flex gap-2 mb-1">
                        <button onClick={() => { setShowEditIngredient(ing); setEditForm({ ...ing }); }}
                          className="text-primary hover:text-primary/70 p-1"><span className="icon-[tabler--pencil]" /></button>
                        <button onClick={() => {
                          setNewTransaction(prev => ({ ...prev, ingredient_id: ing.id }));
                          setShowAddTransaction(true);
                        }} className="text-success hover:text-success/80 p-1"><span className="icon-[tabler--plus]" /></button>
                        {ing.is_active && (
                          <button onClick={() => setShowDeleteConfirm(ing)} className="text-error hover:text-error/70 p-1"><span className="icon-[tabler--trash]" /></button>
                        )}
                      </div>

                      {/* Desktop */}
                      <div className="hidden sm:block col-span-3 text-base-content font-medium">{ing.name}</div>
                      <div className="hidden sm:block col-span-1 text-center text-base-content/60">{ing.unit}</div>
                      <div className="hidden sm:block col-span-2 text-right text-base-content font-medium">{ing.current_quantity}</div>
                      <div className="hidden sm:block col-span-2 text-right text-base-content/60">{ing.reorder_level}</div>
                      <div className="hidden sm:block col-span-2 text-right text-base-content/60">{ing.cost_per_unit.toFixed(2)}</div>
                      <div className="hidden sm:flex col-span-2 items-center justify-center gap-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${status.bg} ${status.color}`}>
                          {status.label}
                        </span>
                        <button onClick={() => { setShowEditIngredient(ing); setEditForm({ ...ing }); }}
                          className="text-primary hover:text-primary/70 p-1" title={t('common.edit')}><span className="icon-[tabler--pencil]" /></button>
                        <button onClick={() => {
                          setNewTransaction(prev => ({ ...prev, ingredient_id: ing.id }));
                          setShowAddTransaction(true);
                        }} className="text-success hover:text-success/80 p-1" title={t('inventory.recordTransaction')}><span className="icon-[tabler--plus]" /></button>
                        {ing.is_active && (
                          <button onClick={() => setShowDeleteConfirm(ing)} className="text-error hover:text-error/70 p-1" title={t('common.deactivate')}><span className="icon-[tabler--trash]" /></button>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
                {ingredients.length === 0 && (
                  <div className="p-8 text-center text-base-content/60">{t('inventory.noIngredients')}</div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ========== TAB 2: TRANSACTIONS ========== */}
        {activeTab === 'transactions' && (
          <div className="space-y-6">
            {/* Compact Summary Cards */}
            <div className="grid grid-cols-3 gap-3">
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.totalIngredients')}</span>
                  <span className="text-lg font-bold text-base-content">{transactions.length}</span>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.thisMonthTransactions')}</span>
                  <span className="text-lg font-bold text-primary">{thisMonthTransactions}</span>
                </div>
              </Card>
              <Card padding="sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-base-content/60">{t('inventory.thisWeekTransactions')}</span>
                  <span className="text-lg font-bold text-info">{thisWeekTransactions}</span>
                </div>
              </Card>
            </div>

            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-sm font-semibold text-base-content shrink-0">{t('inventory.transactionLog')}</h2>
              <div className="flex flex-wrap items-center gap-1.5 flex-1">
                <button
                  onClick={() => setIngredientFilter(null)}
                  className={`badge badge-sm cursor-pointer transition-all ${ingredientFilter === null ? 'badge-primary badge-soft' : 'badge-ghost hover:badge-soft hover:badge-primary'}`}
                >
                  {t('inventory.allIngredientsFilter') || 'All'}
                </button>
                {ingredients.slice(0, 12).map(ing => (
                  <button
                    key={ing.id}
                    onClick={() => setIngredientFilter(ingredientFilter === ing.id ? null : ing.id)}
                    className={`badge badge-sm cursor-pointer transition-all ${ingredientFilter === ing.id ? 'badge-primary badge-soft' : 'badge-ghost hover:badge-soft hover:badge-primary'}`}
                  >
                    {ing.name}
                  </button>
                ))}
                {ingredients.length > 12 && (
                  <span className="text-[10px] text-base-content/30">+{ingredients.length - 12} more</span>
                )}
              </div>
              <button
                onClick={() => setShowAddTransaction(true)}
                className="btn btn-success btn-sm gap-1 shrink-0"
              >
                <span className="icon-[tabler--plus] w-3.5 h-3.5" />
                <span className="text-xs">{t('inventory.recordTransaction')}</span>
              </button>
            </div>

            <DataTable
              columns={transactionColumns}
              data={filteredTransactions}
              keyExtractor={tx => tx.id}
              emptyMessage={t('inventory.noTransactions')}
              mobileRender={(tx) => {
                const ing = ingredients.find(i => i.id === tx.ingredient_id);
                return (
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${getTransactionColor(tx.transaction_type)}`} />
                      <span className="font-medium capitalize text-base-content">{tx.transaction_type}</span>
                      <span className="text-slate-500 text-sm">— {ing?.name || `ID: ${tx.ingredient_id}`}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={`font-semibold ${tx.quantity_change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {tx.quantity_change >= 0 ? '+' : ''}{tx.quantity_change} {ing?.unit || ''}
                      </span>
                      <span className="text-slate-400 text-xs">{new Date(tx.created_at).toLocaleDateString()}</span>
                    </div>
                    {tx.note && <span className="text-slate-500 italic text-xs">"{tx.note}"</span>}
                  </div>
                );
              }}
            />
          </div>
        )}

        {/* ========== TAB 3: ADJUSTMENTS ========== */}
        {activeTab === 'adjustments' && (
          <div className="space-y-6">
            {/* Tab-specific Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card>
                <h2 className="text-base-content/60 text-sm">{t('inventory.totalAdjustments')}</h2>
                <p className="text-2xl font-bold text-base-content">{adjustments.length}</p>
              </Card>
                <Card>
                <h2 className="text-base-content/60 text-sm">{t('inventory.uniqueIngredients')}</h2>
                <p className="text-2xl font-bold text-primary dark:text-primary/80">
                  {new Set(adjustments.map(a => a.ingredient_id)).size}
                </p>
              </Card>
            </div>

            <h2 className="text-lg font-semibold text-base-content">{t('inventory.manualAdjustments')}</h2>
            <div className="space-y-3">
              {adjustments.length === 0 && (
                <div className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-8 text-center text-base-content/60">
                  {t('inventory.noAdjustments')}
                </div>
              )}
              {adjustments.map((adj) => {
                const ing = ingredients.find(i => i.id === adj.ingredient_id);
                return (
                  <motion.div
                    key={adj.id}
                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                    className="bg-base-100/70 backdrop-blur-md border border-white/20 dark:border-white/10 rounded-xl p-4"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-base-content font-medium">{ing?.name || `ID: ${adj.ingredient_id}`}</span>
                        <div className="text-sm text-base-content/60 mt-1">
                          {adj.previous_quantity} → <strong>{adj.new_quantity}</strong> {ing?.unit || ''}
                        </div>
                        <p className="text-sm text-base-content/50 mt-1 italic">"{adj.reason}"</p>
                      </div>
                      <div className="text-right text-xs text-slate-400">
                        <div>{new Date(adj.created_at).toLocaleDateString()}</div>
                        {adj.created_by && <div className="mt-1 text-slate-500">by {adj.created_by}</div>}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </motion.div>

      <Modal
        isOpen={showAddIngredient}
        onClose={() => setShowAddIngredient(false)}
        title={t('inventory.addIngredientTitle')}
        footer={<>
          <button onClick={() => setShowAddIngredient(false)} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleAddIngredient} disabled={!newIngredient.name.trim()}
            className="flex-1 py-2.5 rounded-lg bg-success text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <span className="icon-[tabler--device-floppy]" /> {t('inventory.addIngredient')}
          </button>
        </>}
      >
        <div><label className="block text-base-content/80 mb-1 text-sm">Name *</label>
          <input type="text" value={newIngredient.name} onChange={e => setNewIngredient(p => ({ ...p, name: e.target.value }))}
            className="input input-bordered w-full" /></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div><label className="block text-base-content/80 mb-1 text-sm">Unit *</label>
            <input type="text" value={newIngredient.unit} onChange={e => setNewIngredient(p => ({ ...p, unit: e.target.value }))}
              className="input input-bordered w-full" /></div>
          <div><label className="block text-base-content/80 mb-1 text-sm">Current Quantity</label>
            <input type="number" step="0.1" min="0" value={newIngredient.current_quantity} onChange={e => setNewIngredient(p => ({ ...p, current_quantity: Number(e.target.value) }))}
              className="input input-bordered w-full" /></div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <div><label className="block text-base-content/80 mb-1 text-sm">Reorder Level</label>
            <input type="number" step="0.1" min="0" value={newIngredient.reorder_level} onChange={e => setNewIngredient(p => ({ ...p, reorder_level: Number(e.target.value) }))}
              className="input input-bordered w-full" /></div>
          <div><label className="block text-base-content/80 mb-1 text-sm">Reorder Qty</label>
            <input type="number" step="0.1" min="0" value={newIngredient.reorder_quantity} onChange={e => setNewIngredient(p => ({ ...p, reorder_quantity: Number(e.target.value) }))}
              className="input input-bordered w-full" /></div>
          <div><label className="block text-base-content/80 mb-1 text-sm">Cost/Unit</label>
            <input type="number" step="0.01" min="0" value={newIngredient.cost_per_unit} onChange={e => setNewIngredient(p => ({ ...p, cost_per_unit: Number(e.target.value) }))}
              className="input input-bordered w-full" /></div>
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditIngredient && !!editForm}
        onClose={() => { setShowEditIngredient(null); setEditForm(null); }}
        title={t('inventory.editIngredientTitle')}
        footer={<>
          <button onClick={() => { setShowEditIngredient(null); setEditForm(null); }} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleUpdateIngredient} className="flex-1 py-2.5 rounded-lg bg-primary text-primary-content font-semibold flex items-center justify-center gap-2"><span className="icon-[tabler--device-floppy]" /> {t('common.update')}</button>
        </>}
      >
        {editForm && (<>
          <div><label className="block text-base-content/80 mb-1 text-sm">Name</label>
            <input type="text" value={editForm.name} onChange={e => setEditForm(p => ({ ...p!, name: e.target.value }))}
              className="input input-bordered w-full" /></div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div><label className="block text-base-content/80 mb-1 text-sm">Unit</label>
              <input type="text" value={editForm.unit} onChange={e => setEditForm(p => ({ ...p!, unit: e.target.value }))}
                className="input input-bordered w-full" /></div>
            <div><label className="block text-base-content/80 mb-1 text-sm">Stock</label>
              <input type="number" step="0.1" value={editForm.current_quantity} onChange={e => setEditForm(p => ({ ...p!, current_quantity: Number(e.target.value) }))}
                className="input input-bordered w-full" /></div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            <div><label className="block text-base-content/80 mb-1 text-sm">Reorder Level</label>
              <input type="number" step="0.1" value={editForm.reorder_level} onChange={e => setEditForm(p => ({ ...p!, reorder_level: Number(e.target.value) }))}
                className="input input-bordered w-full" /></div>
            <div><label className="block text-base-content/80 mb-1 text-sm">Reorder Qty</label>
              <input type="number" step="0.1" value={editForm.reorder_quantity} onChange={e => setEditForm(p => ({ ...p!, reorder_quantity: Number(e.target.value) }))}
                className="input input-bordered w-full" /></div>
            <div><label className="block text-base-content/80 mb-1 text-sm">Cost/Unit</label>
              <input type="number" step="0.01" value={editForm.cost_per_unit} onChange={e => setEditForm(p => ({ ...p!, cost_per_unit: Number(e.target.value) }))}
                className="input input-bordered w-full" /></div>
          </div>
        </>)}
      </Modal>

      <ConfirmDialog
        isOpen={!!showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(null)}
        onConfirm={handleDeleteIngredient}
        title={t('inventory.deactivateTitle')}
        message={t('inventory.deactivateConfirm')}
        itemName={showDeleteConfirm?.name || ''}
      />

      <Modal
        isOpen={showAddTransaction}
        onClose={() => setShowAddTransaction(false)}
        title={t('inventory.recordTitle')}
        footer={<>
          <button onClick={() => setShowAddTransaction(false)} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleAddTransaction} disabled={newTransaction.ingredient_id === 0 || newTransaction.quantity_change === 0}
            className="flex-1 py-2.5 rounded-lg bg-success text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2"><span className="icon-[tabler--device-floppy]" /> {t('inventory.recordTransaction')}</button>
        </>}
      >
        <div><label className="block text-base-content/80 mb-1 text-sm">{t('inventory.ingredient')} *</label>
          <select value={newTransaction.ingredient_id} onChange={e => setNewTransaction(p => ({ ...p, ingredient_id: Number(e.target.value) }))}
            className="input input-bordered w-full">
            <option value={0}>{t('inventory.selectIngredient')}</option>
            {ingredients.filter(i => i.is_active).map(ing => (
              <option key={ing.id} value={ing.id}>{ing.name} ({ing.current_quantity} {ing.unit})</option>
            ))}
          </select></div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div><label className="block text-base-content/80 mb-1 text-sm">{t('inventory.type')} *</label>
            <select value={newTransaction.transaction_type} onChange={e => setNewTransaction(p => ({ ...p, transaction_type: e.target.value }))}
              className="input input-bordered w-full">
              {TRANSACTION_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select></div>
          <div><label className="block text-base-content/80 mb-1 text-sm">{t('inventory.quantityChange')} *</label>
            <input type="number" step="0.1" value={newTransaction.quantity_change}
              onChange={e => setNewTransaction(p => ({ ...p, quantity_change: Number(e.target.value) }))}
              placeholder={t('inventory.quantityPlaceholder')}
              className="input input-bordered w-full" />
            <p className="text-xs text-base-content/50 mt-1">{t('inventory.positiveHint')}</p>
          </div>
        </div>
        <div><label className="block text-base-content/80 mb-1 text-sm">{t('inventory.note')}</label>
          <input type="text" value={newTransaction.note || ''} onChange={e => setNewTransaction(p => ({ ...p, note: e.target.value || null }))}
            className="input input-bordered w-full" /></div>
        {newTransaction.transaction_type === 'adjustment' && (
          <>
            <div><label className="block text-base-content/80 mb-1 text-sm">{t('inventory.adjustmentReason')} *</label>
              <input type="text" value={adjustmentReason} onChange={e => setAdjustmentReason(e.target.value)}
                className="input input-bordered w-full" /></div>
            <div><label className="block text-base-content/80 mb-1 text-sm">{t('inventory.createdBy')}</label>
              <input type="text" value={createdBy} onChange={e => setCreatedBy(e.target.value)}
                className="input input-bordered w-full" /></div>
          </>
        )}
      </Modal>

      <StatusToast type={toast?.type || 'success'} message={toast?.message || ''} visible={!!toast} onDismiss={() => setToast(null)} />

      <KeyboardShortcutsModal isOpen={showShortcutHelp} onClose={() => setShowShortcutHelp(false)} />
    </PageLayout>
  );
}
