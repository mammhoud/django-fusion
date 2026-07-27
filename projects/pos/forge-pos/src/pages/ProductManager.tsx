import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useMemo } from 'react';
import { FaPlus, FaTrash, FaCheck, FaExclamationTriangle, FaImage, FaTimes, FaEdit, FaSearch } from 'react-icons/fa';
import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';
import { readFile } from '@tauri-apps/plugin-fs';
import { Product, NewProduct, UpdateProductPayload, Settings, Category } from '../types';
import ProductCard, { PRODUCT_CARD_COLORS, ProductCardSkeleton, PRODUCT_SKELETON_COUNT } from '../components/ProductCard';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../components/KeyboardShortcutsModal';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

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
  const [newProduct, setNewProduct] = useState({ name: '', price: '', unit: 'item', category_id: 0 as number | 0 });
  const [borderColor, setBorderColor] = useState('#6366f1');
  const [productImage, setProductImage] = useState<string | null>(null);
  // Snapshot of the original image when editing so we don't accidentally
  // re-clear or re-write the image on every save.
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [currencySymbol, setCurrencySymbol] = useState('USD');
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

  useEffect(() => {
    const loadSettings = async () => {
      try {
        const response = await invoke<Settings>('get_settings');
        if (response?.currency) {
          setCurrencySymbol(response.currency || 'USD');
        }
      } catch (error) {
        console.error('Error loading currency:', error);
      }
    };

    loadSettings();
  }, []);

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
    setNewProduct({ name: '', price: '', unit: 'item', category_id: 0 });
    setProductImage(null);
    setBorderColor('#6366f1');
    setOriginalImage(null);
  };

  const openAddModal = () => {
    setEditingProduct(null);
    setNewProduct({ name: '', price: '', unit: 'item', category_id: 0 });
    setProductImage(null);
    setBorderColor('#6366f1');
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
    });
    setProductImage(product.image ?? null);
    setBorderColor(product.border_color || '#6366f1');
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
          border_color: borderColor || null,
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
          border_color: borderColor || null,
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

      {/* Stats Cards Row */}          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 mb-6 sm:mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card--glass rounded-xl p-4 sm:p-6 transition-colors duration-300"
        >
          <h2 className="text-lg sm:text-xl text-slate-900 dark:text-white mb-2">{t('productManager.totalProducts')}</h2>
          <p className="text-3xl sm:text-4xl font-bold text-teal-600 dark:text-teal-400">{products.length}</p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="card--glass rounded-xl p-4 sm:p-6 transition-colors duration-300"
        >
          <h2 className="text-lg sm:text-xl text-slate-900 dark:text-white mb-2">{t('productManager.filteredCount') || 'Visible'}</h2>
          <p className="text-3xl sm:text-4xl font-bold text-purple-600 dark:text-purple-400">{filteredProducts.length}</p>
        </motion.div>
      </div>

      {/* ── Filter bar (AJAX-style with debounce) ── */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="card--glass rounded-xl p-3 sm:p-4 mb-4"
      >
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('productManager.searchPlaceholder') || 'Search products...'}
              aria-label={t('productManager.searchPlaceholder') || 'Search products'}
              data-testid="pm-search-input"
              className="w-full pl-9 pr-9 py-2.5 rounded-lg bg-white/50 dark:bg-white/5
                border border-slate-300 dark:border-gray-600
                text-slate-900 dark:text-white text-sm
                placeholder:text-slate-400 dark:placeholder:text-gray-500
                focus:outline-none focus:border-teal-400 transition-colors"
            />
            {isFiltering && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                aria-label="filtering"
                className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4
                  border-2 border-teal-400 border-t-transparent rounded-full"
              />
            )}
          </div>
          <select
            value={selectedCategory === 'all' ? 'all' : String(selectedCategory)}
            onChange={(e) => setSelectedCategory(e.target.value === 'all' ? 'all' : Number(e.target.value))}
            data-testid="pm-category-filter"
            aria-label={t('productManager.categoryFilter') || 'Filter by category'}
            className="px-3 py-2.5 rounded-lg bg-white/50 dark:bg-white/5
              border border-slate-300 dark:border-gray-600
              text-slate-900 dark:text-white text-sm focus:outline-none
              focus:border-teal-400 transition-colors sm:w-48"
          >
            <option value="all">{t('productManager.allCategories') || 'All categories'}</option>
            {categories.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          <select
            value={sortKey}
            onChange={(e) => setSortKey(e.target.value as SortKey)}
            aria-label={t('productManager.sortBy') || 'Sort by'}
            className="px-3 py-2.5 rounded-lg bg-white/50 dark:bg-white/5
              border border-slate-300 dark:border-gray-600
              text-slate-900 dark:text-white text-sm focus:outline-none
              focus:border-teal-400 transition-colors sm:w-44"
          >
            <option value="newest">{t('productManager.sortNewest') || 'Newest'}</option>
            <option value="name-asc">{t('productManager.sortNameAsc') || 'Name (A→Z)'}</option>
            <option value="name-desc">{t('productManager.sortNameDesc') || 'Name (Z→A)'}</option>
            <option value="price-asc">{t('productManager.sortPriceAsc') || 'Price (low→high)'}</option>
            <option value="price-desc">{t('productManager.sortPriceDesc') || 'Price (high→low)'}</option>
          </select>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={openAddModal}
            data-testid="pm-add-button"
            className="bg-linear-to-r from-teal-400 to-teal-500 dark:from-teal-500 dark:to-teal-600
              text-white rounded-xl py-2.5 px-4 sm:px-6 flex items-center justify-center gap-2
              transition-all duration-300 shadow-lg hover:shadow-xl whitespace-nowrap"
          >
            <FaPlus /> <span>{t('productManager.addNewProduct')}</span>
          </motion.button>
        </div>
      </motion.div>

      {/* Product Grid */}
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="skeleton"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}              className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-9 4xl:grid-cols-10 gap-3 sm:gap-4"
          >
            {Array.from({ length: PRODUCT_SKELETON_COUNT }).map((_, i) => (
              <ProductCardSkeleton key={i} />
            ))}
          </motion.div>
        ) : filteredProducts.length > 0 ? (
          <motion.div
            key="grid"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-9 4xl:grid-cols-10 gap-3 sm:gap-4"
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
                  {/* Column index badge — shows the product's position in the filtered grid */}
                  <span className="index-pill group-hover:scale-110 transition-transform duration-200">
                    {index + 1}
                  </span>
                  <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-all duration-300">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={(e) => { e.stopPropagation(); openEditModal(product); }}
                      className="w-7 h-7 flex items-center justify-center rounded-full
                        bg-white/90 dark:bg-slate-700/90 text-blue-500 hover:text-blue-400
                        hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all shadow-sm"
                      aria-label={t('common.edit')}
                    >
                      <FaEdit className="w-3 h-3" />
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={(e) => { e.stopPropagation(); openDeleteConfirmation(product); }}
                      className="w-7 h-7 flex items-center justify-center rounded-full
                        bg-white/90 dark:bg-slate-700/90 text-red-400 hover:text-red-300
                        hover:bg-red-50 dark:hover:bg-red-900/30 transition-all shadow-sm disabled:opacity-50"
                      disabled={deletingId === product.id}
                      aria-label={t('productManager.deleteTitle')}
                    >
                      {deletingId === product.id ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                          className="w-3.5 h-3.5 border-2 border-red-400 border-t-transparent rounded-full"
                        />
                      ) : (
                        <FaTrash className="w-3 h-3" />
                      )}
                    </motion.button>
                  </div>
                </ProductCard>
              );
            })}
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="card--glass rounded-xl p-8 text-center"
          >
            <FaImage className="w-16 h-16 mx-auto mb-4 text-slate-400 dark:text-slate-500" />
            <p className="text-slate-600 dark:text-white/60 text-lg mb-3">
              {t('productManager.noProducts')}
            </p>
            {(searchQuery || selectedCategory !== 'all') && (
              <button
                onClick={() => { setSearchQuery(''); setSelectedCategory('all'); }}
                className="text-sm font-medium text-teal-600 dark:text-teal-400 hover:underline transition-colors"
              >
                {t('common.clear')}
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Add / Edit Modal (unified) */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-6 w-full max-w-md transition-colors duration-300"
            data-testid="pm-modal"
          >
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mb-4 sm:mb-6">
              {modalTitle}
            </h2>

            <div className="space-y-4">
              {/* Product Image */}
              <div>
                <label className="block text-slate-900 dark:text-white mb-2">{t('productManager.productImageOptional') || 'Product Image (optional)'}</label>
                <div className="flex items-center gap-3">
                  {productImage ? (
                    <div className="relative w-20 h-20 shrink-0">
                      <img
                        src={productImage}
                        alt="Product preview"
                        className="w-20 h-20 rounded-lg object-cover border-2"
                        style={{ borderColor: borderColor }}
                      />
                      <button
                        type="button"
                        onClick={() => setProductImage(null)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-0.5
                          hover:bg-red-600 transition-colors shadow-lg"
                      >
                        <FaTimes className="w-3 h-3" />
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={handlePickImage}
                      disabled={isUploadingImage}
                      className="flex flex-col items-center justify-center w-20 h-20 rounded-lg
                        bg-white/30 dark:bg-white/5 border-2 border-dashed border-slate-300 dark:border-gray-600
                        text-slate-500 dark:text-gray-400 hover:border-teal-400 hover:bg-teal-500/5
                        transition-all cursor-pointer disabled:opacity-50"
                    >
                      {isUploadingImage ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                          className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full"
                        />
                      ) : (
                        <FaImage className="w-6 h-6" />
                      )}
                    </button>
                  )}
                  <p className="text-xs text-slate-500 dark:text-gray-400">
                    PNG, JPG, GIF, WebP<br />Optional product photo
                  </p>
                </div>
              </div>

              {/* Border Color Picker — enhanced with live preview */}
              <div>
                <label className="block text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                  <span className="w-4 h-4 rounded-full border" style={{ backgroundColor: borderColor }} />
                  {t('productManager.borderColor') || 'Border Color'}
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={borderColor}
                    onChange={(e) => setBorderColor(e.target.value)}
                    className="w-12 h-10 rounded-lg cursor-pointer border-2 border-slate-300 dark:border-gray-600
                      bg-transparent p-0.5"
                    title="Choose border color for product card"
                  />
                  <input
                    type="text"
                    value={borderColor}
                    onChange={(e) => setBorderColor(e.target.value)}
                    className="flex-1 px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-700
                      text-slate-900 dark:text-white border border-slate-300 dark:border-transparent
                      focus:outline-none focus:border-teal-400 transition-colors text-sm font-mono"
                    placeholder="#6366f1"
                    pattern="^#[0-9a-fA-F]{6}$"
                  />
                  <div className="flex flex-wrap gap-1 max-w-[180px]">
                    {['#6366f1', '#ec4899', '#14b8a6', '#f59e0b', '#ef4444', '#22c55e', '#8b5cf6', '#f97316', '#06b6d4', '#84cc16'].map(c => (
                      <button
                        key={c}
                        type="button"
                        onClick={() => setBorderColor(c)}
                        className={`w-7 h-7 rounded-full border-2 transition-all hover:scale-110 ${
                          borderColor === c ? 'border-slate-900 dark:border-white scale-110 ring-2 ring-offset-1 ring-slate-400' : 'border-transparent'
                        }`}
                        style={{ backgroundColor: c }}
                        title={c}
                      />
                    ))}
                  </div>
                </div>
                {/* Live preview card */}
                <div
                  className="mt-3 rounded-xl p-3 border-2 bg-white/50 dark:bg-white/5 backdrop-blur-sm flex items-center gap-3"
                  style={{ borderColor, backgroundColor: `${borderColor}10` }}
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                    style={{ backgroundColor: borderColor }}
                  >
                    P
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                      {newProduct.name || 'Product Name'}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-gray-400">
                      {currencySymbol} {(Number(newProduct.price) || 0).toFixed(2)} / {newProduct.unit || 'item'}
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-slate-900 dark:text-white mb-2">{t('productManager.productName')}</label>
                <input
                  type="text"
                  value={newProduct.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  data-testid="pm-name-input"
                  className={`w-full px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-700
                    text-slate-900 dark:text-white border focus:outline-none transition-colors ${
                      errors.name
                        ? 'border-red-500 focus:border-red-400'
                        : 'border-slate-300 dark:border-transparent focus:border-teal-400'
                    }`}
                  placeholder={t('productManager.namePlaceholder')}
                  disabled={isSubmitting}
                />
                {errors.name && (
                  <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.name}</p>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-slate-900 dark:text-white mb-2">
                    Price ({currencySymbol} per {newProduct.unit})
                  </label>
                  <input
                    type="number"
                    value={newProduct.price}
                    onChange={(e) => handleInputChange('price', e.target.value)}
                    data-testid="pm-price-input"
                    className={`w-full px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-700
                      text-slate-900 dark:text-white border focus:outline-none transition-colors ${
                        errors.price
                          ? 'border-red-500 focus:border-red-400'
                          : 'border-slate-300 dark:border-transparent focus:border-teal-400'
                      }`}
                    placeholder={t('productManager.pricePlaceholder', { unit: newProduct.unit })}
                    step="0.01"
                    min="0"
                    disabled={isSubmitting}
                  />
                  {errors.price && (
                    <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.price}</p>
                  )}
                </div>

                <div>
                  <label className="block text-slate-900 dark:text-white mb-2">Unit</label>
                  <input
                    type="text"
                    value={newProduct.unit}
                    onChange={(e) => handleInputChange('unit', e.target.value)}
                    data-testid="pm-unit-input"
                    className={`w-full px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-700
                      text-slate-900 dark:text-white border focus:outline-none transition-colors ${
                        errors.unit
                          ? 'border-red-500 focus:border-red-400'
                          : 'border-slate-300 dark:border-transparent focus:border-teal-400'
                      }`}
                    placeholder={t('productManager.unitPlaceholder')}
                    disabled={isSubmitting}
                  />
                  {errors.unit && (
                    <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.unit}</p>
                  )}
                </div>
              </div>

              {categories.length > 0 && (
                <div>
                  <label className="block text-slate-900 dark:text-white mb-2">
                    {t('productManager.category') || 'Category'}
                  </label>
                  <select
                    value={newProduct.category_id ? String(newProduct.category_id) : ''}
                    onChange={(e) => handleInputChange('category_id', e.target.value ? Number(e.target.value) : 0)}
                    disabled={isSubmitting}
                    className="w-full px-4 py-2 rounded-lg bg-slate-100 dark:bg-slate-700
                      text-slate-900 dark:text-white border border-slate-300 dark:border-transparent
                      focus:outline-none focus:border-teal-400 transition-colors"
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
                  className="flex-1 px-4 py-2 rounded-lg bg-slate-200 dark:bg-slate-700
                    text-slate-900 dark:text-white hover:bg-slate-300 dark:hover:bg-slate-600
                    transition-colors disabled:opacity-50"
                  disabled={isSubmitting}
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleSaveProduct}
                  data-testid="pm-submit"
                  className="flex-1 px-4 py-2 rounded-lg bg-teal-500 text-white hover:bg-teal-400
                    transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
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
                      {editingProduct ? <FaEdit /> : <FaPlus />}
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
            className="bg-white dark:bg-slate-800 rounded-xl p-6 w-full max-w-md border-2
              border-red-300 dark:border-red-500/30 transition-colors duration-300"
          >
            <div className="flex justify-center mb-4">
              <div className="bg-red-500/20 rounded-full p-4">
                <FaExclamationTriangle className="text-red-500 dark:text-red-400 text-4xl" />
              </div>
            </div>

            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white text-center mb-3">
              {t('productManager.deleteTitle')}
            </h2>

            <p className="text-slate-600 dark:text-gray-300 text-center mb-2">
              {t('productManager.deleteConfirm')}
            </p>
            <p className="text-slate-900 dark:text-white font-semibold text-center text-lg mb-1">
              {productToDelete.name}
            </p>
            <p className="text-slate-500 dark:text-gray-400 text-center text-sm mb-6">
              {t('productManager.deleteWarning')}
            </p>

            <div className="flex gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => { setShowDeleteModal(false); setProductToDelete(null); }}
                className="flex-1 px-6 py-3 rounded-lg bg-slate-200 dark:bg-slate-700
                  text-slate-900 dark:text-white hover:bg-slate-300 dark:hover:bg-slate-600
                  transition-colors font-semibold"
              >
                {t('productManager.cancelDelete')}
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleDeleteProduct}
                className="flex-1 px-6 py-3 rounded-lg bg-red-500 text-white hover:bg-red-600
                  transition-colors font-semibold flex items-center justify-center gap-2"
              >
                <FaTrash />
                {t('productManager.confirmDelete')}
              </motion.button>
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
          className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-teal-500 text-white px-6 py-3
            rounded-xl flex items-center gap-2 z-50"
        >
          <FaCheck className="text-xl" />
          {statusMessage}
        </motion.div>
      )}

      {/* Error Message */}
      {submitStatus === 'error' && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-red-500 text-white px-6 py-3
            rounded-xl flex items-center gap-2 max-w-md z-50"
        >
          <FaExclamationTriangle className="text-xl" />
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
