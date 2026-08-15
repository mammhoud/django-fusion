import { useState, useEffect, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';
import { readFile } from '@tauri-apps/plugin-fs';
import { Product, NewProduct, UpdateProductPayload, Category, NewCategory, UpdateCategoryPayload, Ingredient } from '../../../types';
import Card from '../../../components/ui/Card';
import DataTable, { type Column } from '../../../components/ui/DataTable';
import ProductCard, { PRODUCT_CARD_COLORS, ProductCardSkeleton, PRODUCT_SKELETON_COUNT, hexToRgba } from '../../../components/pos/ProductCard';
import ProductFilterBar from '../../../components/shared/ProductFilterBar';
import Modal from '../../../components/ui/Modal';
import Button from '../../../components/ui/Button';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';
import PageLayout from '../../../components/layout/PageLayout';
import { iconClass } from '../../../lib/icons';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../../components/shared/KeyboardShortcutsModal';
import { useDebouncedSearch } from '../../../hooks/useDebouncedSearch';
import { useCurrency } from '../../../contexts/CurrencyContext';
import AnimatePresence from '../../../components/ui/AnimatePresence';
import { Tooltip, TooltipTrigger, TooltipContent } from '../../../components/ui/tooltip';

interface FormErrors {
  name?: string;
  price?: string;
  unit?: string;
}

type SortKey = 'newest' | 'name-asc' | 'name-desc' | 'price-asc' | 'price-desc';

/** Preset swatches for the category color picker. */
export const CATEGORY_COLOR_PALETTE = [
  '#f97316', // orange
  '#f43f5e', // rose
  '#8b5cf6', // violet
  '#06b6d4', // cyan
  '#10b981', // emerald
  '#eab308', // yellow
  '#3b82f6', // blue
  '#db2777', // pastel (FlyonUI pastel-light primary)
  '#14b8a6', // teal
  '#6366f1', // indigo
];

/** Order types a product can be restricted to (mirrors Sale's ORDER_TYPES). */
export const ORDER_TYPE_OPTIONS = [
  { value: 'dine-in', label: 'Dine-in', i18nKey: 'sale.dineIn', color: '#10b981' },
  { value: 'takeaway', label: 'Takeaway', i18nKey: 'sale.takeaway', color: '#3b82f6' },
  { value: 'delivery', label: 'Delivery', i18nKey: 'sale.delivery', color: '#8b5cf6' },
  { value: 'extra-order', label: 'Extra Order', i18nKey: 'sale.extraOrder', color: '#f97316' },
  { value: 'dated-order', label: 'Dated Order', i18nKey: 'sale.datedOrder', color: '#db2777' },
];

export default function ProductManager() {
  const { t } = useTranslation();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [newProduct, setNewProduct] = useState({ name: '', price: '', unit: 'item', category_id: 0 as number | 0, product_type: 'product', barcode: '', description: '', available_order_types: 'dine-in,takeaway,delivery,extra-order,dated-order' });
  // ── Add-wizard state: 3 steps (Basics → Recipe & Options → Review) ──
  const [wizardStep, setWizardStep] = useState<1 | 2 | 3>(1);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [recipeRows, setRecipeRows] = useState<{ ingredient_id: number; quantity: number; unit?: string }[]>([]);
  const [recipeYield, setRecipeYield] = useState(1);
  const [productImage, setProductImage] = useState<string | null>(null);
  // Snapshot of the original image when editing so we don't accidentally
  // re-clear or re-write the image on every save.
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const { formatPrice, currencySymbol } = useCurrency();
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [productToDelete, setProductToDelete] = useState<Product | null>(null);

  // Bulk selection (table view) + bulk action state
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [isBulkSubmitting, setIsBulkSubmitting] = useState(false);
  const [bulkAction, setBulkAction] = useState<'category' | 'type' | null>(null);
  /** Snapshot of the target product IDs taken when a bulk modal opens. */
  const [bulkTargetIds, setBulkTargetIds] = useState<number[]>([]);
  const [bulkCategoryValue, setBulkCategoryValue] = useState<number>(0);
  const [bulkTypeValue, setBulkTypeValue] = useState('product');
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Category CRUD state
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [categoryForm, setCategoryForm] = useState({ name: '', color: CATEGORY_COLOR_PALETTE[0] });
  const [categoryErrors, setCategoryErrors] = useState<{ name?: string }>({});
  const [isCategorySubmitting, setIsCategorySubmitting] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null);
  const [showCategoryDeleteModal, setShowCategoryDeleteModal] = useState(false);

  // AJAX-style debounced search — shared hook. Rename-destructure keeps the
  // existing JSX variable names (`searchQuery`, `debouncedSearch`, `isFiltering`).
  const {
    query: searchQuery,
    setQuery: setSearchQuery,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();
  const [selectedCategory, setSelectedCategory] = useState<number | 'all'>('all');
  const [sortKey, setSortKey] = useState<SortKey>('newest');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const key = e.key;

      if (key === '?' || key === '/') {
        e.preventDefault();
        setShowShortcutHelp(prev => !prev);
        return;
      }

      if (key.toLowerCase() === 'a' && !showAddModal && !showDeleteModal) {
        e.preventDefault();
        setShowAddModal(true);
        return;
      }

      if (key === 'Escape') {
        if (showAddModal) { closeModal(); return; }
        if (showDeleteModal) {
          e.preventDefault();
          setShowDeleteModal(false);
          setProductToDelete(null);
        }
        if (showCategoryModal) { closeCategoryModal(); return; }
        if (showCategoryDeleteModal) {
          e.preventDefault();
          setShowCategoryDeleteModal(false);
          setCategoryToDelete(null);
        }
        return;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showAddModal, showDeleteModal, showCategoryModal, showCategoryDeleteModal]);


  const loadProducts = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [productsRes, categoriesRes, ingredientsRes] = await Promise.all([
        invoke<Product[]>('get_products'),
        invoke<Category[]>('get_categories').catch(() => []),
        // Active ingredients power the wizard's Recipe step (step 2).
        invoke<Ingredient[]>('get_ingredients', { includeInactive: false }).catch(() => []),
      ]);
      setProducts(productsRes);
      setCategories(categoriesRes || []);
      setIngredients(ingredientsRes || []);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  // ----- Derived: filtered + sorted products (unified search: name, barcode, category) -----
  const filteredProducts = useMemo(() => {
    let result = products;
    const query = debouncedSearch.trim().toLowerCase();
    if (query) {
      result = result.filter(p => {
        const catName = p.category_id != null
          ? (categories.find(c => c.id === p.category_id)?.name || '').toLowerCase()
          : '';
        return (
          p.name.toLowerCase().includes(query) ||
          (p.barcode || '').toLowerCase().includes(query) ||
          catName.includes(query)
        );
      });
    }
    if (selectedCategory !== 'all') {
      result = result.filter(p => p.category_id === selectedCategory);
    }
    const sorted = [...result];
    switch (sortKey) {
      case 'name-asc': sorted.sort((a, b) => a.name.localeCompare(b.name)); break;
      case 'name-desc': sorted.sort((a, b) => b.name.localeCompare(a.name)); break;
      case 'price-asc': sorted.sort((a, b) => a.price - b.price); break;
      case 'price-desc': sorted.sort((a, b) => b.price - a.price); break;
      case 'newest':
      default: sorted.sort((a, b) => b.id - a.id);
    }
    return sorted;
  }, [products, debouncedSearch, selectedCategory, sortKey, categories]);

  const handleInputChange = (field: string, value: string | number) => {
    setNewProduct({ ...newProduct, [field]: value });
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!newProduct.name.trim()) {
      newErrors.name = t('productManager.validationName');
    } else {
      const lowerName = newProduct.name.trim().toLowerCase();
      const duplicate = products.some(
        p => p.name.toLowerCase() === lowerName && p.id !== editingProduct?.id
      );
      if (duplicate) newErrors.name = t('productManager.validationDuplicate');
    }

    if (!newProduct.price) {
      newErrors.price = t('productManager.validationPrice');
    } else {
      const priceNum = Number(newProduct.price);
      if (isNaN(priceNum) || priceNum <= 0) {
        newErrors.price = t('productManager.validationPricePositive');
      }
    }

    if (!newProduct.unit.trim()) {
      newErrors.unit = t('productManager.validationUnit');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePickImage = async () => {
    setIsUploadingImage(true);
    try {
      const file = await open({
        multiple: false,
        filters: [{ name: 'Image', extensions: ['png', 'jpg', 'jpeg', 'gif', 'webp'] }],
        title: 'Select Product Image',
      });
      if (file && typeof file === 'string') {
        const contents = await readFile(file);
        let binary = '';
        const chunkSize = 8192;
        for (let i = 0; i < contents.length; i += chunkSize) {
          const chunk = contents.slice(i, Math.min(i + chunkSize, contents.length));
          binary += String.fromCharCode.apply(null, Array.from(chunk));
        }
        const base64 = btoa(binary);
        const extension = file.split('.').pop()?.toLowerCase();
        let mimeType = 'image/jpeg';
        if (extension === 'png') mimeType = 'image/png';
        else if (extension === 'gif') mimeType = 'image/gif';
        else if (extension === 'webp') mimeType = 'image/webp';
        const dataUrl = `data:${mimeType};base64,${base64}`;
        setProductImage(dataUrl);
      }
    } catch (error) {
      console.error('Error selecting image:', error);
    } finally {
      setIsUploadingImage(false);
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingProduct(null);
    setErrors({});
    setNewProduct({ name: '', price: '', unit: 'item', category_id: 0, product_type: 'product', barcode: '', description: '', available_order_types: 'dine-in,takeaway,delivery,extra-order,dated-order' });
    setProductImage(null);
    setOriginalImage(null);
    // Reset the add wizard to its first step + empty recipe rows.
    setWizardStep(1);
    setRecipeRows([]);
    setRecipeYield(1);
  };

  const openAddModal = () => {
    setEditingProduct(null);
    setNewProduct({ name: '', price: '', unit: 'item', category_id: 0, product_type: 'product', barcode: '', description: '', available_order_types: 'dine-in,takeaway,delivery,extra-order,dated-order' });
    setProductImage(null);
    setOriginalImage(null);
    setErrors({});
    setWizardStep(1);
    setRecipeRows([]);
    setRecipeYield(1);
    setShowAddModal(true);
  };

  const openEditModal = (product: Product) => {
    setEditingProduct(product);
    setNewProduct({
      name: product.name,
      price: String(product.price),
      unit: product.unit,
      category_id: product.category_id ?? 0,
      product_type: product.product_type || 'product',
      barcode: product.barcode || '',
      description: product.description || '',
      available_order_types: product.available_order_types || 'dine-in,takeaway,delivery,extra-order,dated-order',
    });
    setProductImage(product.image ?? null);
    setOriginalImage(product.image ?? null);
    setErrors({});
    setShowAddModal(true);
  };

  const handleSaveProduct = async () => {
    if (!validateForm()) return;

    setIsSubmitting(true);
    setSubmitStatus('idle');
    setStatusMessage('');

    // Snapshot the row we're editing so we can fold updated fields into the
    // optimistic local state. This keeps the grid flicker-free after save.
    const editingId = editingProduct?.id ?? null;
    const trimmedName = newProduct.name.trim();
    const parsedPrice = Number(newProduct.price) || 0;
    const trimmedUnit = newProduct.unit.trim() || 'item';
    const nextCategoryId: number | null = newProduct.category_id > 0 ? newProduct.category_id : null;
    const nextImage: string | null = productImage || null;

    try {
      // If the recipe step fails AFTER the product row is saved, surface a
      // warning instead of dropping the newly created product from state.
      let recipeWarning: string | null = null;
      if (editingId !== null) {
        const update: UpdateProductPayload = {
          name: trimmedName,
          price: parsedPrice,
          unit: trimmedUnit,
          category_id: nextCategoryId,
          product_type: newProduct.product_type || 'product',
            barcode: newProduct.barcode || null,
          description: newProduct.description || null,
          available_order_types: newProduct.available_order_types || '',
        };
        const imageChanged = nextImage !== (originalImage || null);
        if (imageChanged) {
          update.image = nextImage;
        }
        // The Rust backend uses `.returning(Product::as_returning())`, so we
        // get the authoritative updated row back — use it for our optimistic
        // splice so local state exactly matches the DB row (including any
        // server-side transforms like updated_at timestamps).
        const updated = await invoke<Product>('update_product', { id: editingId, update });
        setProducts(prev => prev.map(p => (p.id === editingId ? updated : p)));
      } else {
        const create: NewProduct = {
          name: trimmedName,
          price: parsedPrice,
          unit: trimmedUnit,
          category_id: nextCategoryId,
          image: nextImage,
          product_type: newProduct.product_type || 'product',
            barcode: newProduct.barcode || null,
          description: newProduct.description || null,
          available_order_types: newProduct.available_order_types || '',
        };
        const result = await invoke<Product>('add_product', { product: create });

        // Optimistic insert — prepend the new product so the user sees it instantly.
        setProducts(prev => [result, ...prev]);

        // Wizard step 2 (Recipe) — if valid ingredient rows were added, build the
        // recipe + its ingredients right after the product row exists. A recipe
        // failure is caught so the already-saved product stays in the list; the
        // user gets a warning instead of a hard error.
        const validRows = recipeRows.filter(r => r.ingredient_id > 0 && r.quantity > 0);
        if (validRows.length > 0) {
          try {
            await invoke('create_recipe', {
              recipe: {
                product_id: result.id,
                recipe_type_id: 1,
                yield_quantity: recipeYield,
              },
              ingredients: validRows.map(r => ({
                recipe_id: 0,
                ingredient_id: r.ingredient_id,
                quantity: r.quantity,
                unit: r.unit || null,
                preparation_note: null,
              })),
            });
          } catch (recipeError) {
            console.error('Product saved but recipe creation failed:', recipeError);
            recipeWarning = t('productManager.recipeSaveWarning');
          }
        }
      }

      closeModal();

      // Show success toast immediately (no waiting on the network refetch).
      setSubmitStatus(recipeWarning ? 'error' : 'success');
      setStatusMessage(
        recipeWarning ||
        (editingId !== null
          ? t('productManager.successUpdated')
          : t('productManager.successAdded'))
      );

      // Quiet background refetch to reconcile with backend (no skeleton flicker).
      loadProducts({ quiet: true });

      setTimeout(() => setSubmitStatus('idle'), 3000);
    } catch (error) {
      console.error('Error saving product:', error);
      setSubmitStatus('error');
      setStatusMessage(String(error) || (editingId !== null ? t('productManager.errorUpdate') : t('productManager.errorAdd')));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Advance the add wizard. Step 1 (Basics) validates before moving on;
   * step 2 (Recipe & Options) always allows moving to the Review step.
   */
  const handleWizardNext = () => {
    if (wizardStep === 1 && !validateForm()) return;
    setWizardStep(w => (w + 1) as 1 | 2 | 3);
  };

  const openDeleteConfirmation = (product: Product) => {
    setProductToDelete(product);
    setShowDeleteModal(true);
  };

  const handleDeleteProduct = async () => {
    if (!productToDelete) return;
    const idToDelete = productToDelete.id;

    setDeletingId(idToDelete);
    setShowDeleteModal(false);

    // Optimistic remove — splices the row out so the grid updates instantly,
    // avoiding the skeleton flicker on save/delete.
    setProducts(prev => prev.filter(p => p.id !== idToDelete));

    try {
      await invoke('delete_product', { id: idToDelete });

      setSubmitStatus('success');
      setStatusMessage(t('productManager.successDeleted'));

      // Quietly reconcile with backend (no skeleton flicker).
      loadProducts({ quiet: true });

      setTimeout(() => setSubmitStatus('idle'), 3000);
    } catch (error) {
      console.error('Error deleting product:', error);
      // Quiet refetch so the grid reflects the actual server state without
      // triggering the skeleton flicker.
      loadProducts({ quiet: true });
      setSubmitStatus('error');
      setStatusMessage(String(error) || t('productManager.errorDelete'));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setDeletingId(null);
      setProductToDelete(null);
    }
  };

  // ── Bulk actions (table view) ──
  const clearSelection = () => setSelectedIds(new Set());

  const finishBulk = (message: string) => {
    clearSelection();
    setSubmitStatus('success');
    setStatusMessage(message);
    loadProducts({ quiet: true });
    setTimeout(() => setSubmitStatus('idle'), 3000);
  };

  const handleBulkDelete = async (rows: Product[]) => {
    if (rows.length === 0 || isBulkSubmitting) return;
    const ids = rows.map(p => p.id);
    setIsBulkSubmitting(true);
    try {
      // Optimistic remove — splice selected rows out so the table updates instantly.
      setProducts(prev => prev.filter(p => !ids.includes(p.id)));
      for (const id of ids) {
        await invoke('delete_product', { id });
      }
      finishBulk(t('productManager.bulkDeleted', { count: ids.length }));
    } catch (error) {
      console.error('Bulk delete failed:', error);
      loadProducts({ quiet: true });
      setSubmitStatus('error');
      setStatusMessage(String(error) || t('productManager.errorDelete'));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsBulkSubmitting(false);
    }
  };

  const handleBulkChangeCategory = async () => {
    if (isBulkSubmitting) return;
    const ids = bulkTargetIds;
    if (ids.length === 0) return;
    setBulkAction(null);
    setIsBulkSubmitting(true);
    try {
      for (const id of ids) {
        const updated = await invoke<Product>('update_product', {
          id,
          update: { category_id: bulkCategoryValue === 0 ? null : bulkCategoryValue },
        });
        setProducts(prev => prev.map(p => (p.id === updated.id ? updated : p)));
      }
      finishBulk(t('productManager.bulkCategoryUpdated', { count: ids.length }));
    } catch (error) {
      console.error('Bulk category change failed:', error);
      loadProducts({ quiet: true });
      setSubmitStatus('error');
      setStatusMessage(String(error) || t('productManager.errorUpdate'));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsBulkSubmitting(false);
    }
  };

  const handleBulkChangeType = async () => {
    if (isBulkSubmitting) return;
    const ids = bulkTargetIds;
    if (ids.length === 0) return;
    setBulkAction(null);
    setIsBulkSubmitting(true);
    try {
      for (const id of ids) {
        const updated = await invoke<Product>('update_product', {
          id,
          update: { product_type: bulkTypeValue },
        });
        setProducts(prev => prev.map(p => (p.id === updated.id ? updated : p)));
      }
      finishBulk(t('productManager.bulkTypeUpdated', { count: ids.length }));
    } catch (error) {
      console.error('Bulk type change failed:', error);
      loadProducts({ quiet: true });
      setSubmitStatus('error');
      setStatusMessage(String(error) || t('productManager.errorUpdate'));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsBulkSubmitting(false);
    }
  };

  // ── Category CRUD ──
  const openAddCategory = () => {
    setEditingCategory(null);
    // Unique color auto-assign: pick the first palette color not already in use.
    const used = new Set(categories.map(c => c.color).filter(Boolean));
    const nextColor = CATEGORY_COLOR_PALETTE.find(c => !used.has(c)) ?? CATEGORY_COLOR_PALETTE[0];
    setCategoryForm({ name: '', color: nextColor });
    setCategoryErrors({});
    setShowCategoryModal(true);
  };

  const openEditCategory = (category: Category) => {
    setEditingCategory(category);
    setCategoryForm({ name: category.name, color: category.color || CATEGORY_COLOR_PALETTE[0] });
    setCategoryErrors({});
    setShowCategoryModal(true);
  };

  const closeCategoryModal = () => {
    setShowCategoryModal(false);
    setEditingCategory(null);
    setCategoryErrors({});
  };

  const handleSaveCategory = async () => {
    const trimmedName = categoryForm.name.trim();
    if (!trimmedName) {
      setCategoryErrors({ name: t('productManager.categoryValidationName') || 'Please enter a category name' });
      return;
    }
    setIsCategorySubmitting(true);
    try {
      if (editingCategory) {
        const update: UpdateCategoryPayload = { name: trimmedName, color: categoryForm.color };
        const updated = await invoke<Category>('update_category', { id: editingCategory.id, update });
        setCategories(prev => prev.map(c => (c.id === updated.id ? updated : c)));
      } else {
        const data: NewCategory = { name: trimmedName, color: categoryForm.color };
        const created = await invoke<Category>('add_category', { data });
        setCategories(prev => [...prev, created]);
      }
      closeCategoryModal();
      setSubmitStatus('success');
      setStatusMessage(
        editingCategory
          ? t('productManager.categorySuccessUpdated') || 'Category updated'
          : t('productManager.categorySuccessAdded') || 'Category added'
      );
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } catch (error) {
      console.error('Error saving category:', error);
      setSubmitStatus('error');
      setStatusMessage(String(error));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsCategorySubmitting(false);
    }
  };

  const openDeleteCategoryConfirmation = (category: Category) => {
    setCategoryToDelete(category);
    setShowCategoryDeleteModal(true);
  };

  const handleDeleteCategory = async () => {
    if (!categoryToDelete) return;
    const id = categoryToDelete.id;
    setShowCategoryDeleteModal(false);
    setIsCategorySubmitting(true);
    try {
      await invoke('delete_category', { id });
      setCategories(prev => prev.filter(c => c.id !== id));
      setProducts(prev => prev.map(p => (p.category_id === id ? { ...p, category_id: null } : p)));
      if (selectedCategory === id) setSelectedCategory('all');
      setSubmitStatus('success');
      setStatusMessage(t('productManager.categorySuccessDeleted') || 'Category deleted');
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } catch (error) {
      console.error('Error deleting category:', error);
      setSubmitStatus('error');
      setStatusMessage(String(error));
      setTimeout(() => setSubmitStatus('idle'), 3000);
    } finally {
      setIsCategorySubmitting(false);
      setCategoryToDelete(null);
    }
  };

  const modalTitle = editingProduct ? t('productManager.editProduct') : t('productManager.addProduct');

  // ── Category → name map for table column ──
  const categoryMap = useMemo(() => {
    const map: Record<number, string> = {};
    categories.forEach(c => { map[c.id] = c.name; });
    return map;
  }, [categories]);

  // ── Inline edit handler for DataTable ──
  const handleInlineEdit = async (product: Product, key: string, value: string) => {
    const update: UpdateProductPayload = {};
    if (key === 'name') update.name = value;
    else if (key === 'price') update.price = parseFloat(value) || 0;
    else if (key === 'barcode') update.barcode = value || null;
    else return;

    try {
      const updated = await invoke<Product>('update_product', { id: product.id, update });
      setProducts(prev => prev.map(p => (p.id === updated.id ? updated : p)));
    } catch (error) {
      console.error('Inline edit failed:', error);
      throw error;
    }
  };

  // ── Table columns for product list ──
  const tableColumns: Column<Product>[] = [
    {
      key: 'name',
      label: t('productManager.productName') || 'Name',
      sortable: true,
      editable: true,
      render: (p: Product) => (
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md overflow-hidden shrink-0 bg-base-200 flex items-center justify-center">
            {p.image ? (
              <img src={p.image} alt={p.name} className="w-full h-full object-contain" />
            ) : (
              <span className="text-[10px] font-bold text-base-content/40">
                {p.name.charAt(0).toUpperCase()}
              </span>
            )}
          </div>
          <span className="font-medium truncate max-w-32" title={p.name}>
            {p.name}
          </span>
        </div>
      ),
    },        {
          key: 'barcode',
          label: t('productManager.barcode') || 'Barcode',
          sortable: true,
          editable: true,
          hideOnMobile: true,
          render: (p: Product) => (
        <span className="font-mono text-xs text-base-content/70">
          {p.barcode || (
            <span className="text-base-content/30 italic">-</span>
          )}
        </span>
      ),
    },
    {
      key: 'price',
      label: `Price (${currencySymbol})`,
      sortable: true,
      editable: true,
      editType: 'number',
      render: (p: Product) => (
        <span className="font-semibold text-primary">
          {formatPrice(p.price)}
        </span>
      ),
    },
    {          key: 'category_id',
          label: t('productManager.category') || 'Category',
          sortable: true,
          hideOnMobile: true,
          render: (p: Product) => (
        <span className="text-sm">
          {p.category_id && categoryMap[p.category_id] ? (
            <span className="badge badge-sm badge-ghost font-normal">
              {categoryMap[p.category_id]}
            </span>
          ) : (
            <span className="text-base-content/30 italic">-</span>
          )}
        </span>
      ),
    },
    {          key: 'unit',
          label: t('productManager.unit') || 'Unit',
          sortable: true,
          render: (p: Product) => (
        <span className="text-xs text-base-content/60 uppercase tracking-wider">
          {p.unit}
        </span>
      ),
    },
    {          key: '_stock',
          label: t('productManager.stock') || 'Stock',
          sortable: false,
          render: (_p: Product) => (
        <span className="text-xs text-base-content/50">
          <span className="badge badge-sm badge-ghost gap-1 font-normal">
            <span className="ri-archive-line ri-12px" />
            {t('productManager.viaIngredients') || 'Ingredients'}
          </span>
        </span>
      ),
    },
    {          key: 'product_type',
          label: t('productManager.type') || 'Type',
          sortable: true,
          hideOnMobile: true,
          render: (p: Product) => {
        const typeStyles: Record<string, string> = {
          product: 'badge-ghost',
          service: 'badge-info badge-soft',
          combo: 'badge-warning badge-soft',
          addon: 'badge-accent badge-soft',
        };
        return (
          <span className={`badge badge-sm ${typeStyles[p.product_type || 'product'] || 'badge-ghost'} capitalize`}>
            {p.product_type || 'product'}
          </span>
        );
      },
    },
    {
      key: '_actions',
      label: '',
      render: (p: Product) => (
        <div className="flex items-center gap-1 justify-end">
          <Tooltip>
            <TooltipTrigger
              render={
                <button
                  onClick={(e) => { e.stopPropagation(); openEditModal(p); }}
                  className="p-1.5 rounded-md text-base-content/40 hover:text-primary hover:bg-primary/10 transition-all"
                  aria-label={t('common.edit')}
                />
              }
            >
              <span className="ri-pencil-line ri-14px" />
            </TooltipTrigger>
            <TooltipContent>{t('common.edit')}</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger
              render={
                <button
                  onClick={(e) => { e.stopPropagation(); openDeleteConfirmation(p); }}
                  className="p-1.5 rounded-md text-base-content/40 hover:text-error hover:bg-error/10 transition-all"
                  disabled={deletingId === p.id}
                  aria-label={t('productManager.deleteTitle')}
                />
              }
            >
              {deletingId === p.id ? (
                <div className="w-3.5 h-3.5 border-2 border-error border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="ri-delete-bin-line ri-14px" />
              )}
            </TooltipTrigger>
            <TooltipContent>{t('productManager.deleteTitle')}</TooltipContent>
          </Tooltip>
        </div>
      ),
    },
  ];

  // ── Mobile card render for table rows ──
  const mobileTableRender = (p: Product) => (
    <div className="flex items-center gap-3 py-1">
      <div className="w-9 h-9 rounded-full overflow-hidden shrink-0 bg-base-200 flex items-center justify-center">
        {p.image ? (
          <img src={p.image} alt={p.name} className="w-full h-full object-contain" />
        ) : (
          <span className="text-sm font-bold text-base-content/40">
            {p.name.charAt(0).toUpperCase()}
          </span>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm truncate">{p.name}</span>
          {p.barcode && (
            <span className="font-mono text-[10px] text-base-content/40 truncate max-w-20">
              {p.barcode}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-base-content/50">
          <span className="text-primary font-semibold">{formatPrice(p.price)}</span>
          {p.category_id && categoryMap[p.category_id] && (
            <>
              <span>·</span>
              <span>{categoryMap[p.category_id]}</span>
            </>
          )}
          <span>·</span>
          <span className="uppercase">{p.unit}</span>
        </div>
      </div>
      <div className="flex gap-0.5 shrink-0">
        <Tooltip>
          <TooltipTrigger
            render={
              <button
                onClick={() => openEditModal(p)}
                className="p-1.5 rounded-md text-base-content/40 hover:text-primary"
              />
            }
          >
            <span className="ri-pencil-line ri-14px" />
          </TooltipTrigger>
          <TooltipContent>{t('common.edit')}</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger
            render={
              <button
                onClick={() => openDeleteConfirmation(p)}
                className="p-1.5 rounded-md text-base-content/40 hover:text-error"
              />
            }
          >
            <span className="ri-delete-bin-line ri-14px" />
          </TooltipTrigger>
          <TooltipContent>{t('productManager.deleteTitle')}</TooltipContent>
        </Tooltip>
      </div>
    </div>
  );

  return (
    <PageLayout
      title={
        <div className="flex flex-col">
          <span>{t('productManager.title')}</span>
          <span className="text-sm font-normal text-slate-500 dark:text-white/40">
            {t('productManager.productCount', { count: filteredProducts.length })}
          </span>
        </div>
      }
      background="bg-linear-to-br from-base-200 via-primary/10 to-base-200"
    >

      {/* Compact Stats Row */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <Card padding="sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-base-content/60">{t('productManager.totalProducts')}</span>
            <span className="text-lg font-bold text-primary">{products.length}</span>
          </div>
        </Card>
        <Card padding="sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-base-content/60">{t('productManager.filteredCount') || 'Visible'}</span>
            <span className="text-lg font-bold text-primary">{filteredProducts.length}</span>
          </div>
        </Card>
      </div>

      {/* ── Compact rounded filter bar — shared ProductFilterBar component ──
          Same bar used on Sale; see docs/shared-components.md. */}
      <ProductFilterBar
        searchValue={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder={t('productManager.searchPlaceholder') || 'Search...'}
        searchAriaLabel={t('productManager.searchPlaceholder') || 'Search products'}
        searchTestId="pm-search-input"
        searchLoading={isFiltering}
        searchClassName="flex-1 max-w-xs"
        topRowActions={
          <>
            {viewMode === 'grid' && (
              <div className="field field--sm w-32">
                <select
                  value={sortKey}
                  onChange={(e) => setSortKey(e.target.value as SortKey)}
                  aria-label={t('productManager.sortBy') || 'Sort by'}
                  className="select"
                >
                  <option value="newest">{t('productManager.sortNewest') || 'Newest'}</option>
                  <option value="name-asc">A→Z</option>
                  <option value="name-desc">Z→A</option>
                  <option value="price-asc">$↑</option>
                  <option value="price-desc">$↓</option>
                </select>
              </div>
            )}
            <Tooltip>
              <TooltipTrigger
                render={
                  <Button
                    variant="ghost"
                    shape="square"
                    size="sm"
                    onClick={() => setViewMode(prev => prev === 'grid' ? 'table' : 'grid')}
                    className="text-base-content/50 hover:text-base-content shrink-0"
                    aria-label={viewMode === 'grid' ? t('common.switchToTable') : t('common.switchToGrid')}
                  />
                }
              >
                {viewMode === 'grid'
                  ? <span className="ri-file-list-3-line ri-16px" />
                  : <span className="ri-layout-grid-line ri-16px" />}
              </TooltipTrigger>
              <TooltipContent>{viewMode === 'grid' ? t('common.switchToTable') : t('common.switchToGrid')}</TooltipContent>
            </Tooltip>
            <Button
              variant="primary"
              size="sm"
              onClick={openAddModal}
              data-testid="pm-add-button"
              className="shrink-0"
              iconStart={<span className="ri-add-line ri-14px" />}
            >
              <span className="hidden sm:inline text-xs">{t('productManager.addNewProduct')}</span>
            </Button>
          </>
        }
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        categoryAllLabel={t('productManager.allCategories') || 'All'}
        categoryTestIdPrefix="pm-category-filter"
        categoryAllTestId="pm-category-filter"
        pillsChildren={
          <>
            <button
              onClick={openAddCategory}
              data-testid="pm-manage-categories"
              className="tag tag--sm tag--ghost cursor-pointer transition-all hover:border-primary/40 hover:text-primary flex items-center gap-1"
              title={t('productManager.manageCategories') || 'Manage categories'}
            >
              <span className="ri-settings-3-line ri-12px" />
              {t('productManager.manageCategories') || 'Manage'}
            </button>
            {selectedCategory !== 'all' && (
              <Tooltip>
                <TooltipTrigger
                  render={
                    <button
                      onClick={() => setSelectedCategory('all')}
                      className="tag tag--sm tag--ghost text-base-content/40 hover:text-error transition-colors"
                    />
                  }
                >
                  <span className="ri-close-line ri-12px" />
                </TooltipTrigger>
                <TooltipContent>{t('common.clearFilter')}</TooltipContent>
              </Tooltip>
            )}
          </>
        }
      />

      {/* ── Product Grid / Table ── */}
      {viewMode === 'grid' ? (
        <AnimatePresence mode="wait">
          {isLoading ? (
            <div
              key="skeleton"
              
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-9 4xl:grid-cols-10 gap-2"
            >
              {Array.from({ length: PRODUCT_SKELETON_COUNT }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </div>
          ) : filteredProducts.length > 0 ? (
            <div
              key="grid"
              
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-9 4xl:grid-cols-10 gap-2"
            >
              {filteredProducts.map((product, index) => {
                // Single uniform card color (theme primary) — the default look.
                const color = PRODUCT_CARD_COLORS[0];
                const categoryColor = null;
                return (
                  <ProductCard
                    key={product.id}
                    product={product}
                    color={color}
                    categoryColor={categoryColor}
                    currency={currencySymbol}
                    index={index}
                    onClick={() => openEditModal(product)}
                    onEdit={() => openEditModal(product)}
                    onDelete={() => openDeleteConfirmation(product)}
                  />
                );
              })}
            </div>
          ) : (
            <div
              key="empty"
              
            >
              <Card padding="2xl" center>
                <span className="ri-image-line w-16 h-16 mx-auto mb-4 text-base-content/40" />
                <p className="text-base-content/60 text-lg mb-3">
                  {t('productManager.noProducts')}
                </p>
                {(searchQuery || selectedCategory !== 'all') && (
                  <button
                    onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}
                    className="text-sm font-medium text-primary hover:underline transition-colors"
                  >
                    {t('common.clear')}
                  </button>
                )}
              </Card>
            </div>
          )}
        </AnimatePresence>
      ) : (
        <DataTable<Product>
          columns={tableColumns}
          data={filteredProducts}
          keyExtractor={(p) => p.id}
          emptyMessage={t('productManager.noProducts')}
          onEditSave={handleInlineEdit}
          exportable
          fileName="products"
          mobileRender={mobileTableRender}
          selectable
          selectedIds={selectedIds}
          onSelectionChange={(ids) => setSelectedIds(new Set(Array.from(ids) as number[]))}
          bulkActions={[
            {
              key: 'bulk-delete',
              label: t('common.delete'),
              icon: <span className="ri-delete-bin-line ri-12px" />,
              className: 'btn-soft btn-error',
              testId: 'pm-bulk-delete',
              onClick: (rows: Product[]) => {
                if (!window.confirm(t('productManager.bulkDeleteConfirm', { count: rows.length }))) return;
                void handleBulkDelete(rows);
              },
            },
            {
              key: 'bulk-category',
              label: t('productManager.bulkChangeCategory'),
              icon: <span className="ri-folder-line ri-12px" />,
              testId: 'pm-bulk-category',
              onClick: (rows: Product[]) => {
                setBulkTargetIds(rows.map(p => p.id));
                setBulkAction('category');
                setBulkCategoryValue(0);
              },
            },
            {
              key: 'bulk-type',
              label: t('productManager.bulkChangeType'),
              icon: <span className="ri-price-tag-line ri-12px" />,
              testId: 'pm-bulk-type',
              onClick: (rows: Product[]) => {
                setBulkTargetIds(rows.map(p => p.id));
                setBulkAction('type');
                setBulkTypeValue('product');
              },
            },
          ]}
        />
      )}

      {/* Add / Edit Modal (unified) — shared Modal component (FlyonUI BEM frame) */}
      <Modal
        isOpen={showAddModal}
        onClose={closeModal}
        title={modalTitle}
        size="lg"
        scroll
        contentTestId="pm-modal"
        footer={
          editingProduct ? (
            <div className="flex gap-2 w-full">
              <button
                onClick={closeModal}
                className="btn btn-ghost flex-1 disabled:opacity-50"
                disabled={isSubmitting}
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleSaveProduct}
                data-testid="pm-submit"
                className="btn btn-primary flex-1 disabled:opacity-50 gap-2"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    {t('common.updating') || 'Updating...'}
                  </>
                ) : (
                  <>
                    <span className="ri-edit-line" />
                    {t('common.update')}
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="flex gap-2 w-full">
              <button
                onClick={closeModal}
                className="btn btn-ghost disabled:opacity-50"
                disabled={isSubmitting}
              >
                {t('common.cancel')}
              </button>
              {wizardStep > 1 && (
                <button
                  onClick={() => setWizardStep(w => (w - 1) as 1 | 2 | 3)}
                  className="btn btn-ghost gap-1 disabled:opacity-50"
                  disabled={isSubmitting}
                >
                  <span className="ri-arrow-left-s-line ri-14px" />
                  {t('common.back') || 'Back'}
                </button>
              )}
              {wizardStep < 3 ? (
                <button
                  onClick={handleWizardNext}
                  data-testid="pm-next"
                  className="btn btn-primary flex-1 gap-1 disabled:opacity-50"
                  disabled={isSubmitting}
                >
                  {wizardStep === 1 ? (t('productManager.wizardToRecipe') || 'Recipe') : (t('productManager.wizardToReview') || 'Review')}
                  <span className="ri-arrow-right-s-line ri-14px" />
                </button>
              ) : (
                <button
                  onClick={handleSaveProduct}
                  data-testid="pm-submit"
                  className="btn btn-primary flex-1 gap-2 disabled:opacity-50"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      {t('productManager.adding')}
                    </>
                  ) : (
                    <>
                      <span className="ri-check-line" />
                      {t('productManager.addProduct')}
                    </>
                  )}
                </button>
              )}
            </div>
          )
        }
      >
        <div className="space-y-4">
              {/* Wizard steps indicator — add mode only (edit keeps the single form) */}
              {!editingProduct && (
                <div className="flex items-center gap-1.5 mb-1">
                  {[
                    { step: 1 as const, label: t('productManager.wizardBasics') || 'Basics', icon: 'ri-price-tag-3-line' },
                    { step: 2 as const, label: t('productManager.wizardRecipe') || 'Recipe & Options', icon: 'ri-restaurant-line' },
                    { step: 3 as const, label: t('productManager.wizardReview') || 'Review', icon: 'ri-eye-line' },
                  ].map(({ step, label, icon }) => (
                    <button
                      key={step}
                      type="button"
                      onClick={() => step < wizardStep && setWizardStep(step)}
                      disabled={isSubmitting}
                      className={`flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg border text-[11px] font-semibold transition-all
                        ${wizardStep === step
                          ? 'border-primary bg-primary/10 text-primary dark:bg-primary/20'
                          : wizardStep > step
                            ? 'border-success/40 bg-success/5 text-success/80 dark:bg-success/10'
                            : 'border-base-300/50 text-base-content/40 hover:border-primary/30'
                        }`}
                    >
                      <span className={`${icon} ri-14px`} />
                      {label}
                    </button>
                  ))}
                </div>
              )}

              {/* Step 1 — Basics (image, name, type, pricing, units, meta) */}
              {(editingProduct || wizardStep === 1) && (
              <>
              {/* Product Image */}
              <div>
                <label className="block text-base-content mb-2">{t('productManager.productImageOptional') || 'Product Image (optional)'}</label>
                <div className="flex items-center gap-3">
                  {productImage ? (
                    <div className="relative w-20 h-20 shrink-0">
                      <img
                        src={productImage}
                        alt="Product preview"
                        className="w-20 h-20 rounded-full object-cover border-2 border-slate-300 dark:border-gray-600"
                      />
                      <Tooltip>
                        <TooltipTrigger
                          render={
                            <button
                              type="button"
                              onClick={() => setProductImage(null)}
                              className="absolute -top-2 -right-2 bg-error text-error-content rounded-full p-0.5
                                hover:brightness-90 transition-all shadow-lg"
                            />
                          }
                        >
                          <span className="ri-close-line ri-12px" />
                        </TooltipTrigger>
                        <TooltipContent>{t('common.removeImage')}</TooltipContent>
                      </Tooltip>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={handlePickImage}
                      disabled={isUploadingImage}
                      className="flex flex-col items-center justify-center w-20 h-20 rounded-full
                        bg-base-100/30 border-2 border-dashed border-slate-300 dark:border-gray-600
                        text-base-content/50 hover:border-primary hover:bg-primary/5
                        transition-all cursor-pointer disabled:opacity-50"
                    >
                      {isUploadingImage ? (
                        <div
                          className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin"
                        />
                      ) : (
                        <span className="ri-image-line ri-24px" />
                      )}
                    </button>
                  )}
                  <p className="text-xs text-base-content/50">
                    PNG, JPG, GIF, WebP<br />Optional product photo
                  </p>
                </div>
              </div>

              <div className={`field ${errors.name ? 'field--error' : ''}`}>
                <label className="label-text">{t('productManager.productName')}</label>
                <input
                  type="text"
                  value={newProduct.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  data-testid="pm-name-input"
                  className="input w-full"
                  placeholder={t('productManager.namePlaceholder')}
                  disabled={isSubmitting}
                />
                {errors.name && (
                  <p className="helper-text">{errors.name}</p>
                )}
              </div>

              {/* Product Type */}
              {!editingProduct && (
                <div>
                  <label className="block text-base-content mb-2 flex items-center gap-2">
                    <span className="ri-price-tag-line ri-16px text-accent" />
                    {t('productManager.productType') || 'Product Type'}
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {[
                      { value: 'product', label: t('productManager.typeProduct') || 'Product', icon: 'package' },
                      { value: 'service', label: t('productManager.typeService') || 'Service', icon: 'settings' },
                      { value: 'combo', label: t('productManager.typeCombo') || 'Combo', icon: 'layers-union' },
                      { value: 'addon', label: t('productManager.typeAddon') || 'Add-on', icon: 'plus' },
                    ].map(({ value, label, icon }) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => handleInputChange('product_type', value)}
                        disabled={isSubmitting}
                        className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all
                          ${newProduct.product_type === value
                            ? 'border-teal-500 bg-primary/5 text-primary'
                            : 'border-slate-200 dark:border-slate-600 bg-base-100/50 text-slate-600 dark:text-slate-400 hover:border-primary/50'
                          }`}
                      >
                        <span className={iconClass(icon, 'w-5 h-5')} />
                        <span className="text-xs font-semibold">{label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Available Order Types — edit mode only (add wizard shows this on step 2) */}
              {editingProduct && (
                <div>
                  <label className="block text-base-content mb-2 flex items-center gap-2">
                    <span className="ri-store-2-line ri-16px text-primary/70" />
                    {t('productManager.availableOrderTypes') || 'Available Order Types'}
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                    {ORDER_TYPE_OPTIONS.map(ot => {
                      const selected = (newProduct.available_order_types || '').split(',').map(s => s.trim()).filter(Boolean);
                      const isOn = selected.includes(ot.value);
                      return (
                        <button
                          key={ot.value}
                          type="button"
                          onClick={() => {
                            const next = isOn
                              ? selected.filter(v => v !== ot.value).join(',')
                              : [...selected, ot.value].join(',');
                            handleInputChange('available_order_types', next);
                          }}
                          disabled={isSubmitting}
                          className={`flex items-center gap-1.5 px-2.5 py-2 rounded-lg border-2 transition-all text-xs font-medium
                            ${isOn
                              ? 'border-primary bg-primary/5 text-primary'
                              : 'border-slate-200 dark:border-slate-600 bg-base-100/50 text-slate-600 dark:text-slate-400 hover:border-primary/50'
                            }`}
                        >
                          <span className={`w-2 h-2 rounded-full shrink-0 ${isOn ? '' : 'bg-base-300'}`} style={isOn ? { backgroundColor: ot.color } : undefined} />
                          {t(ot.i18nKey, ot.label)}
                        </button>
                      );
                    })}
                  </div>
                  <p className="helper-text mt-1">
                    {t('productManager.availableOrderTypesHint') || 'Products are hidden from order types that are not selected'}
                  </p>
                </div>
              )}

              {/* Price + Unit in a 2-column row */}
              <div className="grid grid-cols-2 gap-3">
                <div className={`field ${errors.price ? 'field--error' : ''}`}>
                  <label className="label-text">
                    <span className="ri-money-dollar-circle-line ri-14px inline-block mr-1 text-primary/70" />
                    Price ({currencySymbol})
                  </label>
                  <input
                    type="number"
                    value={newProduct.price}
                    onChange={(e) => handleInputChange('price', e.target.value)}
                    data-testid="pm-price-input"
                    className="input w-full h-9 text-sm"
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                    disabled={isSubmitting}
                  />
                  {errors.price && (
                    <p className="helper-text">{errors.price}</p>
                  )}
                </div>

                <div className={`field ${errors.unit ? 'field--error' : ''}`}>
                  <label className="label-text">
                    <span className="ri-box-3-line ri-14px inline-block mr-1 text-primary/70" />
                    Unit
                  </label>
                  <input
                    type="text"
                    value={newProduct.unit}
                    onChange={(e) => handleInputChange('unit', e.target.value)}
                    data-testid="pm-unit-input"
                    className="input w-full h-9 text-sm"
                    placeholder="item, kg, pcs"
                    disabled={isSubmitting}
                  />
                  {errors.unit && (
                    <p className="helper-text">{errors.unit}</p>
                  )}
                </div>
              </div>


              {/* Barcode + Description */}
              <div>
                <label className="block text-base-content mb-1.5 text-xs font-medium">
                  <span className="ri-barcode-line ri-14px inline-block mr-1 text-primary/70" />
                  SKU / Barcode
                </label>
                <input
                  type="text"
                  value={newProduct.barcode}
                  onChange={(e) => handleInputChange('barcode', e.target.value)}
                  className="input w-full h-9 text-sm"
                  placeholder="e.g. 8901234567890"
                  disabled={isSubmitting}
                />
              </div>

              <div>
                <label className="block text-base-content mb-1.5 text-xs font-medium">
                  <span className="ri-align-left ri-14px inline-block mr-1 text-primary/70" />
                  Description
                </label>
                <textarea
                  value={newProduct.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="textarea w-full text-sm resize-none"
                  placeholder={t('productManager.descriptionPlaceholder') || 'Product description for menu & tickets...'}
                  rows={2}
                  disabled={isSubmitting}
                />
              </div>

              {/* Category selector */}
              {categories.length > 0 && (
                <div>
                  <label className="block text-base-content mb-1.5 text-xs font-medium">
                    <span className="ri-folder-line ri-14px inline-block mr-1 text-primary/70" />
                    {t('productManager.category') || 'Category'}
                  </label>
                  <select
                    value={newProduct.category_id ? String(newProduct.category_id) : ''}
                    onChange={(e) => handleInputChange('category_id', e.target.value ? Number(e.target.value) : 0)}
                    disabled={isSubmitting}
                    className="select w-full h-9 text-sm"
                  >
                    <option value="">{t('productManager.noCategory') || '- No category -'}</option>
                    {categories.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              )}
              </>
              )}

              {/* Step 2 — Recipe & Options (ingredient rows + yield + order types) */}
              {!editingProduct && wizardStep === 2 && (
                <div className="space-y-4">
                  {/* Recipe ingredients builder */}
                  <div>
                    <label className="block text-base-content mb-2 flex items-center gap-2">
                      <span className="ri-restaurant-2-line ri-16px text-accent" />
                      {t('productManager.recipeIngredients') || 'Recipe Ingredients'}
                    </label>
                    <p className="text-xs text-base-content/50 mb-3">
                      {t('productManager.recipeHint') || 'Define the ingredients this product consumes — stock is deducted on sale.'}
                    </p>
                    {ingredients.length === 0 ? (
                      <p className="text-xs text-base-content/40 italic">
                        {t('productManager.noIngredients') || 'No active ingredients yet. Add them in Inventory first.'}
                      </p>
                    ) : (
                      <>
                        <div className="space-y-2">
                          {recipeRows.map((row, idx) => (
                            <div key={idx} className="flex items-center gap-2">
                              <select
                                value={row.ingredient_id}
                                onChange={(e) => {
                                  const next = [...recipeRows];
                                  next[idx] = { ...row, ingredient_id: Number(e.target.value), unit: ingredients.find(i => i.id === Number(e.target.value))?.unit || row.unit };
                                  setRecipeRows(next);
                                }}
                                disabled={isSubmitting}
                                className="select flex-1 h-9 text-sm"
                              >
                                <option value={0}>{t('productManager.selectIngredient') || 'Select ingredient...'}</option>
                                {ingredients.map(i => (
                                  <option key={i.id} value={i.id}>{i.name} ({i.unit})</option>
                                ))}
                              </select>
                              <input
                                type="number"
                                value={row.quantity}
                                min="0"
                                step="0.01"
                                onChange={(e) => {
                                  const next = [...recipeRows];
                                  next[idx] = { ...row, quantity: Number(e.target.value) || 0 };
                                  setRecipeRows(next);
                                }}
                                disabled={isSubmitting}
                                className="input w-20 h-9 text-sm"
                                placeholder="Qty"
                              />
                              <span className="text-xs text-base-content/50 w-10">{row.unit || 'unit'}</span>
                              <Tooltip>
                                <TooltipTrigger
                                  render={
                                    <button
                                      type="button"
                                      onClick={() => setRecipeRows(prev => prev.filter((_, i) => i !== idx))}
                                      disabled={isSubmitting}
                                      className="p-1.5 text-base-content/40 hover:text-error transition-colors"
                                      aria-label={t('common.remove') || 'Remove'}
                                    />
                                  }
                                >
                                  <span className="ri-delete-bin-line ri-14px" />
                                </TooltipTrigger>
                                <TooltipContent>{t('common.remove') || 'Remove'}</TooltipContent>
                              </Tooltip>
                            </div>
                          ))}
                        </div>
                        <button
                          type="button"
                          onClick={() => setRecipeRows(prev => [...prev, { ingredient_id: 0, quantity: 0, unit: '' }])}
                          disabled={isSubmitting}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                            bg-accent/10 text-accent hover:bg-accent/20 transition-colors"
                        >
                          <span className="ri-add-line ri-14px" />
                          {t('productManager.addIngredient') || 'Add ingredient'}
                        </button>
                      </>
                    )}
                  </div>

                  {/* Yield quantity */}
                  <div>
                    <label className="block text-base-content mb-1.5 text-xs font-medium">
                      <span className="ri-stack-line ri-14px inline-block mr-1 text-primary/70" />
                      {t('productManager.recipeYield') || 'Yield quantity'}
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        value={recipeYield}
                        min="1"
                        step="1"
                        onChange={(e) => setRecipeYield(Math.max(1, parseInt(e.target.value) || 1))}
                        disabled={isSubmitting}
                        className="input w-24 h-9 text-sm"
                      />
                      <span className="text-xs text-base-content/50">{t('productManager.recipeYieldHint') || 'Servings produced by one batch of the recipe above'}</span>
                    </div>
                  </div>

                  {/* Available Order Types — where this product can be sold */}
                  <div>
                    <label className="block text-base-content mb-2 flex items-center gap-2">
                      <span className="ri-store-2-line ri-16px text-primary/70" />
                      {t('productManager.availableOrderTypes') || 'Available Order Types'}
                    </label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
                      {ORDER_TYPE_OPTIONS.map(ot => {
                        const selected = (newProduct.available_order_types || '').split(',').map(s => s.trim()).filter(Boolean);
                        const isOn = selected.includes(ot.value);
                        return (
                          <button
                            key={ot.value}
                            type="button"
                            onClick={() => {
                              const next = isOn
                                ? selected.filter(v => v !== ot.value).join(',')
                                : [...selected, ot.value].join(',');
                              handleInputChange('available_order_types', next);
                            }}
                            disabled={isSubmitting}
                            className={`flex items-center gap-1.5 px-2.5 py-2 rounded-lg border-2 transition-all text-xs font-medium
                              ${isOn
                                ? 'border-primary bg-primary/5 text-primary'
                                : 'border-slate-200 dark:border-slate-600 bg-base-100/50 text-slate-600 dark:text-slate-400 hover:border-primary/50'
                              }`}
                          >
                            <span className={`w-2 h-2 rounded-full shrink-0 ${isOn ? '' : 'bg-base-300'}`} style={isOn ? { backgroundColor: ot.color } : undefined} />
                            {t(ot.i18nKey, ot.label)}
                          </button>
                        );
                      })}
                    </div>
                    <p className="helper-text mt-1">
                      {t('productManager.availableOrderTypesHint') || 'Products are hidden from order types that are not selected'}
                    </p>
                  </div>
                </div>
              )}

              {/* Step 3 — Review summary before saving */}
              {!editingProduct && wizardStep === 3 && (
                <div className="space-y-4">
                  <div className="rounded-xl border border-base-300/40 divide-y divide-base-300/30">
                    <div className="flex justify-between px-3.5 py-2.5 text-sm">
                      <span className="text-base-content/60">{t('productManager.productName')}</span>
                      <span className="font-medium text-base-content">{newProduct.name || '—'}</span>
                    </div>
                    <div className="flex justify-between px-3.5 py-2.5 text-sm">
                      <span className="text-base-content/60">{t('productManager.type') || 'Type'}</span>
                      <span className="font-medium text-base-content capitalize">{newProduct.product_type || 'product'}</span>
                    </div>
                    <div className="flex justify-between px-3.5 py-2.5 text-sm">
                      <span className="text-base-content/60">{t('productManager.category') || 'Category'}</span>
                      <span className="font-medium text-base-content">
                        {newProduct.category_id ? (categories.find(c => c.id === newProduct.category_id)?.name || '—') : '—'}
                      </span>
                    </div>
                    <div className="flex justify-between px-3.5 py-2.5 text-sm">
                      <span className="text-base-content/60">Price</span>
                      <span className="font-medium text-base-content">{currencySymbol} {Number(newProduct.price) || 0}</span>
                    </div>
                    <div className="flex justify-between px-3.5 py-2.5 text-sm">
                      <span className="text-base-content/60">{t('productManager.unit') || 'Unit'}</span>
                      <span className="font-medium text-base-content">{newProduct.unit || '—'}</span>
                    </div>
                    <div className="flex justify-between px-3.5 py-2.5 text-sm">
                      <span className="text-base-content/60">{t('productManager.recipeIngredients') || 'Ingredients'}</span>
                      <span className="font-medium text-base-content">
                        {recipeRows.length === 0
                          ? t('productManager.noRecipe') || 'None'
                          : `${recipeRows.length} × ${t('productManager.recipeYield') || 'yield'} ${recipeYield}`}
                      </span>
                    </div>
                  </div>
                  {recipeRows.length > 0 && (
                    <div className="rounded-lg bg-base-100/60 border border-base-300/30 px-3 py-2">
                      {recipeRows.map((row, idx) => (
                        <div key={idx} className="flex justify-between text-xs text-base-content/70 py-1">
                          <span>{ingredients.find(i => i.id === row.ingredient_id)?.name || `#${row.ingredient_id}`}</span>
                          <span className="tabular-nums">{row.quantity} {row.unit || ''}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

            </div>
        </Modal>

      {/* Delete Confirmation Modal — shared ConfirmDialog */}
      <ConfirmDialog
        isOpen={showDeleteModal && !!productToDelete}
        onClose={() => { setShowDeleteModal(false); setProductToDelete(null); }}
        onConfirm={handleDeleteProduct}
        title={t('productManager.deleteTitle')}
        message={t('productManager.deleteConfirm')}
        itemName={productToDelete?.name ?? ''}
        description={t('productManager.deleteWarning')}
        confirmLabel={t('productManager.confirmDelete')}
        variant="danger"
      />

      {/* Bulk Change Category Modal */}
      <Modal
        isOpen={bulkAction === 'category'}
        onClose={() => setBulkAction(null)}
        title={t('productManager.bulkChangeCategory')}
        size="sm"
        footer={
          <div className="flex gap-2 w-full">
            <button
              onClick={() => setBulkAction(null)}
              className="btn btn-ghost flex-1"
              disabled={isBulkSubmitting}
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleBulkChangeCategory}
              data-testid="pm-bulk-category-apply"
              className="btn btn-primary flex-1 gap-1.5"
              disabled={isBulkSubmitting}
            >
              {isBulkSubmitting ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="ri-folder-line ri-14px" />
              )}
              {isBulkSubmitting ? t('productManager.saving') : t('common.save')}
            </button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-sm text-base-content/60">
            {t('productManager.bulkCategoryHint', { count: bulkTargetIds.length })}
          </p>
          <div className="field">
            <label className="label-text">{t('productManager.category')}</label>
            <select
              value={bulkCategoryValue ? String(bulkCategoryValue) : ''}
              onChange={(e) => setBulkCategoryValue(e.target.value ? Number(e.target.value) : 0)}
              className="select w-full"
              data-testid="pm-bulk-category-select"
            >
              <option value="">{t('productManager.noCategory') || '— No category —'}</option>
              {categories.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>
      </Modal>

      {/* Bulk Change Type Modal */}
      <Modal
        isOpen={bulkAction === 'type'}
        onClose={() => setBulkAction(null)}
        title={t('productManager.bulkChangeType')}
        size="sm"
        footer={
          <div className="flex gap-2 w-full">
            <button
              onClick={() => setBulkAction(null)}
              className="btn btn-ghost flex-1"
              disabled={isBulkSubmitting}
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleBulkChangeType}
              data-testid="pm-bulk-type-apply"
              className="btn btn-primary flex-1 gap-1.5"
              disabled={isBulkSubmitting}
            >
              {isBulkSubmitting ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="ri-price-tag-line ri-14px" />
              )}
              {isBulkSubmitting ? t('productManager.saving') : t('common.save')}
            </button>
          </div>
        }
      >
        <div className="space-y-3">
          <p className="text-sm text-base-content/60">
            {t('productManager.bulkTypeHint', { count: bulkTargetIds.length })}
          </p>
          <div className="field">
            <label className="label-text">{t('productManager.type')}</label>
            <select
              value={bulkTypeValue}
              onChange={(e) => setBulkTypeValue(e.target.value)}
              className="select w-full"
              data-testid="pm-bulk-type-select"
            >
              <option value="product">{t('productManager.typeProduct') || 'Product'}</option>
              <option value="service">{t('productManager.typeService') || 'Service'}</option>
              <option value="combo">{t('productManager.typeCombo') || 'Combo'}</option>
              <option value="addon">{t('productManager.typeAddon') || 'Add-on'}</option>
            </select>
          </div>
        </div>
      </Modal>

      {/* Category CRUD Modal — shared Modal component */}
      <Modal
        isOpen={showCategoryModal}
        onClose={closeCategoryModal}
        title={editingCategory ? t('productManager.editCategory') : t('productManager.addCategory')}
        size="sm"
        footer={
          <div className="flex gap-2 w-full">
            <button
              onClick={closeCategoryModal}
              className="btn btn-ghost flex-1 disabled:opacity-50"
              disabled={isCategorySubmitting}
            >
              {t('common.cancel')}
            </button>
            <button
              onClick={handleSaveCategory}
              data-testid="pm-category-submit"
              className="btn btn-primary flex-1 disabled:opacity-50 gap-2"
              disabled={isCategorySubmitting}
            >
              {isCategorySubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {t('productManager.saving') || 'Saving...'}
                </>
              ) : (
                <>
                  <span className="ri-check-line" />
                  {editingCategory ? t('common.update') : t('productManager.addCategory')}
                </>
              )}
            </button>
          </div>
        }
      >
        <div className="space-y-4">
              {/* Category name */}
              <div className={`field ${categoryErrors.name ? 'field--error' : ''}`}>
                <label className="label-text">{t('productManager.categoryName')}</label>
                <input
                  type="text"
                  value={categoryForm.name}
                  onChange={(e) => {
                    setCategoryForm(prev => ({ ...prev, name: e.target.value }));
                    if (categoryErrors.name) setCategoryErrors({});
                  }}
                  data-testid="pm-category-name-input"
                  className="input w-full"
                  placeholder={t('productManager.categoryNamePlaceholder') || 'e.g. Burgers, Sides...'}
                  disabled={isCategorySubmitting}
                />
                {categoryErrors.name && (
                  <p className="helper-text">{categoryErrors.name}</p>
                )}
              </div>

              {/* Color palette picker */}
              <div>
                <label className="label-text">
                  {t('productManager.categoryColor') || 'Color'}
                </label>
                <div className="flex flex-wrap items-center gap-2 mt-1.5">
                  {CATEGORY_COLOR_PALETTE.map(color => (
                    <Tooltip key={color}>
                      <TooltipTrigger
                        render={
                          <button
                            type="button"
                            onClick={() => setCategoryForm(prev => ({ ...prev, color }))}
                            aria-label={`Color ${color}`}
                            className={`w-7 h-7 rounded-full transition-all cursor-pointer
                              hover:scale-110 active:scale-95 ring-2 ring-offset-2 ring-offset-base-100
                              ${categoryForm.color === color ? 'ring-base-content/60 scale-110' : 'ring-transparent'}`}
                            style={{ backgroundColor: color }}
                          />
                        }
                      />
                      <TooltipContent>{color}</TooltipContent>
                    </Tooltip>
                  ))}
                  <Tooltip>
                    <TooltipTrigger
                      render={
                        <label className="relative w-7 h-7 rounded-full overflow-hidden border border-base-300/50 cursor-pointer hover:scale-110 transition-transform">
                          <span
                            className="absolute inset-0 flex items-center justify-center text-[10px]"
                            style={{ backgroundColor: 'repeating-conic-gradient(#d1d5db 0% 25%, #f9fafb 0% 50%) 0 0/12px 12px' }}
                          />
                          <input
                            type="color"
                            value={/^#[0-9a-fA-F]{6}$/.test(categoryForm.color) ? categoryForm.color : '#f97316'}
                            onChange={(e) => setCategoryForm(prev => ({ ...prev, color: e.target.value }))}
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            aria-label={t('productManager.categoryCustomColor') || 'Custom color'}
                          />
                          <span className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <span className="ri-dropper-line ri-12px text-base-content/70" />
                          </span>
                        </label>
                      }
                    />
                    <TooltipContent>{t('productManager.categoryCustomColor') || 'Custom color'}</TooltipContent>
                  </Tooltip>
                </div>
                {/* Live preview */}
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-xs text-base-content/50">{t('productManager.colorPreview') || 'Preview'}:</span>
                  <span
                    className="px-2.5 py-1 rounded-lg text-xs font-semibold border"
                    style={{ backgroundColor: hexToRgba(categoryForm.color, 0.14), borderColor: hexToRgba(categoryForm.color, 0.5), color: categoryForm.color }}
                  >
                    {categoryForm.name.trim() || (t('productManager.category') || 'Category')}
                  </span>
                </div>
              </div>

              {/* Existing categories list with edit / delete */}
              {categories.length > 0 && (
                <div className="border-t border-base-300/20 pt-3 mt-2">
                  <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-2">
                    {t('productManager.existingCategories') || 'Existing categories'}
                  </p>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                    {categories.map(cat => (
                      <div
                        key={cat.id}
                        className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg border border-base-300/20 bg-base-100/50"
                      >
                        <span
                          className="w-3 h-3 rounded-full shrink-0"
                          style={{ backgroundColor: cat.color || '#94a3b8' }}
                        />
                        <span className="flex-1 text-sm font-medium truncate">{cat.name}</span>
                        <Tooltip>
                          <TooltipTrigger
                            render={
                              <button
                                onClick={() => openEditCategory(cat)}
                                className="p-1 rounded-md text-base-content/40 hover:text-primary hover:bg-primary/10 transition-all"
                                aria-label={t('common.edit')}
                              />
                            }
                          >
                            <span className="ri-pencil-line ri-14px" />
                          </TooltipTrigger>
                          <TooltipContent>{t('common.edit')}</TooltipContent>
                        </Tooltip>
                        <Tooltip>
                          <TooltipTrigger
                            render={
                              <button
                                onClick={() => openDeleteCategoryConfirmation(cat)}
                                className="p-1 rounded-md text-base-content/40 hover:text-error hover:bg-error/10 transition-all"
                                aria-label={t('productManager.deleteCategory')}
                              />
                            }
                          >
                            <span className="ri-delete-bin-line ri-14px" />
                          </TooltipTrigger>
                          <TooltipContent>{t('productManager.deleteCategory')}</TooltipContent>
                        </Tooltip>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
        </Modal>

      {/* Category Delete Confirmation Modal — shared ConfirmDialog */}
      <ConfirmDialog
        isOpen={showCategoryDeleteModal && !!categoryToDelete}
        onClose={() => { setShowCategoryDeleteModal(false); setCategoryToDelete(null); }}
        onConfirm={handleDeleteCategory}
        title={t('productManager.deleteCategory')}
        message={t('productManager.deleteCategoryConfirm') || 'Delete this category?'}
        itemName={categoryToDelete?.name ?? ''}
        description={t('productManager.deleteCategoryWarning') || 'Products in this category will become uncategorized.'}
        confirmLabel={t('productManager.confirmDelete')}
        variant="danger"
      />

      {/* Success Message */}
      {submitStatus === 'success' && (
        <div
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-success"
        >
          <span className="ri-check-line text-xl" />
          {statusMessage}
        </div>
      )}

      {/* Error Message */}
      {submitStatus === 'error' && (
        <div
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-error max-w-md"
        >
          <span className="ri-alert-line text-xl" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Keyboard Shortcut Help Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcutHelp}
        onClose={() => setShowShortcutHelp(false)}
      />
    </PageLayout>
  );
}
