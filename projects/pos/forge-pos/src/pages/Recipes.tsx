import { motion } from 'framer-motion';
import { useState, useEffect, useCallback } from 'react';
import { MdRestaurantMenu, MdEdit, MdDelete, MdAdd, MdRemove } from 'react-icons/md';
import { FaPlus, FaSave, FaSearch, FaCubes, FaUtensils } from 'react-icons/fa';
import { invoke } from '@tauri-apps/api/core';
import { Recipe, NewRecipe, RecipeIngredient, NewRecipeIngredient, Product, Ingredient } from '../types';
import PageLayout from '../components/PageLayout';
import { SkeletonCard, SkeletonList } from '../components/Skeleton';
import { useTranslation } from 'react-i18next';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import StatusToast from '../components/StatusToast';

interface RecipeWithDetails {
  recipe: Recipe;
  productName: string;
  productPrice: number;
  productUnit: string;
  ingredients: RecipeIngredient[];
  totalCost: number;
  costPerServing: number;
}

export default function Recipes() {
  const { t } = useTranslation();
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
      <PageLayout title={t('recipes.title')} background="bg-slate-100 dark:bg-slate-900">
        <div className="space-y-6">
          <SkeletonCard count={4} />
          <SkeletonList items={6} />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={<><MdRestaurantMenu className="text-orange-500" /> Recipes</>}
      background="bg-linear-to-br from-slate-100 via-orange-100 to-slate-100 dark:from-slate-900 dark:via-orange-950 dark:to-slate-900"
    >

        {/* Summary Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('recipes.totalRecipes')}</h2>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">{recipes.filter(r => r.is_active).length}</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('recipes.productsUsed')}</h2>
            <p className="text-2xl font-bold text-orange-500">{new Set(recipes.filter(r => r.is_active).map(r => r.product_id)).size}</p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('recipes.avgCostPerRecipe')}</h2>
            <p className="text-2xl font-bold text-rose-500">
              {recipesWithDetails.filter(r => r.recipe.is_active && r.totalCost > 0).length > 0
                ? Math.round(recipesWithDetails.filter(r => r.recipe.is_active).reduce((s, r) => s + r.totalCost, 0) / recipesWithDetails.filter(r => r.recipe.is_active).length)
                : 0}
            </p>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="card--glass card--hover rounded-xl p-4">
            <h2 className="text-slate-600 dark:text-white/60 text-sm">{t('recipes.avgProfitMargin')}</h2>
            <p className="text-2xl font-bold text-emerald-500">
              {recipesWithDetails.filter(r => r.recipe.is_active && r.totalCost > 0).length > 0
                ? `${Math.round(recipesWithDetails.filter(r => r.recipe.is_active).reduce((s, r) => s + profitMargin(r), 0) / recipesWithDetails.filter(r => r.recipe.is_active && r.totalCost > 0).length)}%`
                : 'N/A'}
            </p>
          </motion.div>
        </div>

        {/* Filters & Actions */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
          <div className="relative">
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder={t('recipes.searchPlaceholder')}
              className="pl-9 pr-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-sm w-64"
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            onClick={() => setShowAddRecipe(true)}
            className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-xl font-semibold text-sm"
          >
            <FaPlus /> {t('recipes.addRecipe')}
          </motion.button>
        </div>

        {/* Recipe Cards */}          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 3xl:grid-cols-5 gap-4">
          {filteredRecipes.map(rd => (
            <motion.div
              key={rd.recipe.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`card--glass rounded-xl overflow-hidden border border-slate-200 dark:border-white/5
                ${!rd.recipe.is_active ? 'opacity-60' : 'hover:border-orange-300 dark:hover:border-orange-500/30'} transition-all`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-orange-500 flex items-center justify-center text-white text-lg">
                      <FaUtensils />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-900 dark:text-white">{rd.productName}</h3>
                      <span className="text-xs text-slate-500 dark:text-gray-400">
                        {rd.recipe.yield_quantity} {rd.productUnit} · {rd.ingredients.length} ingredient{rd.ingredients.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleOpenEdit(rd.recipe.id)}
                      className="text-blue-500 hover:text-blue-400 p-1.5 rounded-lg hover:bg-blue-500/10" title={t('common.edit')}>
                      <MdEdit className="w-4 h-4" />
                    </button>
                    {rd.recipe.is_active && (
                      <button onClick={() => setShowDeleteRecipe(rd.recipe)}
                        className="text-red-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10" title={t('common.deactivate')}>
                        <MdDelete className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Cost Analysis */}
                <div className="grid grid-cols-3 gap-3 mb-3">
                  <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-slate-500 dark:text-gray-400">{t('recipes.productPrice')}</p>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">{rd.productPrice.toLocaleString()}</p>
                  </div>
                  <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-slate-500 dark:text-gray-400">{t('recipes.totalCost')}</p>
                    <p className={`text-sm font-bold ${rd.totalCost > rd.productPrice ? 'text-red-500' : 'text-emerald-500'}`}>
                      {rd.totalCost.toFixed(0)}
                    </p>
                  </div>
                  <div className="bg-white/50 dark:bg-white/5 rounded-lg p-2.5 text-center">
                    <p className="text-xs text-slate-500 dark:text-gray-400">{t('recipes.costPerServing')}</p>
                    <p className="text-sm font-bold text-indigo-500">{rd.costPerServing.toFixed(1)}</p>
                  </div>
                </div>

                {/* Profit Bar */}
                {rd.totalCost > 0 && rd.productPrice > 0 && (
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-slate-500 dark:text-gray-400 mb-1">
                      <span>{t('recipes.totalCost')} ({((rd.totalCost / rd.productPrice) * 100).toFixed(0)}%)</span>
                      <span className={profitMargin(rd) >= 0 ? 'text-emerald-500' : 'text-red-500'}>
                        {profitMargin(rd) >= 0 ? '+' : ''}{profitMargin(rd).toFixed(0)}% {t('recipes.margin')}
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }} animate={{ width: `${Math.min((rd.totalCost / rd.productPrice) * 100, 100)}%` }}
                        className={`h-full rounded-full ${rd.totalCost <= rd.productPrice ? 'bg-emerald-500' : 'bg-red-500'}`}
                      />
                    </div>
                  </div>
                )}

                {/* Ingredients List */}
                <div className="space-y-1">
                  {rd.ingredients.slice(0, 5).map(ri => (
                    <div key={ri.id} className="flex items-center justify-between text-xs text-slate-600 dark:text-gray-400">
                      <span className="flex items-center gap-1">
                        <FaCubes className="text-orange-400 w-2.5 h-2.5" />
                        {getIngredientName(ri.ingredient_id)}
                      </span>
                      <span>
                        {ri.quantity} {ri.unit || getIngredientUnit(ri.ingredient_id)}
                        <span className="text-slate-400 ml-1">({calcIngredientCost(ri.ingredient_id, ri.quantity).toFixed(0)})</span>
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
              </div>
            </motion.div>
          ))}
          {filteredRecipes.length === 0 && (
            <div className="col-span-full card--glass rounded-xl p-8 text-center text-slate-600 dark:text-white/60">
              {searchQuery ? t('recipes.noSearchResults') : t('recipes.noRecipes')}
            </div>
          )}
        </div>

      <Modal
        isOpen={showAddRecipe}
        onClose={() => setShowAddRecipe(false)}
        title={t('recipes.createRecipeTitle')}
        footer={<>
          <button onClick={() => setShowAddRecipe(false)} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleCreateRecipe}
            disabled={newRecipe.product_id === 0 || newRecipe.yield_quantity <= 0 || newRecipeIngredients.length === 0}
            className="flex-1 py-2.5 rounded-lg bg-orange-500 text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <FaSave /> {t('recipes.createRecipeTitle')}
          </button>
        </>}
      >
        <div>            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('recipes.product')} *</label>
          <select value={newRecipe.product_id} onChange={e => setNewRecipe(p => ({ ...p, product_id: Number(e.target.value) }))}
            className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white">
            <option value={0}>{t('recipes.selectProduct')}</option>
            {products.map(p => (
              <option key={p.id} value={p.id}>{p.name} ({p.price}/ {p.unit})</option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('recipes.recipeType')}</label>              <select value={newRecipe.recipe_type_id} onChange={e => setNewRecipe(p => ({ ...p, recipe_type_id: Number(e.target.value) }))}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white">
              <option value={1}>{t('recipes.standard')}</option>
            </select>
          </div>
          <div>
            <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('recipes.yieldQuantity')} *</label>
            <input type="number" step="0.1" min="0.1" value={newRecipe.yield_quantity}
              onChange={e => setNewRecipe(p => ({ ...p, yield_quantity: Number(e.target.value) }))}
              className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
          </div>
        </div>

        <div className="border-t border-slate-300 dark:border-white/10 pt-4">            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
              <FaCubes className="text-orange-500" /> {t('recipes.ingredients')} {newRecipeIngredients.length > 0 && `(${newRecipeIngredients.length})`}
            </h3>

          <div className="grid grid-cols-12 gap-2 mb-2">
            <div className="col-span-5">
              <select value={newIngredientInput.ingredient_id} onChange={e => setNewIngredientInput(p => ({ ...p, ingredient_id: Number(e.target.value), unit: getIngredientUnit(Number(e.target.value)) }))}
                className="w-full px-2 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-xs">
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
                className="w-full px-2 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-xs" />
            </div>
            <div className="col-span-2">
              <input type="text" value={newIngredientInput.unit}
                onChange={e => setNewIngredientInput(p => ({ ...p, unit: e.target.value }))}
                placeholder={t('recipes.unit')}
                className="w-full px-2 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-xs" />
            </div>
            <div className="col-span-2">
              <button onClick={handleAddNewIngredient} disabled={newIngredientInput.ingredient_id === 0 || newIngredientInput.quantity === 0}
                className="w-full h-full flex items-center justify-center bg-orange-500 text-white rounded-lg disabled:opacity-50 text-xs font-bold">
                <MdAdd className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="space-y-1 max-h-32 overflow-y-auto">
            {newRecipeIngredients.map((ri, idx) => (
              <div key={idx} className="flex items-center justify-between bg-white/30 dark:bg-white/5 rounded-lg px-2 py-1.5">
                <span className="text-xs text-slate-700 dark:text-gray-300">
                  {getIngredientName(ri.ingredient_id)} — {ri.quantity} {ri.unit || getIngredientUnit(ri.ingredient_id)}
                </span>
                <button onClick={() => handleRemoveNewIngredient(idx)} className="text-red-500 hover:text-red-400 p-0.5">
                  <MdRemove className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="mt-2 text-right text-xs text-slate-500 dark:text-gray-400">
            {t('recipes.totalIngredientCost')}: <strong className="text-slate-900 dark:text-white">
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
          <button onClick={() => setShowEditRecipe(null)} className="flex-1 py-2.5 rounded-lg bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-white font-semibold hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors">{t('common.cancel')}</button>
          <button onClick={handleSaveEdit} disabled={editYield <= 0}
            className="flex-1 py-2.5 rounded-lg bg-blue-500 text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2">
            <FaSave /> {t('common.saveChanges')}
          </button>
        </>}
      >          <div className="text-sm text-slate-600 dark:text-gray-400">
          {t('recipes.product')}: <strong className="text-slate-900 dark:text-white">{getProductName(recipes.find(r => r.id === showEditRecipe)?.product_id || 0)}</strong>
        </div>
        <div>
          <label className="block text-slate-700 dark:text-gray-300 mb-1 text-sm">{t('recipes.yieldQuantity')}</label>
          <input type="number" step="0.1" min="0.1" value={editYield}
            onChange={e => setEditYield(Number(e.target.value))}
            className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white" />
        </div>

        <div className="border-t border-slate-300 dark:border-white/10 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <FaCubes className="text-orange-500" /> {t('recipes.ingredients')} ({editIngredients.length})
            </h3>
            <button onClick={() => setShowEditAddIngredient(!showEditAddIngredient)}
              className="text-xs text-orange-500 hover:text-orange-400 font-medium flex items-center gap-1">
              <MdAdd /> {t('recipes.addIngredient')}
            </button>
          </div>

          {showEditAddIngredient && (
            <div className="grid grid-cols-12 gap-2 mb-3 p-2 bg-white/30 dark:bg-white/5 rounded-lg">
              <div className="col-span-5">
                <select value={editIngredientInput.ingredient_id} onChange={e => setEditIngredientInput(p => ({ ...p, ingredient_id: Number(e.target.value), unit: getIngredientUnit(Number(e.target.value)) }))}
                  className="w-full px-2 py-1 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-xs">
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
                  className="w-full px-2 py-1 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-xs" />
              </div>
              <div className="col-span-2">
                <input type="text" value={editIngredientInput.unit}
                  onChange={e => setEditIngredientInput(p => ({ ...p, unit: e.target.value }))}
                  placeholder={t('recipes.unit')}
                  className="w-full px-2 py-1 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600 text-slate-900 dark:text-white text-xs" />
              </div>
              <div className="col-span-2">
                <button onClick={handleAddEditIngredient} disabled={editIngredientInput.ingredient_id === 0 || editIngredientInput.quantity === 0}
                  className="w-full h-full flex items-center justify-center bg-orange-500 text-white rounded-lg disabled:opacity-50 text-xs font-bold">
                  <MdAdd />
                </button>
              </div>
            </div>
          )}

          <div className="space-y-1 max-h-40 overflow-y-auto">
            {editIngredients.map((ri, idx) => (
              <div key={ri.id} className="flex items-center justify-between bg-white/30 dark:bg-white/5 rounded-lg px-2 py-1.5">
                <span className="text-xs text-slate-700 dark:text-gray-300">
                  {getIngredientName(ri.ingredient_id)} — {ri.quantity} {ri.unit || getIngredientUnit(ri.ingredient_id)}
                </span>
                <button onClick={() => handleRemoveEditIngredient(idx)} className="text-red-500 hover:text-red-400 p-0.5">
                  <MdRemove className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          <div className="mt-2 text-right text-xs text-slate-500 dark:text-gray-400">
            {t('recipes.totalCostLabel')}: <strong className="text-slate-900 dark:text-white">
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

      <StatusToast type={toast?.type || 'success'} message={toast?.message || ''} visible={!!toast} onDismiss={() => setToast(null)} />
    </PageLayout>
  );
}
