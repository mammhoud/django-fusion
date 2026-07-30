import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import { Recipe, NewRecipe, RecipeIngredient, NewRecipeIngredient, Product, Ingredient, Note } from '../../types';
import PageLayout from '../../components/layout/PageLayout';
import { SkeletonCard, SkeletonList } from '../../components/layout/Skeleton';
import { useTranslation } from 'react-i18next';
import Card from '../../components/layout/Card';
import Modal from '../../components/layout/Modal';
import ConfirmDialog from '../../components/display/ConfirmDialog';
import StatusToast from '../../components/data/StatusToast';

interface RecipeWithDetails {
  recipe: Recipe;
  productName: string;
  productPrice: number;
  productUnit: string;
  ingredients: RecipeIngredient[];
  totalCost: number;
  costPerServing: number;
}

// ── Module-level notes cache to avoid repeated full fetches ──
let notesCache: Note[] | null = null;
let notesCacheTimestamp = 0;
const NOTES_CACHE_TTL = 30000; // 30 seconds

export default function Recipes() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);

  // Data states
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [recipeIngredientsMap, setRecipeIngredientsMap] = useState<Record<number, RecipeIngredient[]>>({});

  // Search
  const [searchQuery, setSearchQuery] = useState('');

  // Modal states
  const [showAddRecipe, setShowAddRecipe] = useState(false);
  const [showEditRecipe, setShowEditRecipe] = useState<number | null>(null);
  const [showDeleteRecipe, setShowDeleteRecipe] = useState<Recipe | null>(null);

  // Form state - Add Recipe
  const [newRecipe, setNewRecipe] = useState<NewRecipe>({ product_id: 0, recipe_type_id: 1, yield_quantity: 1 });
  const [newRecipeIngredients, setNewRecipeIngredients] = useState<Omit<NewRecipeIngredient, 'recipe_id'>[]>([]);
  const [newIngredientInput, setNewIngredientInput] = useState({ ingredient_id: 0, quantity: 0, unit: '', preparation_note: '' });

  // Form state - Edit Recipe
  const [editYield, setEditYield] = useState(1);
  const [editIngredients, setEditIngredients] = useState<RecipeIngredient[]>([]);
  const [editIngredientInput, setEditIngredientInput] = useState({ ingredient_id: 0, quantity: 0, unit: '', preparation_note: '' });
  const [showEditAddIngredient, setShowEditAddIngredient] = useState(false);

  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // ── Recipe Notes state ──
  const [showNotesModal, setShowNotesModal] = useState<RecipeWithDetails | null>(null);
  const [recipeNotes, setRecipeNotes] = useState<Note[]>([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [newNoteForm, setNewNoteForm] = useState({ name: '', category: 'preparation' as string, template_body: '' });
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [noteCounts, setNoteCounts] = useState<Record<number, number>>({});

  // Note category definitions with color coding
  const NOTE_CATEGORIES: { id: string; label: string; badge: string }[] = [
    { id: 'preparation', label: 'Preparation Steps', badge: 'badge-info badge-soft' },
    { id: 'chef-tips', label: 'Chef Tips', badge: 'badge-warning badge-soft' },
    { id: 'allergen', label: 'Allergen Info', badge: 'badge-error badge-soft' },
    { id: 'plating', label: 'Plating Guide', badge: 'badge-success badge-soft' },
    { id: 'general', label: 'General', badge: 'badge-ghost' },
  ];

  const getNoteCategoryBadge = (category: string | null | undefined) => {
    const cat = NOTE_CATEGORIES.find(c => c.id === category);
    return cat?.badge || 'badge-ghost';
  };

  const getNoteCategoryLabel = (category: string | null | undefined) => {
    const cat = NOTE_CATEGORIES.find(c => c.id === category);
    return cat?.label || category || 'General';
  };

  const fetchRecipeNotes = async (recipeId: number) => {
    setNotesLoading(true);
    try {
      // Use cache if still valid
      const now = Date.now();
      if (!notesCache || (now - notesCacheTimestamp) > NOTES_CACHE_TTL) {
        notesCache = await invoke<Note[]>('get_notes');
        notesCacheTimestamp = now;
      }
      // Filter to only notes linked to this recipe
      const notes = (notesCache || []).filter(n => n.recipe_id === recipeId);
      setRecipeNotes(notes);
    } catch (e) { 
      setRecipeNotes([]); 
      console.error('Error loading recipe notes:', e);
    } finally {
      setNotesLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!showNotesModal || !newNoteForm.name.trim() || !newNoteForm.template_body.trim()) return;
    try {
      await invoke<Note>('add_note', {
        template: {
          name: newNoteForm.name,
          template_body: newNoteForm.template_body,
          category: newNoteForm.category || null,
          recipe_id: showNotesModal.recipe.id,
          use_as_template: false,
        }
      });
      setNewNoteForm({ name: '', category: 'preparation', template_body: '' });
      notesCache = null; // invalidate cache after mutation
      await fetchRecipeNotes(showNotesModal.recipe.id);
      refreshNoteCounts();
      showStatus('success', 'Note added!');
    } catch (e) { 
      console.error('Error adding note:', e);
      showStatus('error', String(e));
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (!showNotesModal) return;
    try {
      await invoke('delete_note', { id: noteId });
      notesCache = null; // invalidate cache after mutation
      await fetchRecipeNotes(showNotesModal.recipe.id);
      refreshNoteCounts();
      showStatus('success', 'Note deleted');
    } catch (e) { 
      console.error('Error deleting note:', e);
      showStatus('error', String(e));
    }
  };

  const handleUpdateNote = async () => {
    if (!editingNote || !showNotesModal) return;
    try {
      await invoke('update_note', {
        id: editingNote.id,
        update: {
          name: editingNote.name,
          template_body: editingNote.template_body,
          category: editingNote.category || null,
        }
      });
      setEditingNote(null);
      notesCache = null; // invalidate cache after mutation
      await fetchRecipeNotes(showNotesModal.recipe.id);
      refreshNoteCounts();
      showStatus('success', 'Note updated!');
    } catch (e) {
      console.error('Error updating note:', e);
      showStatus('error', String(e));
    }
  };

  const refreshNoteCounts = async () => {
    try {
      const allNotes = notesCache || await invoke<Note[]>('get_notes');
      if (!notesCache) { notesCache = allNotes; notesCacheTimestamp = Date.now(); }
      const counts: Record<number, number> = {};
      for (const n of allNotes) {
        if (n.recipe_id != null) {
          counts[n.recipe_id] = (counts[n.recipe_id] || 0) + 1;
        }
      }
      setNoteCounts(counts);
    } catch { /* non-critical */ }
  };

  const openNotesModal = async (rd: RecipeWithDetails) => {
    setShowNotesModal(rd);
    setEditingNote(null);
    await fetchRecipeNotes(rd.recipe.id);
  };

  const getIngredientName = (id: number) => ingredients.find(i => i.id === id)?.name || `Ingredient #${id}`;
  const getIngredientUnit = (id: number) => ingredients.find(i => i.id === id)?.unit || '';
  const getIngredientCost = (id: number) => ingredients.find(i => i.id === id)?.cost_per_unit || 0;
  const getProductName = (id: number) => products.find(p => p.id === id)?.name || `Product #${id}`;
  const getProductPrice = (id: number) => products.find(p => p.id === id)?.price || 0;
  const getProductUnit = (id: number) => products.find(p => p.id === id)?.unit || '';

  const calcIngredientCost = (ingredientId: number, quantity: number) => {
    const costPerUnit = getIngredientCost(ingredientId);
    return costPerUnit * quantity;
  };

  const loadData = useCallback(async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [recipesRes, productsRes, ingredientsRes] = await Promise.all([
        invoke<Recipe[]>('get_recipes', { includeInactive: true }),
        invoke<Product[]>('get_products'),
        invoke<Ingredient[]>('get_ingredients', { includeInactive: true }),
      ]);
      setRecipes(recipesRes);
      setProducts(productsRes);
      setIngredients(ingredientsRes);

      // Load ingredients for each recipe
      const ingredientsMap: Record<number, RecipeIngredient[]> = {};
      await Promise.all(recipesRes.map(async (r) => {
        try {
          const ris = await invoke<RecipeIngredient[]>('get_recipe_ingredients', { recipeId: r.id });
          ingredientsMap[r.id] = ris;
        } catch { ingredientsMap[r.id] = []; }
      }));
      setRecipeIngredientsMap(ingredientsMap);

      // Compute note counts grouped by recipe_id (reuses module-level cache)
      try {
        const allNotes = await invoke<Note[]>('get_notes');
        notesCache = allNotes;
        notesCacheTimestamp = Date.now();
        const counts: Record<number, number> = {};
        for (const n of allNotes) {
          if (n.recipe_id != null) {
            counts[n.recipe_id] = (counts[n.recipe_id] || 0) + 1;
          }
        }
        setNoteCounts(counts);
      } catch { /* note count fetch is non-critical */ }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const showStatus = (type: 'success' | 'error', msg: string) => {
    setToast({ type, message: msg });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Computed recipes with details ──
  const recipesWithDetails: RecipeWithDetails[] = recipes.map(r => {
    const ris = recipeIngredientsMap[r.id] || [];
    const totalCost = ris.reduce((sum, ri) => sum + calcIngredientCost(ri.ingredient_id, ri.quantity), 0);
    return {
      recipe: r,
      productName: getProductName(r.product_id),
      productPrice: getProductPrice(r.product_id),
      productUnit: getProductUnit(r.product_id),
      ingredients: ris,
      totalCost,
      costPerServing: r.yield_quantity > 0 ? totalCost / r.yield_quantity : 0,
    };
  });

  const profitMargin = (rd: RecipeWithDetails) => {
    if (rd.totalCost === 0) return 0;
    return ((rd.productPrice - rd.totalCost) / rd.productPrice) * 100;
  };

  const filteredRecipes = searchQuery
    ? recipesWithDetails.filter(rd =>
        rd.productName.toLowerCase().includes(searchQuery.toLowerCase()))
    : recipesWithDetails;

  // ── CRUD: Add Recipe ──
  const handleAddNewIngredient = () => {
    if (newIngredientInput.ingredient_id === 0 || newIngredientInput.quantity === 0) return;
    setNewRecipeIngredients(prev => [...prev, {
      ingredient_id: newIngredientInput.ingredient_id,
      quantity: newIngredientInput.quantity,
      unit: newIngredientInput.unit || null,
      preparation_note: newIngredientInput.preparation_note || null,
    }]);
    setNewIngredientInput({ ingredient_id: 0, quantity: 0, unit: '', preparation_note: '' });
  };

  const handleRemoveNewIngredient = (index: number) => {
    setNewRecipeIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const handleCreateRecipe = async () => {
    if (newRecipe.product_id === 0 || newRecipe.yield_quantity <= 0 || newRecipeIngredients.length === 0) return;
    try {
      await invoke('create_recipe', {
        recipe: newRecipe,
        ingredients: newRecipeIngredients.map(ri => ({ ...ri, recipe_id: 0 })),
      });
      setShowAddRecipe(false);
      setNewRecipe({ product_id: 0, recipe_type_id: 1, yield_quantity: 1 });
      setNewRecipeIngredients([]);
      loadData({ quiet: true });
      showStatus('success', t('recipes.successCreated'));
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── CRUD: Edit Recipe ──
  const handleOpenEdit = async (recipeId: number) => {
    setShowEditRecipe(recipeId);
    const r = recipes.find(rec => rec.id === recipeId);
    if (r) setEditYield(r.yield_quantity);
    const ris = recipeIngredientsMap[recipeId] || [];
    setEditIngredients([...ris]);
    setShowEditAddIngredient(false);
    setEditIngredientInput({ ingredient_id: 0, quantity: 0, unit: '', preparation_note: '' });
  };

  const handleAddEditIngredient = () => {
    if (editIngredientInput.ingredient_id === 0 || editIngredientInput.quantity === 0) return;
    setEditIngredients(prev => [...prev, {
      id: -Date.now(),
      recipe_id: showEditRecipe!,
      ingredient_id: editIngredientInput.ingredient_id,
      quantity: editIngredientInput.quantity,
      unit: editIngredientInput.unit || null,
      preparation_note: editIngredientInput.preparation_note || null,
    }]);
    setEditIngredientInput({ ingredient_id: 0, quantity: 0, unit: '', preparation_note: '' });
  };

  const handleRemoveEditIngredient = (index: number) => {
    setEditIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const handleSaveEdit = async () => {
    if (!showEditRecipe || editYield <= 0) return;
    try {
      // Update yield
      await invoke('update_recipe', {
        id: showEditRecipe,
        update: { yield_quantity: editYield },
      });

      // Persist ingredient changes
      const currentIngredients = recipeIngredientsMap[showEditRecipe] || [];
      const editIds = new Set(editIngredients.filter(ri => ri.id > 0).map(ri => ri.id));

      // Delete removed ingredients
      for (const ri of currentIngredients) {
        if (!editIds.has(ri.id)) {
          await invoke('delete_recipe_ingredient', { id: ri.id });
        }
      }

      // Add new ingredients
      for (const ri of editIngredients) {
        if (ri.id < 0) {
          await invoke('add_recipe_ingredient', {
            ingredient: {
              recipe_id: showEditRecipe,
              ingredient_id: ri.ingredient_id,
              quantity: ri.quantity,
              unit: ri.unit,
              preparation_note: ri.preparation_note,
            }
          });
        }
      }

      setShowEditRecipe(null);
      loadData({ quiet: true });
      showStatus('success', t('recipes.successUpdated'));
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── CRUD: Delete Recipe ──
  const handleDeleteRecipe = async () => {
    if (!showDeleteRecipe) return;
    try {
      await invoke('soft_delete_recipe', { id: showDeleteRecipe.id });
      setShowDeleteRecipe(null);
      loadData({ quiet: true });
      showStatus('success', t('recipes.successDeleted'));
    } catch (e) { showStatus('error', String(e)); }
  };

  // ── Loading ──
  if (isLoading) {
    return (
      <PageLayout title={t('recipes.title')}>
        <div className="space-y-6">
          <SkeletonCard count={4} />
          <SkeletonList items={6} />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={<><span className="icon-[tabler--menu-2] text-warning" /> Recipes</>}
      background="bg-linear-to-br from-base-200 via-warning/10 to-base-200"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card padding="md" hover>
              <h2 className="text-sm font-semibold text-base-content/80">{t('recipes.totalRecipes')}</h2>
              <p className="text-2xl font-bold text-base-content">{recipes.filter(r => r.is_active).length}</p>
            </Card>
          </div>
          <div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card padding="md" hover>
              <h2 className="text-sm font-semibold text-base-content/80">{t('recipes.productsUsed')}</h2>
              <p className="text-2xl font-bold text-warning">{new Set(recipes.filter(r => r.is_active).map(r => r.product_id)).size}</p>
            </Card>
          </div>
          <div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card padding="md" hover>
              <h2 className="text-sm font-semibold text-base-content/80">{t('recipes.avgCostPerRecipe')}</h2>
              <p className="text-2xl font-bold text-error">
              {recipesWithDetails.filter(r => r.recipe.is_active && r.totalCost > 0).length > 0
                ? Math.round(recipesWithDetails.filter(r => r.recipe.is_active).reduce((s, r) => s + r.totalCost, 0) / recipesWithDetails.filter(r => r.recipe.is_active).length)
                : 0}
            </p>
            </Card>
          </div>
          <div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card padding="md" hover>
              <h2 className="text-sm font-semibold text-base-content/80">{t('recipes.avgProfitMargin')}</h2>
              <p className="text-2xl font-bold text-success">
              {recipesWithDetails.filter(r => r.recipe.is_active && r.totalCost > 0).length > 0
                ? `${Math.round(recipesWithDetails.filter(r => r.recipe.is_active).reduce((s, r) => s + profitMargin(r), 0) / recipesWithDetails.filter(r => r.recipe.is_active && r.totalCost > 0).length)}%`
                : 'N/A'}
            </p>
            </Card>
          </div>
        </div>

        {/* Filters & Actions */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
          <div className="relative">
            <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 text-base-content/50" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder={t('recipes.searchPlaceholder')}
              className="input input-bordered w-64 pl-9"
            />
          </div>
          <button
            onClick={() => setShowAddRecipe(true)}
            className="flex items-center gap-2 px-4 py-2 bg-warning text-white rounded-xl font-semibold text-sm active:scale-[0.98] transition-all"
          >
            <span className="icon-[tabler--plus]" /> {t('recipes.addRecipe')}
          </button>
        </div>

        {/* Recipe Cards */}          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 3xl:grid-cols-6 gap-4">
          {filteredRecipes.map(rd => (
            <div
              key={rd.recipe.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`overflow-hidden rounded-xl border border-base-200
                ${!rd.recipe.is_active ? 'opacity-60' : 'hover:border-warning/70 dark:hover:border-warning/30'} transition-all`}
            >
              <Card padding="md">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-warning flex items-center justify-center text-white text-lg">
                      <span className="icon-[tabler--tools-kitchen-2]" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-base-content">{rd.productName}</h3>
                      <span className="text-xs text-base-content/50">
                        {rd.recipe.yield_quantity} {rd.productUnit} · {rd.ingredients.length} ingredient{rd.ingredients.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleOpenEdit(rd.recipe.id)}
                      className="text-primary hover:text-primary/70 p-1.5 rounded-lg hover:bg-primary/10" title={t('common.edit')}>
                      <span className="icon-[tabler--pencil] w-4 h-4" />
                    </button>
                    <button onClick={() => openNotesModal(rd)}
                      className="text-info hover:text-info/70 p-1.5 rounded-lg hover:bg-info/10 relative group/notesbtn" title="Notes">
                      <span className="icon-[tabler--notes] w-4 h-4" />
                      {(noteCounts[rd.recipe.id] || 0) > 0 && (
                        <span className="absolute -top-1 -right-1 min-w-4 h-4 px-0.5 flex items-center justify-center rounded-full bg-info text-info-content text-[10px] font-bold leading-none">
                          {noteCounts[rd.recipe.id]}
                        </span>
                      )}
                    </button>
                    {rd.recipe.is_active && (
                      <button onClick={() => setShowDeleteRecipe(rd.recipe)}
                        className="text-error hover:text-error/70 p-1.5 rounded-lg hover:bg-error/10" title={t('common.deactivate')}>
                        <span className="icon-[tabler--trash] w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Cost Analysis */}
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="bg-base-100/50 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-base-content/50">{t('recipes.productPrice')}</p>
                    <p className="text-sm font-bold text-base-content tabular-nums">{rd.productPrice.toLocaleString()}</p>
                  </div>
                  <div className="bg-base-100/50 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-base-content/50">{t('recipes.totalCost')}</p>
                    <p className={`text-sm font-bold tabular-nums ${rd.totalCost > rd.productPrice ? 'text-error' : 'text-success'}`}>
                      {rd.totalCost.toFixed(0)}
                    </p>
                  </div>
                  <div className="bg-base-100/50 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-base-content/50">{t('recipes.costPerServing')}</p>
                    <p className="text-sm font-bold text-info tabular-nums">{rd.costPerServing.toFixed(1)}</p>
                  </div>
                </div>

                {/* Profit Bar */}
                {rd.totalCost > 0 && rd.productPrice > 0 && (
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-base-content/50 mb-1">
                      <span>{t('recipes.totalCost')} ({((rd.totalCost / rd.productPrice) * 100).toFixed(0)}%)</span>
                      <span className={profitMargin(rd) >= 0 ? 'text-success' : 'text-error'}>
                        {profitMargin(rd) >= 0 ? '+' : ''}{profitMargin(rd).toFixed(0)}% {t('recipes.margin')}
                      </span>
                    </div>
                    <div className="w-full bg-base-300/50 rounded-full h-2 overflow-hidden">
                      <div
                        initial={{ width: 0 }} animate={{ width: `${Math.min((rd.totalCost / rd.productPrice) * 100, 100)}%` }}
                        className={`h-full rounded-full ${rd.totalCost <= rd.productPrice ? 'bg-success' : 'bg-error'}`}
                      />
                    </div>
                  </div>
                )}

                {/* Ingredients List */}
                <div className="space-y-1">
                  {rd.ingredients.slice(0, 5).map(ri => (
                    <div key={ri.id} className="flex items-center justify-between text-xs text-base-content/60">
                      <span className="flex items-center gap-1">
                        <span className="icon-[tabler--package] text-warning/80 w-2.5 h-2.5" />
                        {getIngredientName(ri.ingredient_id)}
                      </span>
                      <span>
                        {ri.quantity} {ri.unit || getIngredientUnit(ri.ingredient_id)}
                        <span className="text-base-content/40 ml-1">({calcIngredientCost(ri.ingredient_id, ri.quantity).toFixed(0)})</span>
                      </span>
                    </div>
                  ))}
                  {rd.ingredients.length > 5 && (
                    <p className="text-xs text-slate-400 text-center pt-1">{t('recipes.moreIngredients', { count: rd.ingredients.length - 5 })}</p>
                  )}
                </div>

                {!rd.recipe.is_active && (
                  <div className="mt-2 px-2 py-1 bg-red-100 dark:bg-red-900/20 rounded-lg text-xs text-red-500 font-medium text-center">
                    {t('recipes.inactive')}
                  </div>
                )}
            </Card>
            </div>
          ))}
          {filteredRecipes.length === 0 && (
            <Card padding="2xl" center className="col-span-full text-base-content/60">
              {searchQuery ? t('recipes.noSearchResults') : t('recipes.noRecipes')}
            </Card>
          )}
        </div>

      <Modal
        isOpen={showAddRecipe}
        onClose={() => setShowAddRecipe(false)}
        title={t('recipes.createRecipeTitle')}
        footer={<>
          <button onClick={() => setShowAddRecipe(false)} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleCreateRecipe}
            disabled={newRecipe.product_id === 0 || newRecipe.yield_quantity <= 0 || newRecipeIngredients.length === 0}
            className="flex-1 py-2.5 rounded-lg bg-warning text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <span className="icon-[tabler--device-floppy]" /> {t('recipes.createRecipeTitle')}
          </button>
        </>}
      >
        <div>            <label className="block text-base-content/80 mb-1 text-sm">{t('recipes.product')} *</label>
          <select value={newRecipe.product_id} onChange={e => setNewRecipe(p => ({ ...p, product_id: Number(e.target.value) }))}
            className="select select-bordered w-full">
            <option value={0}>{t('recipes.selectProduct')}</option>
            {products.map(p => (
              <option key={p.id} value={p.id}>{p.name} ({p.price}/ {p.unit})</option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('recipes.recipeType')}</label>              <select value={newRecipe.recipe_type_id} onChange={e => setNewRecipe(p => ({ ...p, recipe_type_id: Number(e.target.value) }))}
              className="select select-bordered w-full">
              <option value={1}>{t('recipes.standard')}</option>
            </select>
          </div>
          <div>
            <label className="block text-base-content/80 mb-1 text-sm">{t('recipes.yieldQuantity')} *</label>
            <input type="number" step="0.1" min="0.1" value={newRecipe.yield_quantity}
              onChange={e => setNewRecipe(p => ({ ...p, yield_quantity: Number(e.target.value) }))}
              className="input input-bordered w-full" />
          </div>
        </div>

        <div className="border-t border-base-300/50 pt-4">            <h3 className="text-sm font-semibold text-base-content mb-3 flex items-center gap-2">
              <span className="icon-[tabler--package] text-warning" /> {t('recipes.ingredients')} {newRecipeIngredients.length > 0 && `(${newRecipeIngredients.length})`}
            </h3>

          <div className="grid grid-cols-12 gap-2 mb-2">
            <div className="col-span-5">
              <select value={newIngredientInput.ingredient_id} onChange={e => setNewIngredientInput(p => ({ ...p, ingredient_id: Number(e.target.value), unit: getIngredientUnit(Number(e.target.value)) }))}
                className="select select-bordered w-full text-xs">
                <option value={0}>Ingredient...</option>
                {ingredients.filter(i => i.is_active).map(ing => (
                  <option key={ing.id} value={ing.id}>{ing.name} ({ing.cost_per_unit}/{ing.unit})</option>
                ))}
              </select>
            </div>
            <div className="col-span-3">
              <input type="number" step="0.01" min="0" value={newIngredientInput.quantity || ''}
                onChange={e => setNewIngredientInput(p => ({ ...p, quantity: Number(e.target.value) }))}
                placeholder={t('recipes.qty')}
                className="input input-bordered w-full text-xs" />
            </div>
            <div className="col-span-2">
              <input type="text" value={newIngredientInput.unit}
                onChange={e => setNewIngredientInput(p => ({ ...p, unit: e.target.value }))}
                placeholder={t('recipes.unit')}
                className="input input-bordered w-full text-xs" />
            </div>
            <div className="col-span-2">
              <button onClick={handleAddNewIngredient} disabled={newIngredientInput.ingredient_id === 0 || newIngredientInput.quantity === 0}
                className="w-full h-full flex items-center justify-center bg-warning text-white rounded-lg disabled:opacity-50 text-xs font-bold">
                <span className="icon-[tabler--plus] w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="space-y-1 max-h-32 overflow-y-auto">
            {newRecipeIngredients.map((ri, idx) => (
              <div key={idx} className="flex items-center justify-between bg-base-100/30 rounded-lg px-2 py-1.5">
                <span className="text-xs text-base-content/80">
                  {getIngredientName(ri.ingredient_id)} — {ri.quantity} {ri.unit || getIngredientUnit(ri.ingredient_id)}
                </span>
                <button onClick={() => handleRemoveNewIngredient(idx)} className="text-error hover:text-error/70 p-0.5">
                  <span className="icon-[tabler--minus] w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="mt-2 text-right text-xs text-base-content/50">
            {t('recipes.totalIngredientCost')}: <strong className="text-base-content">
              {newRecipeIngredients.reduce((sum, ri) => sum + calcIngredientCost(ri.ingredient_id, ri.quantity), 0).toFixed(0)}
            </strong>
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={!!showEditRecipe}
        onClose={() => setShowEditRecipe(null)}
        title={t('recipes.editRecipeTitle')}
        footer={<>
          <button onClick={() => setShowEditRecipe(null)} className="flex-1 py-2.5 rounded-lg bg-base-300/50 text-base-content font-semibold hover:bg-base-300/80 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleSaveEdit} disabled={editYield <= 0}
            className="flex-1 py-2.5 rounded-lg bg-primary text-primary-content font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <span className="icon-[tabler--device-floppy]" /> {t('common.saveChanges')}
          </button>
        </>}
      >          <div className="text-sm text-base-content/60">
          {t('recipes.product')}: <strong className="text-base-content">{getProductName(recipes.find(r => r.id === showEditRecipe)?.product_id || 0)}</strong>
        </div>
        <div>
          <label className="block text-base-content/80 mb-1 text-sm">{t('recipes.yieldQuantity')}</label>
          <input type="number" step="0.1" min="0.1" value={editYield}
            onChange={e => setEditYield(Number(e.target.value))}
            className="input input-bordered w-full" />
        </div>

        <div className="border-t border-base-300/50 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-base-content flex items-center gap-2">
              <span className="icon-[tabler--package] text-warning" /> {t('recipes.ingredients')} ({editIngredients.length})
            </h3>
            <button onClick={() => setShowEditAddIngredient(!showEditAddIngredient)}
              className="text-xs text-warning hover:text-warning/80 font-medium flex items-center gap-1">
              <span className="icon-[tabler--plus]" /> {t('recipes.addIngredient')}
            </button>
          </div>

          {showEditAddIngredient && (
            <div className="grid grid-cols-12 gap-2 mb-3 p-2 bg-base-100/30 rounded-lg">
              <div className="col-span-5">
                <select value={editIngredientInput.ingredient_id} onChange={e => setEditIngredientInput(p => ({ ...p, ingredient_id: Number(e.target.value), unit: getIngredientUnit(Number(e.target.value)) }))}
                  className="select select-bordered w-full text-xs">
                  <option value={0}>Select...</option>
                  {ingredients.filter(i => i.is_active).map(ing => (
                    <option key={ing.id} value={ing.id}>{ing.name}</option>
                  ))}
                </select>
              </div>
              <div className="col-span-3">
                <input type="number" step="0.01" value={editIngredientInput.quantity || ''}
                  onChange={e => setEditIngredientInput(p => ({ ...p, quantity: Number(e.target.value) }))}
                  placeholder={t('recipes.qty')}
                  className="input input-bordered w-full text-xs" />
              </div>
              <div className="col-span-2">
                <input type="text" value={editIngredientInput.unit}
                  onChange={e => setEditIngredientInput(p => ({ ...p, unit: e.target.value }))}
                  placeholder={t('recipes.unit')}
                  className="input input-bordered w-full text-xs" />
              </div>
              <div className="col-span-2">
                <button onClick={handleAddEditIngredient} disabled={editIngredientInput.ingredient_id === 0 || editIngredientInput.quantity === 0}
                  className="w-full h-full flex items-center justify-center bg-warning text-white rounded-lg disabled:opacity-50 text-xs font-bold">
                  <span className="icon-[tabler--plus]" />
                </button>
              </div>
            </div>
          )}

          <div className="space-y-1 max-h-40 overflow-y-auto">
            {editIngredients.map((ri, idx) => (
              <div key={ri.id} className="flex items-center justify-between bg-base-100/30 rounded-lg px-2 py-1.5">
                <span className="text-xs text-base-content/80">
                  {getIngredientName(ri.ingredient_id)} — {ri.quantity} {ri.unit || getIngredientUnit(ri.ingredient_id)}
                </span>
                <button onClick={() => handleRemoveEditIngredient(idx)} className="text-error hover:text-error/70 p-0.5">
                  <span className="icon-[tabler--minus] w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="mt-2 text-right text-xs text-base-content/50">
            {t('recipes.totalCostLabel')}: <strong className="text-base-content">
              {editIngredients.reduce((sum, ri) => sum + calcIngredientCost(ri.ingredient_id, ri.quantity), 0).toFixed(0)}
            </strong>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={!!showDeleteRecipe}
        onClose={() => setShowDeleteRecipe(null)}
        onConfirm={handleDeleteRecipe}
        title={t('recipes.deactivateTitle')}
        message={t('recipes.deactivateConfirm')}
        itemName={getProductName(showDeleteRecipe?.product_id || 0)}
      />

      {/* ── Recipe Notes Modal ── */}
      {showNotesModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-base-100 rounded-xl p-6 w-full max-w-2xl max-h-[85vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-info/10 text-info flex items-center justify-center">
                  <span className="icon-[tabler--notes] w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-base-content">Notes for {showNotesModal.productName}</h3>
                  <p className="text-xs text-base-content/50">
                    Recipe #{showNotesModal.recipe.id} — {showNotesModal.recipe.yield_quantity} {showNotesModal.productUnit}
                    {' · '}
                    <span className="text-info underline cursor-pointer hover:text-info/80" onClick={() => { setShowNotesModal(null); navigate('/notes'); }}>
                      Open Notes app
                    </span>
                  </p>
                </div>
              </div>
              <button onClick={() => setShowNotesModal(null)} className="btn btn-ghost btn-sm btn-square">
                <span className="icon-[tabler--x] w-5 h-5" />
              </button>
            </div>

            {/* Add Note Form */}
            <div className="bg-base-200 rounded-xl p-4 mb-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="icon-[tabler--plus] w-4 h-4 text-success" />
                <span className="text-sm font-semibold text-base-content">{t('recipes.addNote') || 'Add Note'}</span>
              </div>
              <div className="flex flex-col gap-2">
                <input
                  type="text"
                  value={newNoteForm.name}
                  onChange={e => setNewNoteForm(f => ({ ...f, name: e.target.value }))}
                  placeholder={t('recipes.noteTitlePlaceholder') || 'Note title...'}
                  className="input input-bordered input-sm w-full"
                />
                <div className="flex gap-2">
                  <select
                    value={newNoteForm.category}
                    onChange={e => setNewNoteForm(f => ({ ...f, category: e.target.value }))}
                    className="select select-bordered select-sm w-44"
                  >
                    {NOTE_CATEGORIES.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.label}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => {
                      const templates: Record<string, string> = {
                        preparation: `1. Gather all ingredients listed in the recipe.
2. Prep and measure each ingredient.
3. Follow cooking sequence as described.`,
                        'chef-tips': `Chef recommendation: For best results, use fresh ingredients.

Tip: Prep time can be reduced by pre-chopping vegetables the day before.`,
                        allergen: `⚠️ Allergens: May contain dairy, gluten, nuts.

Cross-contamination warning: Prepared in a kitchen that also processes shellfish and soy.`,
                        plating: `Plate presentation steps:
1. Base layer: sauce or puree
2. Main element: protein or centerpiece
3. Garnish: herbs, microgreens, edible flowers
4. Final drizzle: oil or reduction`,
                        general: '',
                      };
                      const template = templates[newNoteForm.category] || '';
                      if (template) setNewNoteForm(f => ({ ...f, template_body: template }));
                    }}
                    className="btn btn-ghost btn-sm gap-1 text-xs"
                    title={t('recipes.insertTemplate') || 'Template'}
                  >
                    <span className="icon-[tabler--template] w-3.5 h-3.5" />
                    {t('recipes.insertTemplate') || 'Template'}
                  </button>
                </div>
                <textarea
                  value={newNoteForm.template_body}
                  onChange={e => setNewNoteForm(f => ({ ...f, template_body: e.target.value }))}
                  placeholder={t('recipes.noteBodyPlaceholder') || 'Write your notes here...'}
                  rows={3}
                  className="textarea textarea-bordered textarea-sm w-full"
                />
                <button
                  onClick={handleAddNote}
                  disabled={!newNoteForm.name.trim() || !newNoteForm.template_body.trim()}
                  className="btn btn-primary btn-sm w-full gap-1"
                >
                  <span className="icon-[tabler--plus] w-4 h-4" />
                  Add Note
                </button>
              </div>
            </div>

            {/* Notes List */}
            {notesLoading ? (
              <div className="text-center py-6 text-base-content/50">
                <span className="loading loading-spinner loading-md" />
                <p className="text-sm mt-2">{t('recipes.loadingNotes') || 'Loading notes...'}</p>
              </div>
            ) : recipeNotes.length === 0 ? (
              <div className="text-center py-6 text-base-content/40">
                <span className="icon-[tabler--notes] w-10 h-10 mx-auto mb-2 opacity-30" />
                <p className="text-sm">{t('recipes.noNotes') || 'No notes yet. Add your first note above!'}</p>
              </div>
            ) : (
              <div className="space-y-2">
                {recipeNotes.map(note => (
                  <div key={note.id} className="bg-base-200/50 rounded-lg p-3">
                    {editingNote?.id === note.id ? (
                      /* ── Edit Mode ── */
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={editingNote.name}
                          onChange={e => setEditingNote({ ...editingNote, name: e.target.value })}
                          className="input input-bordered input-sm w-full text-sm"
                          placeholder="Note title"
                        />
                        <select
                          value={editingNote.category || ''}
                          onChange={e => setEditingNote({ ...editingNote, category: e.target.value })}
                          className="select select-bordered select-sm w-full"
                        >
                          {NOTE_CATEGORIES.map(cat => (
                            <option key={cat.id} value={cat.id}>{cat.label}</option>
                          ))}
                        </select>
                        <textarea
                          value={editingNote.template_body}
                          onChange={e => setEditingNote({ ...editingNote, template_body: e.target.value })}
                          rows={3}
                          className="textarea textarea-bordered textarea-sm w-full text-sm"
                        />
                        <div className="flex gap-2 justify-end">
                          <button onClick={() => setEditingNote(null)} className="btn btn-ghost btn-xs">Cancel</button>
                          <button onClick={handleUpdateNote} className="btn btn-primary btn-xs">Save</button>
                        </div>
                      </div>
                    ) : (
                      /* ── View Mode ── */
                      <>
                        <div className="flex items-start justify-between mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="icon-[tabler--note] w-4 h-4 text-info" />
                            <h4 className="text-sm font-semibold text-base-content">{note.name}</h4>
                            <span className={`badge badge-xs ${getNoteCategoryBadge(note.category)}`}>
                              {getNoteCategoryLabel(note.category)}
                            </span>
                          </div>
                          <div className="flex gap-1">
                            <button
                              onClick={() => setEditingNote({ ...note })}
                              className="text-info/60 hover:text-info p-0.5 rounded hover:bg-info/10 transition-colors"
                              title="Edit note"
                            >
                              <span className="icon-[tabler--pencil] w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => handleDeleteNote(note.id)}
                              className="text-error/60 hover:text-error p-0.5 rounded hover:bg-error/10 transition-colors"
                              title="Delete note"
                            >
                              <span className="icon-[tabler--trash] w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                        <p className="text-xs text-base-content/70 whitespace-pre-wrap leading-relaxed">
                          {note.template_body}
                        </p>
                        <p className="text-[10px] text-base-content/30 mt-1.5">
                          {new Date(note.created_at).toLocaleDateString()} · {new Date(note.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <StatusToast type={toast?.type || 'success'} message={toast?.message || ''} visible={!!toast} onDismiss={() => setToast(null)} />
    </PageLayout>
  );
}
