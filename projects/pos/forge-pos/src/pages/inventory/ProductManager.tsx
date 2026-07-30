import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';
import { readFile } from '@tauri-apps/plugin-fs';
import { Product, NewProduct, UpdateProductPayload, Category } from '../../types';
import Card from '../../components/layout/Card';
import DataTable, { type Column } from '../../components/data/DataTable';
import ProductCard, { PRODUCT_CARD_COLORS, ProductCardSkeleton, PRODUCT_SKELETON_COUNT } from '../../components/data/ProductCard';
import PageLayout from '../../components/layout/PageLayout';
import { iconClass } from '../../lib/icons';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import { useCurrency } from '../../contexts/CurrencyContext';

interface FormErrors {
  name?: string;
  price?: string;
  unit?: string;
}

type SortKey = 'newest' | 'name-asc' | 'name-desc' | 'price-asc' | 'price-desc';

export default function ProductManager() {
  const { t } = useTranslation();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [newProduct, setNewProduct] = useState({ name: '', price: '', unit: 'item', category_id: 0 as number | 0, product_type: 'product', prepare_time_minutes: 0, barcode: '', description: '' });
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
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

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
        return;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showAddModal, showDeleteModal]);


  const loadProducts = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [productsRes, categoriesRes] = await Promise.all([
        invoke<Product[]>('get_products'),
        invoke<Category[]>('get_categories').catch(() => []),
      ]);
      setProducts(productsRes);
      setCategories(categoriesRes || []);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  // ----- Derived: filtered + sorted products -----
  const filteredProducts = useMemo(() => {
    let result = products;
    const query = debouncedSearch.trim().toLowerCase();
    if (query) {
      result = result.filter(p => p.name.toLowerCase().includes(query));
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
  }, [products, debouncedSearch, selectedCategory, sortKey]);

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
    setNewProduct({ name: '', price: '', unit: 'item', category_id: 0, product_type: 'product', prepare_time_minutes: 0, barcode: '', description: '' });
    setProductImage(null);
    setOriginalImage(null);
  };

  const openAddModal = () => {
    setEditingProduct(null);
    setNewProduct({ name: '', price: '', unit: 'item', category_id: 0, product_type: 'product', prepare_time_minutes: 0, barcode: '', description: '' });
    setProductImage(null);
    setOriginalImage(null);
    setErrors({});
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
      prepare_time_minutes: product.prepare_time_minutes || 0,
      barcode: product.barcode || '',
      description: product.description || '',
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
      if (editingId !== null) {
        const update: UpdateProductPayload = {
          name: trimmedName,
          price: parsedPrice,
          unit: trimmedUnit,
          category_id: nextCategoryId,
          product_type: newProduct.product_type || 'product',
          prepare_time_minutes: newProduct.prepare_time_minutes,
          barcode: newProduct.barcode || null,
          description: newProduct.description || null,
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
          prepare_time_minutes: newProduct.prepare_time_minutes,
          barcode: newProduct.barcode || null,
          description: newProduct.description || null,
        };
        const result = await invoke<Product>('add_product', { product: create });

        // Optimistic insert — prepend the new product so the user sees it instantly.
        setProducts(prev => [result, ...prev]);
      }

      closeModal();

      // Show success toast immediately (no waiting on the network refetch).
      setSubmitStatus('success');
      setStatusMessage(
        editingId !== null
          ? t('productManager.successUpdated')
          : t('productManager.successAdded')
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
            <span className="text-base-content/30 italic">—</span>
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
            <span className="text-base-content/30 italic">—</span>
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
            <span className="icon-[tabler--package] w-3 h-3" />
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
          <button
            onClick={(e) => { e.stopPropagation(); openEditModal(p); }}
            className="p-1.5 rounded-md text-base-content/40 hover:text-primary hover:bg-primary/10 transition-all"
            aria-label={t('common.edit')}
          >
            <span className="icon-[tabler--pencil] w-3.5 h-3.5" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); openDeleteConfirmation(p); }}
            className="p-1.5 rounded-md text-base-content/40 hover:text-error hover:bg-error/10 transition-all"
            disabled={deletingId === p.id}
            aria-label={t('productManager.deleteTitle')}
          >
            {deletingId === p.id ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-3.5 h-3.5 border-2 border-error border-t-transparent rounded-full"
              />
            ) : (
              <span className="icon-[tabler--trash] w-3.5 h-3.5" />
            )}
          </button>
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
        <button
          onClick={() => openEditModal(p)}
          className="p-1.5 rounded-md text-base-content/40 hover:text-primary"
        >
          <span className="icon-[tabler--pencil] w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => openDeleteConfirmation(p)}
          className="p-1.5 rounded-md text-base-content/40 hover:text-error"
        >
          <span className="icon-[tabler--trash] w-3.5 h-3.5" />
        </button>
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
      background="bg-linear-to-br from-slate-100 via-purple-100 to-slate-100 dark:from-slate-900 dark:via-purple-900 dark:to-slate-900"
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
            <span className="text-lg font-bold text-purple-600 dark:text-purple-400">{filteredProducts.length}</span>
          </div>
        </Card>
      </div>

      {/* ── Compact filter bar with tag-based category pills ── */}
      <div className="flex flex-col gap-3 mb-4">
        {/* Search + sort + add — single row */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1 max-w-xs">
            <span className="icon-[tabler--search] absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-base-content/50" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('productManager.searchPlaceholder') || 'Search...'}
              aria-label={t('productManager.searchPlaceholder') || 'Search products'}
              data-testid="pm-search-input"
              className="input input-bordered w-full pl-8 h-9 text-xs"
            />
            {isFiltering && (
              <div className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            )}
          </div>
          {viewMode === 'grid' && (
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
              aria-label={t('productManager.sortBy') || 'Sort by'}
              className="select select-bordered h-9 text-xs w-36"
            >
              <option value="newest">{t('productManager.sortNewest') || 'Newest'}</option>
              <option value="name-asc">A→Z</option>
              <option value="name-desc">Z→A</option>
              <option value="price-asc">$↑</option>
              <option value="price-desc">$↓</option>
            </select>
          )}
          {/* View toggle: grid vs table */}
          <button
            onClick={() => setViewMode(prev => prev === 'grid' ? 'table' : 'grid')}
            className="btn btn-ghost btn-sm btn-square text-base-content/50 hover:text-base-content"
            aria-label={viewMode === 'grid' ? 'Switch to table view' : 'Switch to grid view'}
            title={viewMode === 'grid' ? 'Table view' : 'Grid view'}
          >
            {viewMode === 'grid' ? (
              <span className="icon-[tabler--list] w-4 h-4" />
            ) : (
              <span className="icon-[tabler--grid-dots] w-4 h-4" />
            )}
          </button>
          <button
            onClick={openAddModal}
            data-testid="pm-add-button"
            className="btn btn-primary btn-sm gap-1.5 shrink-0"
          >
            <span className="icon-[tabler--plus] w-3.5 h-3.5" />
            <span className="hidden sm:inline text-xs">{t('productManager.addNewProduct')}</span>
          </button>
        </div>

        {/* Category filter as clickable tag pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`badge badge-sm cursor-pointer transition-all ${
              selectedCategory === 'all'
                ? 'badge-primary badge-soft'
                : 'badge-ghost hover:badge-soft hover:badge-primary'
            }`}
          >
            {t('productManager.allCategories') || 'All'}
          </button>
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(selectedCategory === cat.id ? 'all' : cat.id)}
              className={`badge badge-sm cursor-pointer transition-all ${
                selectedCategory === cat.id
                  ? 'badge-primary badge-soft'
                  : 'badge-ghost hover:badge-soft hover:badge-primary'
              }`}
            >
              {cat.name}
            </button>
          ))}
          {selectedCategory !== 'all' && (
            <button
              onClick={() => setSelectedCategory('all')}
              className="badge badge-sm badge-ghost text-base-content/40 hover:text-error transition-colors"
              title="Clear filter"
            >
              <span className="icon-[tabler--x] w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* ── Product Grid / Table ── */}
      {viewMode === 'grid' ? (
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="skeleton"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-9 4xl:grid-cols-10 gap-2"
            >
              {Array.from({ length: PRODUCT_SKELETON_COUNT }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))}
            </motion.div>
          ) : filteredProducts.length > 0 ? (
            <motion.div
              key="grid"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-9 4xl:grid-cols-10 gap-2"
            >
              {filteredProducts.map((product, index) => {
                const color = PRODUCT_CARD_COLORS[index % PRODUCT_CARD_COLORS.length];
                return (
                  <ProductCard
                    key={product.id}
                    product={product}
                    color={color}
                    currency={currencySymbol}
                    index={index}
                  >
                    <span className="index-pill group-hover:scale-110 transition-transform duration-200">
                      {index + 1}
                    </span>
                    <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300">
                      <button
                        onClick={(e) => { e.stopPropagation(); openEditModal(product); }}
                        className="w-7 h-7 flex items-center justify-center rounded-full
                          bg-white/90 dark:bg-slate-700/90 text-primary hover:text-primary/70
                          hover:bg-primary/10 dark:hover:bg-primary/10 transition-all active:scale-[0.9] shadow-sm"
                        aria-label={t('common.edit')}
                      >
                        <span className="icon-[tabler--edit] w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); openDeleteConfirmation(product); }}
                        className="w-7 h-7 flex items-center justify-center rounded-full
                          bg-white/90 dark:bg-slate-700/90 text-error hover:text-error/70
                          hover:bg-error/10 dark:hover:bg-error/10 transition-all active:scale-[0.9] shadow-sm disabled:opacity-50"
                        disabled={deletingId === product.id}
                        aria-label={t('productManager.deleteTitle')}
                      >
                        {deletingId === product.id ? (
                          <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                            className="w-3.5 h-3.5 border-2 border-red-400 border-t-transparent rounded-full"
                          />
                        ) : (
                          <span className="icon-[tabler--trash] w-3 h-3" />
                        )}
                      </button>
                    </div>
                  </ProductCard>
                );
              })}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            >
              <Card padding="2xl" center>
                <span className="icon-[tabler--photo] w-16 h-16 mx-auto mb-4 text-base-content/40" />
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
            </motion.div>
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
        />
      )}

      {/* Add / Edit Modal (unified) */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-base-100 rounded-xl p-4 sm:p-6 w-full max-w-md transition-colors duration-300"
            data-testid="pm-modal"
          >
            <h2 className="text-xl sm:text-2xl font-bold text-base-content mb-4 sm:mb-6">
              {modalTitle}
            </h2>

            <div className="space-y-4">
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
                      <button
                        type="button"
                        onClick={() => setProductImage(null)}
                        className="absolute -top-2 -right-2 bg-error text-error-content rounded-full p-0.5
                          hover:brightness-90 transition-all shadow-lg"
                      >
                        <span className="icon-[tabler--x] w-3 h-3" />
                      </button>
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
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full"
                        />
                      ) : (
                        <span className="icon-[tabler--photo] w-6 h-6" />
                      )}
                    </button>
                  )}
                  <p className="text-xs text-base-content/50">
                    PNG, JPG, GIF, WebP<br />Optional product photo
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-base-content mb-2">{t('productManager.productName')}</label>
                <input
                  type="text"
                  value={newProduct.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  data-testid="pm-name-input"
                  className={`input input-bordered w-full ${
                      errors.name
                        ? 'input-error'
                        : ''
                    }`}
                  placeholder={t('productManager.namePlaceholder')}
                  disabled={isSubmitting}
                />
                {errors.name && (
                  <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.name}</p>
                )}
              </div>

              {/* Product Type */}
              {!editingProduct && (
                <div>
                  <label className="block text-base-content mb-2 flex items-center gap-2">
                    <span className="icon-[tabler--tag] w-4 h-4 text-teal-500" />
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

              {/* Price + Unit in a 2-column row */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-base-content mb-1.5 text-xs font-medium">
                    <span className="icon-[tabler--currency-dollar] w-3.5 h-3.5 inline-block mr-1 text-primary/70" />
                    Price ({currencySymbol})
                  </label>
                  <input
                    type="number"
                    value={newProduct.price}
                    onChange={(e) => handleInputChange('price', e.target.value)}
                    data-testid="pm-price-input"
                    className={`input input-bordered w-full h-9 text-sm ${
                        errors.price
                          ? 'input-error'
                          : ''
                      }`}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                    disabled={isSubmitting}
                  />
                  {errors.price && (
                    <p className="text-red-500 dark:text-red-400 text-xs mt-0.5">{errors.price}</p>
                  )}
                </div>

                <div>
                  <label className="block text-base-content mb-1.5 text-xs font-medium">
                    <span className="icon-[tabler--cube] w-3.5 h-3.5 inline-block mr-1 text-primary/70" />
                    Unit
                  </label>
                  <input
                    type="text"
                    value={newProduct.unit}
                    onChange={(e) => handleInputChange('unit', e.target.value)}
                    data-testid="pm-unit-input"
                    className={`input input-bordered w-full h-9 text-sm ${
                        errors.unit
                          ? 'input-error'
                          : ''
                      }`}
                    placeholder="item, kg, pcs"
                    disabled={isSubmitting}
                  />
                  {errors.unit && (
                    <p className="text-red-500 dark:text-red-400 text-xs mt-0.5">{errors.unit}</p>
                  )}
                </div>
              </div>

              {/* Prepare time */}
              <div>
                <label className="block text-base-content mb-1.5 text-xs font-medium">
                  <span className="icon-[tabler--clock-play] w-3.5 h-3.5 inline-block mr-1 text-primary/70" />
                  Prep Time (min)
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    value={newProduct.prepare_time_minutes}
                    onChange={(e) => handleInputChange('prepare_time_minutes', Math.max(0, parseInt(e.target.value) || 0))}
                    className="input input-bordered w-24 h-9 text-sm"
                    placeholder="0"
                    min="0"
                    step="1"
                    disabled={isSubmitting}
                  />
                  <span className="text-xs text-base-content/50">Default preparation time for KDS display</span>
                </div>
              </div>

              {/* Barcode + Description */}
              <div>
                <label className="block text-base-content mb-1.5 text-xs font-medium">
                  <span className="icon-[tabler--barcode] w-3.5 h-3.5 inline-block mr-1 text-primary/70" />
                  SKU / Barcode
                </label>
                <input
                  type="text"
                  value={newProduct.barcode}
                  onChange={(e) => handleInputChange('barcode', e.target.value)}
                  className="input input-bordered w-full h-9 text-sm"
                  placeholder="e.g. 8901234567890"
                  disabled={isSubmitting}
                />
              </div>

              <div>
                <label className="block text-base-content mb-1.5 text-xs font-medium">
                  <span className="icon-[tabler--align-left] w-3.5 h-3.5 inline-block mr-1 text-primary/70" />
                  Description
                </label>
                <textarea
                  value={newProduct.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="textarea textarea-bordered w-full text-sm resize-none"
                  placeholder={t('productManager.descriptionPlaceholder') || 'Product description for menu & tickets...'}
                  rows={2}
                  disabled={isSubmitting}
                />
              </div>

              {/* Category selector */}
              {categories.length > 0 && (
                <div>
                  <label className="block text-base-content mb-1.5 text-xs font-medium">
                    <span className="icon-[tabler--folder] w-3.5 h-3.5 inline-block mr-1 text-primary/70" />
                    {t('productManager.category') || 'Category'}
                  </label>
                  <select
                    value={newProduct.category_id ? String(newProduct.category_id) : ''}
                    onChange={(e) => handleInputChange('category_id', e.target.value ? Number(e.target.value) : 0)}
                    disabled={isSubmitting}
                    className="select select-bordered w-full h-9 text-sm"
                  >
                    <option value="">{t('productManager.noCategory') || '— No category —'}</option>
                    {categories.map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex gap-4 mt-6">
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
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      />
                      {editingProduct ? t('common.updating') || 'Updating...' : t('productManager.adding')}
                    </>
                  ) : (
                    <>
                      {editingProduct ? <span className="icon-[tabler--edit]" /> : <span className="icon-[tabler--plus]" />}
                      {editingProduct ? t('common.update') : t('productManager.addProduct')}
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && productToDelete && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-base-100 rounded-xl p-6 w-full max-w-md border-2
              border-red-300 dark:border-red-500/30 transition-colors duration-300"
          >
            <div className="flex justify-center mb-4">
              <div className="bg-red-500/20 rounded-full p-4">
                <span className="icon-[tabler--alert-triangle] text-red-500 dark:text-red-400 text-4xl" />
              </div>
            </div>

            <h2 className="text-xl sm:text-2xl font-bold text-base-content text-center mb-3">
              {t('productManager.deleteTitle')}
            </h2>

            <p className="text-base-content/70 text-center mb-2">
              {t('productManager.deleteConfirm')}
            </p>
            <p className="text-base-content font-semibold text-center text-lg mb-1">
              {productToDelete.name}
            </p>
            <p className="text-base-content/50 text-center text-sm mb-6">
              {t('productManager.deleteWarning')}
            </p>

            <div className="flex gap-4">
              <button
                onClick={() => { setShowDeleteModal(false); setProductToDelete(null); }}
                className="btn btn-ghost flex-1 font-semibold"
              >
                {t('productManager.cancelDelete')}
              </button>
              <button
                onClick={handleDeleteProduct}
                className="btn btn-error flex-1 font-semibold gap-2"
              >
                <span className="icon-[tabler--trash]" />
                {t('productManager.confirmDelete')}
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Success Message */}
      {submitStatus === 'success' && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-success"
        >
          <span className="icon-[tabler--check] text-xl" />
          {statusMessage}
        </motion.div>
      )}

      {/* Error Message */}
      {submitStatus === 'error' && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 alert alert-error max-w-md"
        >
          <span className="icon-[tabler--alert-triangle] text-xl" />
          <span>{statusMessage}</span>
        </motion.div>
      )}

      {/* Keyboard Shortcut Help Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcutHelp}
        onClose={() => setShowShortcutHelp(false)}
      />
    </PageLayout>
  );
}
