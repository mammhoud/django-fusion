import { motion } from 'framer-motion';
import { useState, useEffect, useRef, useMemo } from 'react';
import { MdShoppingCart, MdCheckCircle, MdLocalPrintshop, MdFileDownload, MdSearch, MdClose } from 'react-icons/md';
import { FaPlus, FaStore, FaTruck, FaHandPaper, FaUserTie, FaDoorOpen, FaMapMarkerAlt, FaFileInvoiceDollar } from 'react-icons/fa';
import { invoke } from '@tauri-apps/api/core';
import { save } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';
import { Product, Settings, CartItem, NewSaleData, NewSaleItemData, DeliveryType, Employee } from '../types';
import Receipt from '../components/Receipt';
import { InvoiceType } from '../types';
import { downloadInvoicePDF } from '../utils/invoicePdf';
import ProductCard, { PRODUCT_CARD_COLORS, ProductCardSkeleton, PRODUCT_SKELETON_COUNT } from '../components/ProductCard';
import jsPDF from 'jspdf';
import PageLayout from '../components/PageLayout';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../components/KeyboardShortcutsModal';
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';
import { useStatusToast } from '../hooks/useStatusToast';
import StatusToast from '../components/StatusToast';

type OrderType = 'dine-in' | 'takeaway' | 'delivery';

const ORDER_TYPES: { key: OrderType; label: string; icon: React.ReactNode }[] = [
  { key: 'dine-in', label: 'Dine-in', icon: <FaStore /> },
  { key: 'takeaway', label: 'Takeaway', icon: <FaHandPaper /> },
  { key: 'delivery', label: 'Delivery', icon: <FaTruck /> },
];

export default function Sale() {
  const { t } = useTranslation();
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showSuccessDialog, setShowSuccessDialog] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [receiptData, setReceiptData] = useState<{
    products: { name: string; quantity: number; unit: string; price: number }[];
    totalAmount: number;
    date: string;
    time: string;
    receiptNumber: string;
    orderType: string;
    tableNumber?: number | null;
    deliveryTypeName?: string;
    deliveryAddress?: string;
    employeeName?: string;
  } | null>(null);
  const receiptRef = useRef<HTMLDivElement>(null);
  const [settings, setSettings] = useState<Settings>({
    restaurant_name: 'POS',
    address: '',
    phone: '',
    currency: 'USD',
    receipt_footer: 'Thank you for your business!',
  });
  const [deliveryTypes, setDeliveryTypes] = useState<DeliveryType[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSelling, setIsSelling] = useState(false);
  const [isDownloadingPDF, setIsDownloadingPDF] = useState(false);
  const [isPrinting, setIsPrinting] = useState(false);
  const [showPDFSuccessDialog, setShowPDFSuccessDialog] = useState(false);
  const [savedPDFPath, setSavedPDFPath] = useState('');
  const [invoiceType, setInvoiceType] = useState<InvoiceType>('tax');
  const [isInvoiceDownloading, setIsInvoiceDownloading] = useState(false);
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);
  // AJAX-style debounced search: 250 ms idle window with isSearching flag for
  // the spinner. Shared hook — see src/hooks/useDebouncedSearch.ts.
  // We rename-destructure so the rest of this file keeps using the original
  // variable names (`searchQuery`, `debouncedSearchQuery`, `isSearching`).
  const {
    query: searchQuery,
    setQuery: setSearchQuery,
    debouncedQuery: debouncedSearchQuery,
    isPending: isSearching,
  } = useDebouncedSearch();
  const [selectedCategory, setSelectedCategory] = useState<number | 'all'>('all');
  const [categories, setCategories] = useState<{ id: number; name: string }[]>([]);

  // Status toast — errors during load, sale, print, or PDF generation must
  // surface to the user (the existing alert() calls block the main thread but
  // get swallowed by jsdom in tests, so this hook is the canonical path).
  const { status, showError, dismiss } = useStatusToast();

  // ---- Keyboard Shortcuts ----
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

      if (showSuccessDialog) return;

      // Order type
      if (key === '1') { setOrderType('dine-in'); return; }
      if (key === '2') { setOrderType('takeaway'); return; }
      if (key === '3') { setOrderType('delivery'); return; }

      // Clear cart
      if (key === 'Escape') {
        if (cart.length > 0 && confirm('Clear cart?')) {
          setCart([]);
        }
        return;
      }

      // Complete sale (Enter) — only when cart has items
      if (key === 'Enter' && cart.length > 0 && !isSelling) {
        handleSellRef.current();
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [cart.length, showSuccessDialog, isSelling]);

  // Order details
  const [orderType, setOrderType] = useState<OrderType>('dine-in');
  const [tableNumber, setTableNumber] = useState<number>(1);
  const [deliveryTypeId, setDeliveryTypeId] = useState<number>(0);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [employeeId, setEmployeeId] = useState<number>(0);

  const loadData = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [productsRes, settingsRes, dtRes, empRes, categoriesRes] = await Promise.all([
        invoke<Product[]>('get_products'),
        invoke<Settings>('get_settings'),
        invoke<DeliveryType[]>('get_delivery_types', { includeInactive: false }),
        invoke<Employee[]>('get_employees', { includeInactive: false }),
        invoke<{ id: number; name: string }[]>('get_categories'),
      ]);

      setProducts(productsRes);
      if (settingsRes) {
        setSettings({
          restaurant_name: settingsRes.restaurant_name || 'POS',
          address: settingsRes.address || '',
          phone: settingsRes.phone || '',
          currency: settingsRes.currency || 'USD',
          receipt_footer: settingsRes.receipt_footer || 'Thank you for your business!',
        });
      }
      setDeliveryTypes(dtRes);
      setEmployees(empRes);
      setCategories(categoriesRes || []);
      if (dtRes.length > 0) setDeliveryTypeId(dtRes[0].id);
    } catch (error) {
      console.error('Error loading sale data:', error);
      // Even quiet reloads must fail loudly — silent reloads hide backend drift.
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // loadData is referentially stable (it's defined inside the component
    // without reactive captures); listing it as a dep would only re-run on
    // every render. Empty deps here intentionally mirror the established
    // mount-once pattern from other POS pages.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addToCart = (product: Product) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.unit === 'item' || item.unit === 'items' ? item.quantity + 1 : item.quantity + 0.5 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const updateQuantity = (productId: number, quantity: number, unit: string) => {
    if (quantity < (unit === 'item' || unit === 'items' ? 1 : 0.5)) {
      setCart(prev => prev.filter(item => item.id !== productId));
      return;
    }
    setCart(prev =>
      prev.map(item =>
        item.id === productId ? { ...item, quantity } : item
      )
    );
  };

  const handleSell = async () => {
    if (cart.length === 0) {
      showError(t('sale.pleaseSelectProduct'));
      return;
    }

    try {
      setIsSelling(true);

      const now = new Date();
      const saleData: NewSaleData = {
        total_amount: totalAmount + (orderType === 'delivery' ? deliveryFee : 0),
        currency: settings.currency || 'USD',
        date: now.toISOString().split('T')[0],
        time: now.toTimeString().split(' ')[0],
        order_type: orderType,
        status: 'completed',
        table_number: orderType === 'dine-in' ? tableNumber : null,
        delivery_type_id: orderType === 'delivery' ? deliveryTypeId : null,
        delivery_address: orderType === 'delivery' ? deliveryAddress || null : null,
        employee_id: employeeId > 0 ? employeeId : null,
      };

      const itemsData: NewSaleItemData[] = cart.map(item => ({
        product_name: item.name,
        price: item.price,
        quantity: item.quantity,
        unit: item.unit,
      }));

      await invoke('add_sale', { sale: saleData, items: itemsData });

      // Generate receipt data
      const deliveryTypeName = orderType === 'delivery'
        ? deliveryTypes.find(dt => dt.id === deliveryTypeId)?.name
        : undefined;
      const employeeName = employeeId > 0
        ? employees.find(e => e.id === employeeId)?.name
        : undefined;

      setReceiptData({
        products: cart.map(item => ({
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          price: item.price * item.quantity,
        })),
        totalAmount,
        date: now.toLocaleDateString(),
        time: now.toLocaleTimeString(),
        receiptNumber: Math.random().toString(36).substr(2, 9).toUpperCase(),
        orderType,
        tableNumber: orderType === 'dine-in' ? tableNumber : null,
        deliveryTypeName,
        deliveryAddress: orderType === 'delivery' ? deliveryAddress : undefined,
        employeeName,
      });

      setShowSuccessDialog(true);
      // Quiet reload keeps prices/settings in sync with backend drift since the
      // user started this sale — but the success dialog already covers UX feedback.
      loadData({ quiet: true });
    } catch (error) {
      console.error('Error saving sale:', error);
      showError(`${t('sale.errorCompleteSale')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsSelling(false);
    }
  }
  const handleSellRef = useRef(handleSell);
  handleSellRef.current = handleSell;

  const handleNewSale = () => {
    setCart([]);
    setShowSuccessDialog(false);
    setReceiptData(null);
    setOrderType('dine-in');
    setTableNumber(1);
    setDeliveryTypeId(deliveryTypes.length > 0 ? deliveryTypes[0].id : 0);
    setDeliveryAddress('');
    setEmployeeId(0);
  };

  const handlePrint = () => {
    setIsPrinting(true);
    setTimeout(() => {
      try {
        window.print();
      } catch (error) {
        console.error('Print error:', error);
        showError(`${t('transactions.printError')}: ${error instanceof Error ? error.message : String(error)}`);
      } finally {
        setIsPrinting(false);
      }
    }, 500);
  };

  const handleDownloadInvoice = async () => {
    if (!receiptData) return;
    setIsInvoiceDownloading(true);
    try {
      await downloadInvoicePDF({
        invoiceType,
        invoiceNumber: `INV-${receiptData.receiptNumber}`,
        date: receiptData.date,
        from: {
          name: settings.restaurant_name || 'POS',
          address: settings.address,
          phone: settings.phone,
          email: settings.email,
          logo: settings.logo,
        },
        to: {
          name: 'Walk-in Customer',
        },
        items: receiptData.products.map(item => ({
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          price: item.price / item.quantity,
        })),
        currency: settings.currency || 'USD',
        taxRate: settings.tax_rate ? parseFloat(settings.tax_rate) : 0,
        notes: settings.receipt_footer,
      });
    } catch (error) {
      console.error('Error generating invoice PDF:', error);
      showError(`${t('sale.errorGeneratePDF')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsInvoiceDownloading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!receiptData) {
      showError(t('transactions.receiptReady'));
      return;
    }

    setIsDownloadingPDF(true);

    try {
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: [80, 297],
      });

      let yPos = 10;
      const pageWidth = 80;
      const margin = 5;
      const contentWidth = pageWidth - margin * 2;

      // Header
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      const restaurantName = settings.restaurant_name || 'POS';
      pdf.text(restaurantName, pageWidth / 2, yPos, { align: 'center' });
      yPos += 7;

      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      if (settings.address) {
        pdf.text(settings.address, pageWidth / 2, yPos, { align: 'center' });
        yPos += 5;
      }
      if (settings.phone) {
        pdf.text(`Tel: ${settings.phone}`, pageWidth / 2, yPos, { align: 'center' });
        yPos += 5;
      }

      pdf.text(`Date: ${receiptData.date}  Time: ${receiptData.time}`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 4;
      pdf.text(`Receipt #: ${receiptData.receiptNumber}`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 4;
      pdf.text(`Order: ${receiptData.orderType}`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 4;
      if (receiptData.tableNumber) {
        pdf.text(`Table: ${receiptData.tableNumber}`, pageWidth / 2, yPos, { align: 'center' });
        yPos += 4;
      }
      if (receiptData.deliveryTypeName) {
        pdf.text(`Delivery: ${receiptData.deliveryTypeName}`, pageWidth / 2, yPos, { align: 'center' });
        yPos += 4;
      }
      if (receiptData.deliveryAddress) {
        const addrLines = pdf.splitTextToSize(`Address: ${receiptData.deliveryAddress}`, contentWidth);
        pdf.text(addrLines, pageWidth / 2, yPos, { align: 'center' });
        yPos += addrLines.length * 4;
      }
      if (receiptData.employeeName) {
        pdf.text(`Server: ${receiptData.employeeName}`, pageWidth / 2, yPos, { align: 'center' });
        yPos += 4;
      }
      yPos += 2;

      // Separator
      pdf.setDrawColor(0);
      pdf.setLineWidth(0.3);
      for (let i = 0; i < contentWidth; i += 2) {
        pdf.line(margin + i, yPos, margin + i + 1, yPos);
      }
      yPos += 5;

      // Items Header
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Item', margin, yPos);
      pdf.text('Qty', pageWidth / 2, yPos, { align: 'center' });
      pdf.text('Price', pageWidth - margin, yPos, { align: 'right' });
      yPos += 5;

      pdf.setFont('helvetica', 'normal');
      receiptData.products.forEach(product => {
        const itemName = product.name.length > 18 ? product.name.substring(0, 18) + '...' : product.name;
        pdf.text(itemName, margin, yPos);
        pdf.text(`${product.quantity} ${product.unit}`, pageWidth / 2, yPos, { align: 'center' });
        pdf.text(`${settings.currency} ${product.price.toFixed(2)}`, pageWidth - margin, yPos, { align: 'right' });
        yPos += 5;
      });

      yPos += 1;
      for (let i = 0; i < contentWidth; i += 2) {
        pdf.line(margin + i, yPos, margin + i + 1, yPos);
      }
      yPos += 5;

      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Total', margin, yPos);
      pdf.text(`${settings.currency} ${receiptData.totalAmount.toFixed(2)}`, pageWidth - margin, yPos, { align: 'right' });
      yPos += 8;

      if (settings.receipt_footer) {
        for (let i = 0; i < contentWidth; i += 2) {
          pdf.line(margin + i, yPos, margin + i + 1, yPos);
        }
        yPos += 5;
        pdf.setFontSize(9);
        pdf.setFont('helvetica', 'normal');
        const footerLines = pdf.splitTextToSize(settings.receipt_footer, contentWidth);
        pdf.text(footerLines, pageWidth / 2, yPos, { align: 'center' });
      }

      const pdfBlob = pdf.output('arraybuffer');
      const pdfArray = new Uint8Array(pdfBlob);

      const defaultFilename = `receipt-${receiptData.receiptNumber}.pdf`;
      const filePath = await save({
        defaultPath: defaultFilename,
        filters: [{ name: 'PDF', extensions: ['pdf'] }],
      });

      if (filePath) {
        await writeFile(filePath, pdfArray);
        setSavedPDFPath(filePath);
        setShowPDFSuccessDialog(true);
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      showError(`${t('sale.errorGeneratePDF')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloadingPDF(false);
    }
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  // Calculate estimated delivery fee
  const deliveryFee = orderType === 'delivery' && settings.delivery_fee ? settings.delivery_fee : 0;

  // Filter products by search query and category
  const filteredProducts = useMemo(() => {
    let result = products;
    const query = debouncedSearchQuery.trim().toLowerCase();
    if (query) {
      result = result.filter(product => product.name.toLowerCase().includes(query));
    }
    if (selectedCategory !== 'all') {
      result = result.filter(product => product.category_id === selectedCategory);
    }
    return result;
  }, [products, debouncedSearchQuery, selectedCategory]);

  // Whether any filter is currently applied — drives counter visibility & aria-hidden.
  // Keyed off debouncedSearchQuery so the count is in sync with the actual grid (the
  // previous version keyed off searchQuery and showed a stale number during the
  // 250ms debounce window).
  const filterActive = debouncedSearchQuery.trim() !== '' || selectedCategory !== 'all';

  return (        <PageLayout title={t('sale.title')} background="bg-slate-100 dark:bg-slate-900">
      <div>
          {/* Order Type Selector */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card--glass rounded-xl p-4 mb-4"
          >
            <div className="flex items-center gap-2 mb-3">
              <MdShoppingCart className="text-teal-500" />
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white">{t('sale.orderType')}</h2>
            </div>
            <div className="grid grid-cols-3 gap-3">
              {ORDER_TYPES.map(ot => (
                <motion.button
                  key={ot.key}
                  whileHover={{ scale: isLoading ? 1 : 1.02 }}
                  whileTap={{ scale: isLoading ? 1 : 0.98 }}
                  onClick={() => setOrderType(ot.key)}
                  disabled={isLoading}
                  className={`flex flex-col items-center gap-1.5 p-3 rounded-xl font-medium text-sm transition-all ${
                    isLoading
                      ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'
                      : orderType === ot.key
                        ? 'bg-teal-500 text-white shadow-lg'
                        : 'bg-white/50 dark:bg-white/5 text-slate-700 dark:text-gray-300 hover:bg-teal-100 dark:hover:bg-teal-800/30'
                  }`}
                >
                  <span className="text-lg">{ot.icon}</span>
                  <span>{ot.key === 'dine-in' ? t('sale.dineIn') : t('sale.' + ot.key)}</span>
                </motion.button>
              ))}
            </div>

            {/* Conditional Fields */}
            {orderType === 'dine-in' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-300 dark:border-white/10"
              >
                <FaDoorOpen className="text-slate-400" />
                <label className="text-sm text-slate-700 dark:text-gray-300">{t('sale.table')}</label>
                <select
                  value={tableNumber}
                  onChange={e => setTableNumber(Number(e.target.value))}
                  disabled={isLoading}
                  className="px-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                    text-slate-900 dark:text-white text-sm flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {Array.from({ length: settings.dine_in_tables || 15 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>{t('sale.tableOption', { number: i + 1 })}</option>
                  ))}
                </select>
              </motion.div>
            )}

            {orderType === 'delivery' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-3 mt-3 pt-3 border-t border-slate-300 dark:border-white/10"
              >
                <div className="flex items-center gap-3">
                  <FaTruck className="text-slate-400" />
                  <label className="text-sm text-slate-700 dark:text-gray-300">{t('sale.deliveryType')}</label>
                  <select
                    value={deliveryTypeId}
                    onChange={e => setDeliveryTypeId(Number(e.target.value))}
                    disabled={isLoading}
                    className="px-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                      text-slate-900 dark:text-white text-sm flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {deliveryTypes.map(dt => (
                      <option key={dt.id} value={dt.id}>
                        {dt.name} {dt.fee_multiplier > 1 ? `(${dt.fee_multiplier}x fee)` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center gap-3">
                  <FaMapMarkerAlt className="text-slate-400" />
                  <input
                    type="text"
                    value={deliveryAddress}
                    onChange={e => setDeliveryAddress(e.target.value)}
                    placeholder={t('sale.deliveryAddress')}
                    disabled={isLoading}
                    className="px-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                      text-slate-900 dark:text-white text-sm flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                </div>
                {settings.delivery_fee && settings.delivery_fee > 0 && (
                  <p className="text-xs text-slate-500 dark:text-gray-400 ml-8">
                    Delivery fee: {settings.currency} {settings.delivery_fee.toFixed(2)}
                    {settings.delivery_fee_per_km ? ` + ${settings.delivery_fee_per_km.toFixed(2)}/km` : ''}
                  </p>
                )}
              </motion.div>
            )}
          </motion.div>

          {/* Employee Assignment */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="card--glass rounded-xl p-4 mb-4"
          >
            <div className="flex items-center gap-3">
              <FaUserTie className="text-slate-400" />
              <label className="text-sm text-slate-700 dark:text-gray-300">{t('sale.assignTo')}</label>
              <select
                value={employeeId}
                onChange={e => setEmployeeId(Number(e.target.value))}
                disabled={isLoading}
                className="px-3 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                  text-slate-900 dark:text-white text-sm flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <option value={0}>{t('sale.noAssignment')}</option>
                {employees.map(emp => (
                  <option key={emp.id} value={emp.id}>{emp.name}</option>
                ))}
              </select>
            </div>
          </motion.div>

          {/* Total Amount Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card--glass rounded-xl p-4 sm:p-6 mb-6 sm:mb-8
              transition-colors duration-300"
          >
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-lg sm:text-xl text-slate-900 dark:text-white mb-1">{t('sale.totalAmount')}</h2>
                <p className={`text-3xl sm:text-4xl font-bold ${isLoading ? 'text-slate-400 dark:text-slate-500 animate-pulse' : 'text-teal-600 dark:text-teal-400'}`}>
                  {isLoading ? '—' : `${settings.currency} ${(totalAmount + deliveryFee).toFixed(2)}`}
                </p>
                {deliveryFee > 0 && (
                  <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">
                    ({settings.currency} {totalAmount.toFixed(2)} + {settings.currency} {deliveryFee.toFixed(2)} delivery)
                  </p>
                )}
              </div>
              <div className="text-slate-600 dark:text-white/60">
                {t('sale.itemsSelected', { count: cart.length })}
              </div>
            </div>
          </motion.div>

          {/* Product Search & Category Filter */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="card--glass rounded-xl p-3 sm:p-4 mb-4"
          >
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <MdSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder={t('sale.searchProducts')}
                  aria-label={t('sale.searchProducts')}
                  disabled={isLoading}
                  className="w-full pl-10 pr-10 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                    text-slate-900 dark:text-white text-sm placeholder:text-slate-400 dark:placeholder:text-gray-500
                    focus:outline-none focus:border-teal-400 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                />
                {isSearching ? (
                  <motion.div
                    aria-label="searching"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4
                      border-2 border-teal-400 border-t-transparent rounded-full pointer-events-none"
                  />
                ) : searchQuery ? (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors"
                    aria-label={t('common.clear')}
                  >
                    <MdClose className="w-4 h-4" />
                  </button>
                ) : null}
              </div>
              <select
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value === 'all' ? 'all' : Number(e.target.value))}
                disabled={isLoading || categories.length === 0}
                aria-label={t('sale.categoryFilter')}
                className="px-3 py-2.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                  text-slate-900 dark:text-white text-sm focus:outline-none focus:border-teal-400 transition-colors
                  disabled:opacity-60 disabled:cursor-not-allowed sm:w-48"
              >
                <option value="all">{t('sale.allCategories')}</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </select>
            </div>
            {/* Result counter — always rendered; faded to opacity 0 when no filter active so the
                card height never jumps and the slot never shows blank whitespace. aria-hidden
                mirrors visibility so screen readers ignore the stale count while it's hidden. */}
            <div className="mt-2 min-h-[1.25rem] flex items-center justify-end">
              <motion.span
                animate={{ opacity: filterActive ? 1 : 0 }}
                transition={{ duration: 0.15 }}
                aria-hidden={!filterActive}
                className="text-xs text-slate-500 dark:text-gray-400 tabular-nums"
              >
                {filteredProducts.length} / {products.length}
              </motion.span>
            </div>
          </motion.div>

          {/* Products Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-7 gap-3 sm:gap-4 mb-6 sm:mb-8">
            {isLoading ? (
              Array.from({ length: PRODUCT_SKELETON_COUNT }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))
            ) : filteredProducts.length > 0 ? (
              filteredProducts.map((product, index) => {
              const cartItem = cart.find(item => item.id === product.id);
              const color = PRODUCT_CARD_COLORS[index % PRODUCT_CARD_COLORS.length];
              return (
                <ProductCard
                  key={product.id}
                  product={product}
                  color={color}
                  currency={settings.currency}
                  isSelected={!!cartItem}
                  index={index}
                >
                  {/* Add Button */}
                  {!cartItem && (
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => addToCart(product)}
                      className={`${color.badge} text-white p-1.5 sm:p-2 rounded-lg hover:brightness-110 transition-all shrink-0 shadow-sm mt-1`}
                      aria-label={t('sale.addToCart', { product: product.name })}
                    >
                      <FaPlus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    </motion.button>
                  )}

                  {cartItem && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center justify-between bg-white/50 dark:bg-white/10 rounded-lg p-1.5 sm:p-2 backdrop-blur-sm w-full mt-1"
                    >
                      <button
                        onClick={() =>
                          updateQuantity(
                            product.id,
                            (cartItem.quantity || 0) - (product.unit === 'item' || product.unit === 'items' ? 1 : 0.5),
                            product.unit
                          )
                        }
                        className="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center text-white bg-red-400 dark:bg-red-500/20
                          hover:bg-red-500 rounded-lg transition-colors text-sm sm:text-base"
                        aria-label={t('sale.decreaseQuantity')}
                      >
                        -
                      </button>
                      <div className="flex flex-col items-center min-w-0 px-1">
                        <span className="text-slate-900 dark:text-white font-medium text-sm sm:text-base">
                          {cartItem.quantity}
                        </span>
                        <span className="text-slate-600 dark:text-white/60 text-[10px] sm:text-xs">
                          {settings.currency} {(cartItem.quantity * product.price).toFixed(2)}
                        </span>
                      </div>
                      <button
                        onClick={() =>
                          updateQuantity(
                            product.id,
                            (cartItem.quantity || 0) + (product.unit === 'item' || product.unit === 'items' ? 1 : 0.5),
                            product.unit
                          )
                        }
                        className="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center text-white bg-teal-400 dark:bg-teal-500/20
                          hover:bg-teal-500 rounded-lg transition-colors text-sm sm:text-base"
                        aria-label={t('sale.increaseQuantity')}
                      >
                        +
                      </button>
                    </motion.div>
                  )}
                </ProductCard>
              );
            })
            ) : (
              <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
                <MdSearch className="w-12 h-12 text-slate-400 dark:text-slate-500 mb-4" />
                <p className="text-slate-600 dark:text-white/70 text-lg mb-2">
                  {t('sale.noProductsMatch')}
                </p>
                <button
                  onClick={() => setSearchQuery('')}
                  className="text-sm font-medium text-teal-600 dark:text-teal-400 hover:underline transition-colors"
                >
                  {t('common.clear')}
                </button>
              </div>
            )}
          </div>

          {/* Cart Summary */}
          {cart.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card--glass rounded-xl p-4 mb-6 transition-colors duration-300"
            >
              <h3 className="text-slate-900 dark:text-white font-semibold mb-3">{t('sale.cartSummary')}</h3>
              <div className="space-y-2">
                {cart.map(item => (
                  <div key={item.id} className="flex justify-between items-center text-slate-700 dark:text-white/80">
                    <span>
                      {item.name} × {item.quantity} {item.unit === 'item' ? 'item(s)' : item.unit}
                    </span>
                    <span>{settings.currency} {(item.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
                <div className="border-t border-slate-300 dark:border-white/10 pt-2 mt-2 flex justify-between items-center">
                  <span className="text-slate-900 dark:text-white font-semibold">{t('sale.subtotal')}</span>
                  <span className="text-slate-900 dark:text-white font-semibold">
                    {settings.currency} {totalAmount.toFixed(2)}
                  </span>
                </div>
                {deliveryFee > 0 && (
                  <div className="flex justify-between items-center text-slate-600 dark:text-gray-400 text-sm">
                    <span>{t('sale.deliveryFee')}</span>
                    <span>{settings.currency} {deliveryFee.toFixed(2)}</span>
                  </div>
                )}
                <div className="border-t border-slate-300 dark:border-white/10 pt-2 mt-2 flex justify-between items-center">
                  <span className="text-slate-900 dark:text-white font-bold">{t('sale.total')}</span>
                  <span className="text-teal-600 dark:text-teal-400 font-bold">
                    {settings.currency} {(totalAmount + deliveryFee).toFixed(2)}
                  </span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Sell Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSell}
            disabled={cart.length === 0 || isSelling || isLoading}
            className={`w-full py-4 rounded-xl flex items-center justify-center gap-3 text-white font-semibold
              transition-all duration-300 shadow-lg hover:shadow-xl ${
                cart.length === 0 || isSelling || isLoading
                  ? 'bg-gray-500/50 cursor-not-allowed'
                  : 'bg-teal-500'
              }`}
          >
            {isSelling ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                />
                <span>{t('sale.processing')}</span>
              </>
            ) : (
              <>
                <MdShoppingCart className="text-xl" />
                {t('sale.completeSale')}
              </>
            )}
          </motion.button>
      </div>

      {/* Success Dialog */}
      {showSuccessDialog && receiptData && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-md w-full my-8 transition-colors duration-300"
          >
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="mx-auto mb-4"
              >
                <MdCheckCircle className="w-16 h-16 text-teal-500 mx-auto" />
              </motion.div>

              <motion.h3
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-2xl font-bold text-slate-900 dark:text-white mb-6"
              >
                {t('sale.saleComplete')}
              </motion.h3>

              {/* Order Details Badge */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="flex flex-wrap justify-center gap-2 mb-4"
              >
                <span className="px-3 py-1 bg-teal-100 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400 rounded-full text-xs font-medium">
                  {receiptData.orderType.charAt(0).toUpperCase() + receiptData.orderType.slice(1)}
                </span>
                {receiptData.tableNumber && (
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full text-xs font-medium">
                    Table {receiptData.tableNumber}
                  </span>
                )}
                {receiptData.deliveryTypeName && (
                  <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 rounded-full text-xs font-medium">
                    {receiptData.deliveryTypeName}
                  </span>
                )}
                {receiptData.employeeName && (
                  <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-full text-xs font-medium">
                    {receiptData.employeeName}
                  </span>
                )}
              </motion.div>

              {/* Receipt Preview */}
              <div className="mb-6">
                <Receipt
                  ref={receiptRef}
                  products={receiptData.products}
                  totalAmount={receiptData.totalAmount}
                  date={receiptData.date}
                  time={receiptData.time}
                  settings={settings}
                  receiptNumber={receiptData.receiptNumber}
                />
              </div>

              {/* Invoice Type Selector */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 dark:text-gray-300 mb-1.5">
                  {t('invoice.typeLabel')}
                </label>
                <select
                  value={invoiceType}
                  onChange={(e) => setInvoiceType(e.target.value as InvoiceType)}
                  className="w-full px-3 py-2 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 dark:border-gray-600
                    text-slate-900 dark:text-white text-sm focus:outline-none focus:border-teal-400"
                >
                  <option value="tax">{t('invoice.typeTax')}</option>
                  <option value="commercial">{t('invoice.typeCommercial')}</option>
                  <option value="proforma">{t('invoice.typeProforma')}</option>
                  <option value="credit">{t('invoice.typeCredit')}</option>
                  <option value="receipt">{t('invoice.typeReceipt')}</option>
                </select>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleDownloadPDF}
                  disabled={isDownloadingPDF}
                  className={`py-3 px-4 text-white rounded-xl font-semibold
                    transition-all duration-300 flex items-center justify-center gap-2 ${
                      isDownloadingPDF ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-500'
                    }`}
                >
                  {isDownloadingPDF ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      />
                      <span>{t('sale.saving')}</span>
                    </>
                  ) : (
                    <>
                      <MdFileDownload className="text-xl" />
                      {t('sale.pdf')}
                    </>
                  )}
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handlePrint}
                  disabled={isPrinting}
                  className={`py-3 px-4 text-white rounded-xl font-semibold
                    transition-all duration-300 flex items-center justify-center gap-2 ${
                      isPrinting ? 'bg-purple-300 cursor-not-allowed' : 'bg-purple-500'
                    }`}
                >
                  {isPrinting ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      />
                      <span>{t('sale.printing')}</span>
                    </>
                  ) : (
                    <>
                      <MdLocalPrintshop className="text-xl" />
                      {t('sale.print')}
                    </>
                  )}
                </motion.button>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleDownloadInvoice}
                disabled={isInvoiceDownloading}
                className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-semibold 
                  transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mb-4"
              >
                {isInvoiceDownloading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  />
                ) : (
                  <>
                    <FaFileInvoiceDollar className="text-xl" />
                    {t('invoice.downloadInvoice')}
                  </>
                )}
              </motion.button>

              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleNewSale}
                className="w-full py-3 px-4 bg-teal-500 text-white rounded-xl font-semibold
                  transition-all duration-300 flex items-center justify-center gap-2"
              >
                <MdShoppingCart className="text-xl" />
                {t('sale.startNewSale')}
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}

      {/* PDF Success Dialog */}
      {showPDFSuccessDialog && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={() => setShowPDFSuccessDialog(false)}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-md w-full transition-colors duration-300"
            onClick={e => e.stopPropagation()}
          >
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="mx-auto mb-4"
              >
                <MdCheckCircle className="w-16 h-16 text-green-500 mx-auto" />
              </motion.div>

              <motion.h3
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-2xl font-bold text-slate-900 dark:text-white mb-2"
              >
                {t('sale.pdfSaved')}
              </motion.h3>

              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-slate-600 dark:text-slate-300 mb-6 break-all text-sm"
              >
                {savedPDFPath}
              </motion.p>

              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowPDFSuccessDialog(false)}
                className="w-full py-3 px-4 bg-green-500 text-white rounded-xl font-semibold
                  transition-all duration-300 hover:bg-green-600"
              >
                {t('common.close')}
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}

      <KeyboardShortcutsModal isOpen={showShortcutHelp} onClose={() => setShowShortcutHelp(false)} />

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}
