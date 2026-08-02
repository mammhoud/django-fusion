import { useState, useEffect, useRef, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { save } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';
import { Product, Settings, CartItem, NewSaleData, NewSaleItemData, DeliveryType, Employee, DeliveryZone, Note, Category } from '../../types';
import Receipt from '../../components/pos/Receipt';
import { InvoiceType } from '../../types';
import { downloadInvoicePDF } from '../../utils/invoicePdf';
import ProductCard, { PRODUCT_CARD_COLORS, productAccentColor, ProductCardSkeleton, PRODUCT_SKELETON_COUNT } from '../../components/pos/ProductCard';
import ProductFilterBar from '../../components/shared/ProductFilterBar';
import Card from '../../components/ui/Card';
import jsPDF from 'jspdf';
import PageLayout from '../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import { useStatusToast } from '../../hooks/useStatusToast';
import { useCurrency } from '../../contexts/CurrencyContext';
import StatusToast from '../../components/ui/StatusToast';
import { iconClass } from '../../lib/icons';

type OrderType = 'dine-in' | 'takeaway' | 'delivery' | 'extra-order' | 'dated-order';

type SortKey = 'newest' | 'name-asc' | 'name-desc' | 'price-asc' | 'price-desc';

const ORDER_TYPES: { key: OrderType; label: string; icon: React.ReactNode }[] = [
  { key: 'dine-in', label: 'Dine-in', icon: <span className={iconClass('lucide:utensils', '')} /> },
  { key: 'takeaway', label: 'Takeaway', icon: <span className={iconClass('lucide:package', '')} /> },
  { key: 'delivery', label: 'Delivery', icon: <span className={iconClass('lucide:truck', '')} /> },
  { key: 'extra-order', label: 'Extra Order', icon: <span className={iconClass('lucide:plus', '')} /> },
  { key: 'dated-order', label: 'Dated Order', icon: <span className={iconClass('lucide:calendar-clock', '')} /> },
];

export default function Sale() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
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
    deliveryFee?: number;
    deliveryZoneName?: string;
    deliveryDistance?: number;
    employeeName?: string;
  } | null>(null);
  const receiptRef = useRef<HTMLDivElement>(null);
  const [settings, setSettings] = useState<Settings>({
    restaurant_name: 'Forge POS',
    address: '',
    phone: '',
    currency: 'USD',
    receipt_footer: 'Thank you for your business!',
  });
  const [deliveryTypes, setDeliveryTypes] = useState<DeliveryType[]>([]);
  const [deliveryZones, setDeliveryZones] = useState<DeliveryZone[]>([]);
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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarHovered, setSidebarHovered] = useState(false);
  // ── Live-update indicator — briefly pulses green when product-updated event fires ──
  const [showLiveBadge, setShowLiveBadge] = useState(false);
  const liveBadgeTimer = useRef<ReturnType<typeof setTimeout>>(undefined);
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
  const [categories, setCategories] = useState<Category[]>([]);

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
  const [selectedZoneId, setSelectedZoneId] = useState<number>(0);
  const [deliveryDistance, setDeliveryDistance] = useState<number>(0);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [employeeId, setEmployeeId] = useState<number>(0);
  const [orderNotes, setOrderNotes] = useState('');
  const [viewMode, setViewMode] = useState<'standard' | 'compact'>('standard');
  const [productTypeFilter, setProductTypeFilter] = useState<string>('all');
  const [sortKey, setSortKey] = useState<SortKey>('newest');
  const [itemNotes, setItemNotes] = useState<Record<number, string>>({});
  // Receipt template notes
  const [templateNotes, setTemplateNotes] = useState<Note[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number>(0);
  // Quick-selectable notes (quick-add into order notes)
  const [selectableNotes, setSelectableNotes] = useState<Note[]>([]);
  const [showQuickNoteForm, setShowQuickNoteForm] = useState(false);
  const [quickNoteText, setQuickNoteText] = useState('');

  const loadData = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [productsRes, settingsRes, dtRes, zonesRes, empRes, categoriesRes, notesRes, selectableRes] = await Promise.all([
        invoke<Product[]>('get_products'),
        invoke<Settings>('get_settings'),
        invoke<DeliveryType[]>('get_delivery_types', { includeInactive: false }),
        invoke<DeliveryZone[]>('get_delivery_zones', { includeInactive: true }),
        invoke<Employee[]>('get_employees', { includeInactive: false }),
        invoke<Category[]>('get_categories'),
        invoke<Note[]>('get_notes'),
        invoke<Note[]>('get_selectable_notes'),
      ]);

      setProducts(productsRes);
      setTemplateNotes((notesRes || []).filter(n => n.use_as_template || n.category === 'receipt'));
      setSelectableNotes(selectableRes || []);
      if (settingsRes) {
        setSettings({
          restaurant_name: settingsRes.restaurant_name || 'Forge POS',
          address: settingsRes.address || '',
          phone: settingsRes.phone || '',
          currency: settingsRes.currency || 'USD',
          receipt_footer: settingsRes.receipt_footer || 'Thank you for your business!',
          unique_card_colors: settingsRes.unique_card_colors !== false,
        });
      }
      setDeliveryTypes(dtRes);
      setDeliveryZones(zonesRes);
      setEmployees(empRes);
      setCategories(categoriesRes || []);
      if (dtRes.length > 0) setDeliveryTypeId(dtRes[0].id);
      const activeZones = zonesRes.filter(z => z.is_active);
      if (activeZones.length > 0 && selectedZoneId === 0) {
        setSelectedZoneId(activeZones[0].id);
      }
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

  // ── Real-time product updates from other windows ──
  useEffect(() => {
    const unlisten = listen('product-updated', () => {
      loadData({ quiet: true });
      setShowLiveBadge(true);
      clearTimeout(liveBadgeTimer.current);
      liveBadgeTimer.current = setTimeout(() => setShowLiveBadge(false), 2000);
    });
    return () => {
      unlisten.then(fn => fn());
      clearTimeout(liveBadgeTimer.current);
    };
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
      setItemNotes(prev => { const n = { ...prev }; delete n[productId]; return n; });
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
        delivery_zone_id: orderType === 'delivery' && selectedZoneId > 0 ? selectedZoneId : null,
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
        deliveryFee: deliveryFee > 0 ? deliveryFee : undefined,
        deliveryZoneName: selectedZone?.name,
        deliveryDistance: orderType === 'delivery' ? deliveryDistance : undefined,
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
    setSelectedZoneId(0);
    setDeliveryDistance(0);      setDeliveryAddress('');
    setEmployeeId(0);
    setOrderNotes('');
    setItemNotes({});
    setSelectedTemplateId(0);
  };

  /*** Append a selectable note's body to the order notes ***/
  const appendQuickNote = (note: Note) => {
    const block = note.template_body && note.template_body.trim() ? note.template_body.trim() : note.name;
    setOrderNotes(prev => (prev ? `${prev}\n\n[${note.name}] ${block}` : `[${note.name}] ${block}`));
  };

  /*** Quick-create a new selectable note and append it to the order notes ***/
  const handleQuickAddNote = async () => {
    const text = quickNoteText.trim();
    if (!text) return;
    try {
      const note = await invoke<Note>('add_note', {
        template: {
          name: text.split('\n')[0].slice(0, 60),
          template_body: text,
          category: 'general',
          use_as_template: false,
          selectable: true,
          steps: null,
        },
      });
      setSelectableNotes(prev => [...prev, note]);
      appendQuickNote(note);
      setQuickNoteText('');
      setShowQuickNoteForm(false);
    } catch (error) {
      console.error('Error adding quick note:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
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
          name: settings.restaurant_name || 'Forge POS',
          address: settings.address,
          phone: settings.phone,
          email: settings.email,
          taxId: settings.tax_id ?? undefined,
          logo: settings.invoice_logo ?? undefined,
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
        notes: [orderNotes.trim(), effectiveReceiptFooter.trim()].filter(Boolean).join('\n\n') || undefined,
        orderType: receiptData.orderType,
        deliveryFee: receiptData.deliveryFee,
        deliveryTypeName: receiptData.deliveryTypeName,
        deliveryZoneName: receiptData.deliveryZoneName,
        deliveryDistance: receiptData.deliveryDistance,
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
      const restaurantName = settings.restaurant_name || 'Forge POS';
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

      // Order Notes (from the sale screen) — printed above the receipt footer
      if (orderNotes.trim()) {
        for (let i = 0; i < contentWidth; i += 2) {
          pdf.line(margin + i, yPos, margin + i + 1, yPos);
        }
        yPos += 5;
        pdf.setFontSize(9);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Notes', pageWidth / 2, yPos, { align: 'center' });
        yPos += 4;
        pdf.setFont('helvetica', 'normal');
        const orderNoteLines = pdf.splitTextToSize(orderNotes.trim(), contentWidth);
        pdf.text(orderNoteLines, pageWidth / 2, yPos, { align: 'center' });
        yPos += orderNoteLines.length * 4 + 2;
        pdf.setFontSize(9);
      }

      if (effectiveReceiptFooter) {
                for (let i = 0; i < contentWidth; i += 2) {
                  pdf.line(margin + i, yPos, margin + i + 1, yPos);
                }
                yPos += 5;
                pdf.setFontSize(9);
                pdf.setFont('helvetica', 'normal');
                const footerLines = pdf.splitTextToSize(effectiveReceiptFooter, contentWidth);
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

  // Compute effective receipt footer: settings footer + optional template note body
  const effectiveReceiptFooter = useMemo(() => {
    const base = settings.receipt_footer || '';
    if (selectedTemplateId > 0) {
      const template = templateNotes.find(n => n.id === selectedTemplateId);
      if (template && template.template_body) {
        return base ? `${base}\n\n${template.template_body}` : template.template_body;
      }
    }
    return base;
  }, [settings.receipt_footer, selectedTemplateId, templateNotes]);

  // Calculate estimated delivery fee using zone formula: base_fee + (km * fee_per_km)
  // Show warning and cap fee when distance exceeds the zone's max_distance.
  const selectedZone = deliveryZones.find(z => z.id === selectedZoneId);
  const exceedsMaxDistance = !!(selectedZone && deliveryDistance > selectedZone.max_distance);
  const effectiveDistance = exceedsMaxDistance ? selectedZone!.max_distance : deliveryDistance;
  const deliveryFee = orderType === 'delivery' && selectedZone
    ? selectedZone.base_fee + (effectiveDistance * selectedZone.fee_per_km)
    : orderType === 'delivery' && settings.delivery_fee
      ? settings.delivery_fee + (deliveryDistance * (settings.delivery_fee_per_km || 0))
      : 0;

  // Per-category product counts → displayed as small badges on the filter pills
  const categoryCounts = useMemo(() => {
    const map: Record<number, number> = {};
    products.forEach(p => {
      if (p.category_id != null) map[p.category_id] = (map[p.category_id] || 0) + 1;
    });
    return map;
  }, [products]);

  // Filter products by search query, category, product type, and the selected
  // order type (products with a restricted `available_order_types` list are
  // hidden from order types they don't belong to), then sort.
  const filteredProducts = useMemo(() => {
    let result = products;
    const query = debouncedSearchQuery.trim().toLowerCase();
    if (query) {
      result = result.filter(product => product.name.toLowerCase().includes(query));
    }
    if (selectedCategory !== 'all') {
      result = result.filter(product => product.category_id === selectedCategory);
    }
    if (productTypeFilter !== 'all') {
      result = result.filter(product => (product.product_type || 'product') === productTypeFilter);
    }
    // Order-type availability: '' = available everywhere; otherwise the
    // comma-separated list must include the currently selected order type.
    result = result.filter(product => {
      const available = (product.available_order_types || '').trim();
      if (!available) return true;
      return available.split(',').map(s => s.trim()).includes(orderType);
    });
    const sorted = [...result].sort((a, b) => {
      switch (sortKey) {
        case 'name-asc': return a.name.localeCompare(b.name);
        case 'name-desc': return b.name.localeCompare(a.name);
        case 'price-asc': return (a.price ?? 0) - (b.price ?? 0);
        case 'price-desc': return (b.price ?? 0) - (a.price ?? 0);
        default: return (b.id ?? 0) - (a.id ?? 0); // newest
      }
    });
    return sorted;
  }, [products, debouncedSearchQuery, selectedCategory, productTypeFilter, sortKey, orderType]);

  // Whether any filter is currently applied — drives counter visibility & aria-hidden.
  // Keyed off debouncedSearchQuery so the count is in sync with the actual grid (the
  // previous version keyed off searchQuery and showed a stale number during the
  // 250ms debounce window).
  const filterActive = debouncedSearchQuery.trim() !== '' || selectedCategory !== 'all';

  return (        <PageLayout title={t('sale.title')}>
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-6 max-w-full overflow-x-hidden">{/* ── Sidebar Toggle Button (desktop only) ── */}
        <div          className="hidden lg:flex items-start pt-1 -mr-2 z-20">
          <button
            onClick={() => { setSidebarOpen(o => !o); setSidebarHovered(false); }}
            className="sticky top-24 p-2 rounded-xl bg-base-100/60 backdrop-blur-sm
              border border-base-300/50 shadow-sm hover:shadow-md
              text-base-content/50 hover:text-primary dark:hover:text-primary/80
              transition-all duration-300 z-10 active:scale-[0.92]"
            aria-label={sidebarOpen ? 'Hide order panel' : 'Show order panel'}
          >
            {sidebarOpen ? <span className={iconClass('lucide:chevron-right', 'w-5 h-5')} /> : <span className={iconClass('lucide:chevron-left', 'w-5 h-5')} />}
          </button>
        </div>

        {/* ── Main Content (products + cart) ── */}
        <div className="flex-1 min-w-0 pb-20 lg:pb-0">{/* Order Type Selector — visible on mobile only */}
          <div className="lg:hidden">
              <Card className="mb-4">
              <div className="flex items-center gap-2 mb-3">
                <span className={iconClass('lucide:shopping-cart', 'text-primary')} />
                <h2 className="text-sm font-semibold text-base-content">{t('sale.orderType')}</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {ORDER_TYPES.map(ot => (
                  <button
                    key={ot.key}
                    onClick={() => setOrderType(ot.key)}
                    disabled={isLoading}
                    className={`flex-1 basis-[calc(33.333%-0.375rem)] min-w-[6rem] flex flex-col items-center gap-1 p-2 rounded-lg font-medium text-xs transition-all active:scale-[0.98] ${
                      isLoading
                        ? 'bg-slate-200 dark:bg-slate-700 text-base-content/40 cursor-not-allowed'
                        : orderType === ot.key
                          ? 'bg-primary text-white shadow-md'
                          : 'bg-base-100/50 text-base-content/80 hover:bg-primary/10 dark:hover:bg-primary/20'
                    }`}
                  >
                    <span className="text-base">{ot.icon}</span>
                    <span className="text-xs">{ot.key === 'dine-in' ? t('sale.dineIn') : t('sale.' + ot.key)}</span>
                  </button>
                ))}
              </div>
              {/* Dine-in: Table + Employee side by side */}
              {orderType === 'dine-in' && (
                <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-base-300/50">
                  <div className="flex flex-col gap-1 min-w-0">
                    <label className="text-xs text-base-content/80">{t('sale.table')}</label>
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span className={iconClass('lucide:door-open', 'text-base-content/50 shrink-0')} />
                      <select
                        value={tableNumber}
                        onChange={e => setTableNumber(Number(e.target.value))}
                        disabled={isLoading}
                        className="select flex-1 min-w-0 disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        {Array.from({ length: settings.dine_in_tables || 15 }, (_, i) => (
                          <option key={i + 1} value={i + 1}>{t('sale.tableOption', { number: i + 1 })}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="flex flex-col gap-1 min-w-0">
                    <label className="text-xs text-base-content/80">{t('sale.assignTo')}</label>
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span className={iconClass('lucide:user-check', 'text-base-content/50 shrink-0')} />
                      <select
                        value={employeeId}
                        onChange={e => setEmployeeId(Number(e.target.value))}
                        disabled={isLoading}
                        className="select flex-1 min-w-0 disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        <option value={0}>{t('sale.noAssignment')}</option>
                        {employees.map(emp => (<option key={emp.id} value={emp.id}>{emp.name}</option>))}
                      </select>
                    </div>
                  </div>
                </div>
              )}
              {orderType === 'delivery' && (
                <div
                  className="space-y-3 mt-3 pt-3 border-t border-base-300/50"
                >
                  {/* Delivery Type + Zone — side by side */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className={iconClass('lucide:truck', 'text-base-content/50 shrink-0')} />
                      <label className="text-sm text-base-content/80 shrink-0">{t('sale.deliveryType')}</label>
                      <select
                        value={deliveryTypeId}
                        onChange={e => setDeliveryTypeId(Number(e.target.value))}
                        disabled={isLoading}
                        className="select flex-1 min-w-0 disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        {deliveryTypes.map(dt => (
                          <option key={dt.id} value={dt.id}>{dt.name} {dt.fee_multiplier > 1 ? `(${dt.fee_multiplier}x fee)` : ''}</option>
                        ))}
                      </select>
                    </div>
                    {/* Delivery Zone selector */}
                    {deliveryZones.length > 0 && (
                      <div className="flex items-center gap-2 min-w-0">
                        <span className={iconClass('lucide:map-pin', 'text-base-content/50 shrink-0')} />
                        <label className="text-sm text-base-content/80 shrink-0">{t('sale.zone')}</label>
                        <select
                          value={selectedZoneId}
                          onChange={e => setSelectedZoneId(Number(e.target.value))}
                          disabled={isLoading}
                          className="select flex-1 min-w-0 disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                          {deliveryZones.filter(z => z.is_active).map(z => (
                            <option key={z.id} value={z.id}>{z.name} ({z.base_fee.toFixed(2)} + {z.fee_per_km.toFixed(2)}/km)</option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>
                  {/* Distance input */}
                  <div className="flex items-center gap-3">
                    <span className={iconClass('lucide:ruler', 'text-base-content/50')} />
                    <label className="text-sm text-base-content/80">{t('sale.distance')}</label>
                    <div className="flex items-center gap-1 flex-1">
                      <input type="number" value={deliveryDistance} onChange={e => setDeliveryDistance(Math.max(0, Number(e.target.value)))}
                        placeholder="0" min="0" step="0.5" disabled={isLoading}
                        className="input w-full disabled:opacity-60 disabled:cursor-not-allowed" />
                      <span className="text-xs text-base-content/50">km</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={iconClass('lucide:map-pin', 'text-base-content/50')} />
                    <input type="text" value={deliveryAddress} onChange={e => setDeliveryAddress(e.target.value)}
                      placeholder={t('sale.deliveryAddress')} disabled={isLoading}
                      className="select flex-1 disabled:opacity-60 disabled:cursor-not-allowed" />
                  </div>
                  {selectedZone && deliveryFee > 0 && (
                    <div className="ml-8">
                      {exceedsMaxDistance ? (
                        <>
                          <p className="text-xs text-warning dark:text-warning/80 font-medium">
                            <span className={iconClass('lucide:alert-triangle', 'w-3.5 h-3.5 inline-block mr-1')} />
                            Distance exceeds {selectedZone.name} max ({selectedZone.max_distance} km) — fee capped at max distance
                          </p>
                          <p className="text-xs text-base-content/50 mt-0.5">
                            Fee: {formatPrice(selectedZone.base_fee)} + {selectedZone.max_distance}km × {formatPrice(selectedZone.fee_per_km)} = <span className="font-semibold text-primary dark:text-primary/80">{formatPrice(deliveryFee)}</span>
                            <span className="line-through text-slate-400 ml-2">({settings.currency} {(selectedZone.base_fee + (deliveryDistance * selectedZone.fee_per_km)).toFixed(2)})</span>
                          </p>
                        </>
                      ) : (
                        <p className="text-xs text-base-content/50">
                          Fee: {formatPrice(selectedZone.base_fee)} + {deliveryDistance}km × {formatPrice(selectedZone.fee_per_km)} = <span className="font-semibold text-primary dark:text-primary/80">{formatPrice(deliveryFee)}</span>
                        </p>
                      )}
                    </div>
                  )}
                  {!selectedZone && deliveryFee > 0 && (
                    <p className="text-xs text-base-content/50 ml-8">
                      Delivery fee: {formatPrice(deliveryFee)}
                    </p>
                  )}
                </div>
              )}
            </Card>

            {/* Employee Assignment — mobile (inline with Table when dine-in; standalone otherwise) */}
            {orderType !== 'dine-in' && (
              <div className="mb-4">
              <div className="flex items-center gap-3">
                <span className={iconClass('lucide:user-check', 'text-base-content/50')} />
                <label className="text-sm text-base-content/80">{t('sale.assignTo')}</label>
                <select value={employeeId} onChange={e => setEmployeeId(Number(e.target.value))} disabled={isLoading}
                  className="select flex-1 disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  <option value={0}>{t('sale.noAssignment')}</option>
                  {employees.map(emp => (<option key={emp.id} value={emp.id}>{emp.name}</option>))}
                </select>
              </div>
              </div>
            )}

            {/* Total Amount Card — mobile (centered, enhanced) */}
              <Card transitional className="sm:p-6 mb-6 sm:mb-8 overflow-hidden">
              <div className="relative flex flex-col items-center text-center gap-1.5 py-1">
                <h2 className="text-sm uppercase tracking-wider text-base-content/60 flex items-center gap-1.5">
                  <span className={iconClass('lucide:wallet', 'w-4 h-4 text-primary')} />
                  {t('sale.totalAmount')}
                </h2>
                <p className={`text-4xl sm:text-5xl font-extrabold tracking-tight ${isLoading ? 'text-base-content/40 animate-pulse' : 'text-primary dark:text-primary/80'}`}>
                  {isLoading ? '—' : `${settings.currency} ${(totalAmount + deliveryFee).toFixed(2)}`}
                </p>
                {deliveryFee > 0 && (
                  <p className="text-xs text-base-content/50">
                    ({formatPrice(totalAmount)} + {formatPrice(deliveryFee)} delivery)
                  </p>
                )}
                <span className="badge badge-soft badge-primary gap-1.5 mt-0.5">
                  <span className={iconClass('lucide:shopping-bag', 'w-3.5 h-3.5')} />
                  {t('sale.itemsSelected', { count: cart.length })}
                </span>
              </div>
            </Card>
           </div>

          {/* ── Compact rounded search + filter + sort bar — shared ProductFilterBar ──
              Same component used on ProductManager; see docs/shared-components.md. */}
          <ProductFilterBar
            searchValue={searchQuery}
            onSearchChange={setSearchQuery}
            searchPlaceholder={t('sale.searchProducts')}
            searchAriaLabel={t('sale.searchProducts')}
            searchTestId="sale-search-input"
            searchLoading={isSearching}
            searchDisabled={isLoading}
            topRowActions={
              <>
                {/* Product type + sort — grouped together so the two selects sit side by side */}
                <div className="flex items-center gap-2">
                  <div className="field field--sm">
                    <select
                      value={productTypeFilter}
                      onChange={e => setProductTypeFilter(e.target.value)}
                      className="select"
                      aria-label={t('sale.productTypeLabel') || 'Product type'}
                    >
                      <option value="all">{t('sale.allTypes') || 'All Types'}</option>
                      <option value="product">{t('sale.typeProduct') || 'Products'}</option>
                      <option value="combo">{t('sale.typeCombo') || 'Combos'}</option>
                      <option value="addon">{t('sale.typeAddon') || 'Add-ons'}</option>
                    </select>
                  </div>
                  <div className="field field--sm">
                    <select
                      value={sortKey}
                      onChange={e => setSortKey(e.target.value as SortKey)}
                      className="select"
                      aria-label={t('sale.sortBy') || 'Sort by'}
                    >
                      <option value="newest">{t('sale.sortNewest') || 'Newest'}</option>
                      <option value="name-asc">A→Z</option>
                      <option value="name-desc">Z→A</option>
                      <option value="price-asc">$↑</option>
                      <option value="price-desc">$↓</option>
                    </select>
                  </div>
                </div>

                {/* Live-update indicator badge */}
                <span
                  className={`w-2 h-2 rounded-full shrink-0 transition-all duration-300 ${
                    showLiveBadge
                      ? 'bg-success scale-125 opacity-100 animate-pulse'
                      : 'bg-success/20 scale-100 opacity-0'
                  }`}
                  title={showLiveBadge ? 'Products updated live' : undefined}
                  aria-hidden={!showLiveBadge}
                />

                {/* View mode toggle — rounded segmented control */}
                <div className="flex items-center gap-1 bg-base-200/50 rounded-full p-0.5 shrink-0">
                  <button
                    type="button"
                    onClick={() => setViewMode('standard')}
                    className={`p-1.5 rounded-full transition-all ${
                      viewMode === 'standard'
                        ? 'bg-base-100 shadow-sm text-primary'
                        : 'text-base-content/40 hover:text-base-content'
                    }`}
                    title="Standard view"
                  >
                    <span className={iconClass('lucide:layout-grid', 'w-4 h-4')} />
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewMode('compact')}
                    className={`p-1.5 rounded-full transition-all ${
                      viewMode === 'compact'
                        ? 'bg-base-100 shadow-sm text-primary'
                        : 'text-base-content/40 hover:text-base-content'
                    }`}
                    title="Compact view"
                  >
                    <span className={iconClass('lucide:layout-list', 'w-4 h-4')} />
                  </button>
                </div>
              </>
            }
            categories={categories}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            categoryAllLabel={t('sale.allCategories')}
            categoryAriaLabel={t('sale.categoryFilter')}
            categoryTestIdPrefix="sale-category-filter"
            categoryCounts={categoryCounts}
            showLegend
            legendLabel={t('sale.categoryLegend')}
            categoryTooltipFormatter={(cat, count) =>
              count !== undefined
                ? `${cat.name} — ${t('sale.categoryCount', { count })}`
                : cat.name
            }
            footer={
              /* Result counter — always rendered; faded to opacity 0 when no filter active so the
                 card height never jumps and the slot never shows blank whitespace. aria-hidden
                 mirrors visibility so screen readers ignore the stale count while it's hidden. */
              <div className="min-h-[1.25rem] flex items-center justify-end">
                <span
                  aria-hidden={!filterActive}
                  className="text-xs text-base-content/50 tabular-nums transition-opacity duration-150"
                >
                  {filteredProducts.length} / {products.length}
                </span>
              </div>
            }
          />

          {/* Products Grid */}
          <div className={`gap-3 sm:gap-4 mb-6 sm:mb-8 grid ${viewMode === 'compact'
              ? 'grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 xl:grid-cols-8 2xl:grid-cols-10 3xl:grid-cols-12'
              : 'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8 3xl:grid-cols-10 4xl:grid-cols-12'
          }`}>
            {isLoading ? (
              Array.from({ length: PRODUCT_SKELETON_COUNT }).map((_, i) => (
                <ProductCardSkeleton key={i} />
              ))
            ) : filteredProducts.length > 0 ? (
              filteredProducts.map((product, index) => {
              const cartItem = cart.find(item => item.id === product.id);
              const color = PRODUCT_CARD_COLORS[index % PRODUCT_CARD_COLORS.length];
              // Unique per-product accent: category color wins when the product
              // has one; otherwise a deterministic golden-angle hue derived from
              // the product id/name so adjacent cards never repeat the same
              // palette color (the rotating 7-color cycle used to repeat).
              const categoryColor = product.category_id != null
                ? (categories.find(c => c.id === product.category_id)?.color || null)
                : null;
              // Unique per-product accents are user-toggleable via Settings.
              // When off, only explicit category colors apply and cards fall
              // back to the rotating palette (pre-feature behavior).
              const accentColor = settings.unique_card_colors !== false
                ? (categoryColor ?? productAccentColor(product))
                : categoryColor;
              return (
                <ProductCard
                  key={product.id}
                  product={product}
                  color={color}
                  categoryColor={accentColor}
                  currency={settings.currency}
                  isSelected={!!cartItem}
                  index={index}
                  showActions={false}
                >
                  {/* Full-width Add Button */}
                  {!cartItem ? (
                    <button
                      onClick={() => addToCart(product)}
                      className={`w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-[10px] sm:text-[11px] font-semibold text-white
                        hover:brightness-110 transition-all active:scale-[0.95] shadow-sm mt-1 group-hover:shadow-md ${color.badge}`}
                      style={accentColor ? { backgroundColor: accentColor } : undefined}
                      aria-label={t('sale.addToCartLabel', { product: product.name })}
                    >
                      <span className="icon-[tabler--plus] w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      {t('sale.addToCartLabel', { product: product.name })}
                    </button>
                  ) : (
                    <div
                      className="flex items-center justify-between bg-white/50 dark:bg-white/10 rounded-lg p-1.5 sm:p-2 backdrop-blur-sm w-full mt-1 shadow-sm"
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
                          hover:bg-red-500 rounded-lg transition-all active:scale-90 text-sm sm:text-base"
                        aria-label={t('sale.decreaseQuantity')}
                      >
                        -
                      </button>
                      <div className="flex flex-col items-center min-w-0 px-1">
                        <span className="text-base-content font-medium text-sm sm:text-base">
                          {cartItem.quantity}
                        </span>
                        <span className="text-base-content/60 text-[10px] sm:text-xs">
                          {formatPrice(cartItem.quantity * product.price)}
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
                        className="w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center text-white bg-primary/90 hover:bg-primary
                          rounded-lg transition-all active:scale-90 text-sm sm:text-base"
                        aria-label={t('sale.increaseQuantity')}
                      >
                        +
                      </button>
                    </div>
                  )}
                </ProductCard>
              );
            })
            ) : (
              <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
                <span className={iconClass('lucide:search', 'w-12 h-12 text-base-content/40 mb-4')} />
                <p className="text-base-content/70 text-lg mb-2">
                  {t('sale.noProductsMatch')}
                </p>
                <button
                  onClick={() => setSearchQuery('')}
                  className="text-sm font-medium text-primary dark:text-primary/80 hover:underline transition-colors"
                >
                  {t('common.clear')}
                </button>
              </div>
            )}
          </div>

          {/* Cart Summary */}
          {cart.length > 0 && (
              <Card transitional className="mb-6">
              <h3 className="text-base-content font-semibold mb-3 flex items-center gap-2">
                <span className={iconClass('lucide:shopping-cart', 'text-primary w-4 h-4')} />
                {t('sale.cartSummary')}
              </h3>
              <div className="space-y-2">
                {cart.map(item => {
                  const note = itemNotes[item.id] || '';
                  return (
                    <div key={item.id} className="flex flex-col">
                      <div className="flex justify-between items-center text-slate-700 dark:text-white/80">
                        <span>
                          {item.name} × {item.quantity} {item.unit === 'item' ? 'item(s)' : item.unit}
                        </span>
                        <span>{formatPrice(item.price * item.quantity)}</span>
                      </div>
                      {/* Item notes customization */}
                      <div className="flex items-center gap-2 mt-0.5">
                        <input
                          type="text"
                          value={note}
                          onChange={e => setItemNotes(prev => ({ ...prev, [item.id]: e.target.value }))}
                          placeholder={t('sale.addNote') || 'Add note...'}
                          className="text-[11px] bg-transparent border-0 border-b border-dashed border-base-300/50
                            text-base-content/50 placeholder:text-base-content/20
                            focus:outline-none focus:border-primary/50 w-full py-0.5"
                        />
                        {note && (
                          <button
                            onClick={() => setItemNotes(prev => { const n = { ...prev }; delete n[item.id]; return n; })}
                            className="text-base-content/30 hover:text-error transition-colors shrink-0"
                          >
                            <span className={iconClass('lucide:x', 'w-3 h-3')} />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
                <div className="border-t border-base-300/50 pt-2 mt-2 flex justify-between items-center">
                  <span className="text-base-content font-semibold">{t('sale.subtotal')}</span>
                  <span className="text-base-content font-semibold">
                    {formatPrice(totalAmount)}
                  </span>
                </div>
                {deliveryFee > 0 && (
                  <div className="flex justify-between items-center text-slate-600 dark:text-gray-400 text-sm">
                    <span>{t('sale.deliveryFee')}</span>
                    <span>{formatPrice(deliveryFee)}</span>
                  </div>
                )}
                <div className="border-t border-base-300/50 pt-2 mt-2 flex justify-between items-center">
                  <span className="text-base-content font-bold">{t('sale.total')}</span>
                  <span className="text-primary dark:text-primary/80 font-bold">
                    {formatPrice(totalAmount + deliveryFee)}
                  </span>
                </div>
              </div>
            </Card>
          )}

          {/* Sell Button — desktop only (mobile uses sticky bar below) */}
          <div className="hidden lg:block">
            <button
              onClick={handleSell}
              disabled={cart.length === 0 || isSelling || isLoading}
              className={`w-full py-4 rounded-xl flex items-center justify-center gap-3 text-white font-semibold
                transition-all duration-300 shadow-lg hover:shadow-xl btn btn-block ${
                  cart.length === 0 || isSelling || isLoading
                    ? 'btn-disabled bg-gray-500/50 cursor-not-allowed'
                    : 'bg-primary btn-primary'
                }`}
            >
              {isSelling ? (
                <>
                  <div
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
                  />
                  <span>{t('sale.processing')}</span>
                </>
              ) : (
                <>
                  <span className={iconClass('lucide:shopping-cart', 'text-xl')} />
                  {t('sale.completeSale')}
                </>
              )}
            </button>
          </div>
        </div>{/* end main-content */}

        {/* ── Sticky Mobile Checkout Bar ── */}
        <div
          initial={false}
          animate={cart.length > 0 ? { y: 0 } : { y: 120 }}
          className="fixed bottom-0 left-0 right-0 lg:hidden z-40 pointer-events-none"
        >
          <div className="pointer-events-auto bg-base-100/95 backdrop-blur-xl
            border-t border-slate-200 dark:border-slate-700
            px-4 py-3 pb-[env(safe-area-inset-bottom,0.75rem)]
            shadow-2xl shadow-black/10 dark:shadow-black/40">
            <div className="flex items-center justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-xs text-base-content/50">
                  {t('sale.itemsSelected', { count: cart.length })}
                </p>
                <p className="text-lg font-bold text-primary dark:text-primary/80">
                  {formatPrice(totalAmount + deliveryFee)}
                </p>
                {deliveryFee > 0 && (
                  <p className="text-[10px] text-slate-400 dark:text-gray-500">
                    {t('sale.deliveryFee')}: {formatPrice(deliveryFee)}
                  </p>
                )}
              </div>
              <button
                onClick={handleSell}
                disabled={cart.length === 0 || isSelling || isLoading}
                className="shrink-0 px-5 py-2.5 rounded-xl bg-primary text-white font-semibold
                  flex items-center gap-2 shadow-lg shadow-teal-500/30 dark:shadow-teal-500/20
                  transition-all duration-200 active:scale-95
                  disabled:bg-gray-400 disabled:shadow-none disabled:cursor-not-allowed"
              >
                {isSelling ? (
                  <>
                    <div
                      className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                    />
                    <span className="text-sm">{t('sale.processing')}</span>
                  </>
                ) : (
                  <>
                    <span className={iconClass('lucide:shopping-cart', 'text-lg')} />
                    <span className="text-sm">{t('sale.completeSale')}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* ── Desktop Sidebar — Order Details Panel ── */}
        <div
          onMouseEnter={() => { if (!sidebarOpen) setSidebarHovered(true); }}
          onMouseLeave={() => setSidebarHovered(false)}
          className="hidden lg:block relative"
        >
          <div
            initial={false}
            animate={{
              width: (sidebarOpen || sidebarHovered) ? 280 : 0,
              opacity: (sidebarOpen || sidebarHovered) ? 1 : 0,
            }}
            transition={{ type: 'spring', stiffness: 300, damping: 28 }}
            className="sticky top-24 overflow-hidden"
          >
            <div className="w-[280px] space-y-4">
              {/* Order Type Card */}
                <Card>
                <div className="flex items-center gap-2 mb-3">
                  <span className={iconClass('lucide:sliders-horizontal', 'text-primary')} />
                  <h2 className="text-sm font-semibold text-base-content">{t('sale.orderType')}</h2>
                </div>
                <div className="flex flex-col gap-1.5">
                  {ORDER_TYPES.map(ot => (
                    <button
                      key={ot.key}
                      onClick={() => setOrderType(ot.key)}
                      disabled={isLoading}
                      className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg font-medium text-xs transition-all active:scale-[0.98] ${
                        isLoading
                          ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                          : orderType === ot.key
                            ? 'bg-primary text-white shadow-md shadow-teal-500/20'
                            : 'bg-base-100/50 text-base-content/80 hover:bg-primary/10'
                      }`}
                    >
                      <span className={`text-base ${orderType === ot.key ? '' : 'text-primary dark:text-primary/80'}`}>{ot.icon}</span>
                      <span className="truncate">{ot.key === 'dine-in' ? t('sale.dineIn') : t('sale.' + ot.key)}</span>
                      {orderType === ot.key && (
                        <span className={iconClass('lucide:circle-check', 'ml-auto w-3.5 h-3.5')} />
                      )}
                    </button>
                  ))}
                </div>

                {/* Dine-in: Table + Employee side by side */}
                {orderType === 'dine-in' && (
                  <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-base-300/30">
                    <div className="flex flex-col gap-1 min-w-0">
                      <label className="text-[11px] text-base-content/60">{t('sale.table')}</label>
                      <div className="flex items-center gap-1.5 min-w-0">
                        <span className={iconClass('lucide:door-open', 'text-base-content/50 text-sm shrink-0')} />
                        <select value={tableNumber} onChange={e => setTableNumber(Number(e.target.value))} disabled={isLoading}
                          className="select flex-1 min-w-0 text-xs"
                        >
                          {Array.from({ length: settings.dine_in_tables || 15 }, (_, i) => (
                            <option key={i + 1} value={i + 1}>{t('sale.tableOption', { number: i + 1 })}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className="flex flex-col gap-1 min-w-0">
                      <label className="text-[11px] text-base-content/60">{t('sale.assignTo')}</label>
                      <div className="flex items-center gap-1.5 min-w-0">
                        <span className={iconClass('lucide:user-check', 'text-base-content/50 text-sm shrink-0')} />
                        <select value={employeeId} onChange={e => setEmployeeId(Number(e.target.value))} disabled={isLoading}
                          className="select flex-1 min-w-0 text-xs"
                        >
                          <option value={0}>{t('sale.noAssignment')}</option>
                          {employees.map(emp => (<option key={emp.id} value={emp.id}>{emp.name}</option>))}
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Delivery: Type + Zone side by side + Address */}
                {orderType === 'delivery' && (
                  <div
                    className="space-y-2 mt-3 pt-3 border-t border-base-300/30"
                  >
                    <div className="grid grid-cols-2 gap-2">
                      <div className="flex items-center gap-1.5 min-w-0">
                        <span className={iconClass('lucide:truck', 'text-base-content/50 text-sm shrink-0')} />
                        <select value={deliveryTypeId} onChange={e => setDeliveryTypeId(Number(e.target.value))} disabled={isLoading}
                          className="select flex-1 min-w-0 text-xs"
                          aria-label={t('sale.deliveryType')}
                        >
                          {deliveryTypes.map(dt => (
                            <option key={dt.id} value={dt.id}>{dt.name}</option>
                          ))}
                        </select>
                      </div>
                      {/* Desktop: Delivery Zone selector */}
                      {deliveryZones.filter(z => z.is_active).length > 0 && (
                        <div className="flex items-center gap-1.5 min-w-0">
                          <span className={iconClass('lucide:map-pin', 'text-base-content/50 text-sm shrink-0')} />
                          <select value={selectedZoneId} onChange={e => setSelectedZoneId(Number(e.target.value))} disabled={isLoading}
                            className="select flex-1 min-w-0 text-xs"
                            aria-label={t('sale.zone')}
                          >
                            {deliveryZones.filter(z => z.is_active).map(z => (
                              <option key={z.id} value={z.id}>{z.name}</option>
                            ))}
                          </select>
                        </div>
                      )}
                    </div>
                    {/* Desktop: Distance input */}
                    <div className="flex items-center gap-2">
                      <span className={iconClass('lucide:ruler', 'text-base-content/50 text-sm')} />
                      <input type="number" value={deliveryDistance} onChange={e => setDeliveryDistance(Math.max(0, Number(e.target.value)))}
                        placeholder="0" min="0" step="0.5" disabled={isLoading}
                        className="input flex-1" />
                      <span className="text-xs text-base-content/50 w-5">km</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={iconClass('lucide:map-pin', 'text-base-content/50 text-sm')} />
                      <input type="text" value={deliveryAddress} onChange={e => setDeliveryAddress(e.target.value)}
                        placeholder={t('sale.deliveryAddress')} disabled={isLoading}
                        className="input flex-1" />
                    </div>
                    {selectedZone && deliveryFee > 0 && (
                      <div>
                        {exceedsMaxDistance ? (
                          <>
                            <p className="text-[11px] text-warning dark:text-warning/80 font-medium">
                              <span className={iconClass('lucide:alert-triangle', 'w-3 h-3 inline-block mr-0.5')} />
                              Exceeds {selectedZone.max_distance} km max — capped
                            </p>
                            <p className="text-[11px] text-base-content/50">
                              Fee: {formatPrice(selectedZone.base_fee)} + {selectedZone.max_distance}km × {formatPrice(selectedZone.fee_per_km)} = {formatPrice(deliveryFee)}
                            </p>
                          </>
                        ) : (
                          <p className="text-[11px] text-base-content/50">
                            Fee: {settings.currency} {selectedZone.base_fee.toFixed(2)} + {deliveryDistance}km × {selectedZone.fee_per_km.toFixed(2)}
                          </p>
                        )}
                      </div>
                    )}
                    {!selectedZone && deliveryFee > 0 && (
                      <p className="text-[11px] text-base-content/50">
                        Fee: {formatPrice(deliveryFee)}
                      </p>
                    )}
                  </div>
                )}
              </Card>

              {/* Employee Assignment Card — hidden for dine-in (shown inline next to Table above) */}
              {orderType !== 'dine-in' && (
                <Card>
                <div className="flex items-center gap-2 mb-2">
                  <span className={iconClass('lucide:user-check', 'text-base-content/50')} />
                  <label className="text-sm font-medium text-base-content/80">{t('sale.assignTo')}</label>
                </div>
                <select value={employeeId} onChange={e => setEmployeeId(Number(e.target.value))} disabled={isLoading}
                  className="select w-full"
                >
                  <option value={0}>{t('sale.noAssignment')}</option>
                  {employees.map(emp => (<option key={emp.id} value={emp.id}>{emp.name}</option>))}
                </select>
                </Card>
              )}

              {/* Order Notes Card */}
                <Card>
                <div className="flex items-center gap-2 mb-2">
                  <span className={iconClass('lucide:sticky-note', 'text-base-content/50')} />
                  <label className="text-sm font-medium text-base-content/80">Order Notes</label>
                </div>
                <textarea
                  value={orderNotes}
                  onChange={e => setOrderNotes(e.target.value)}
                  placeholder={t('sale.orderNotesPlaceholder') || 'Special instructions, allergies, notes...'}
                  rows={3}
                  disabled={isLoading}
                  className="textarea w-full text-sm resize-none"
                />
                {orderNotes && (
                  <p className="text-[10px] text-primary mt-1">
                    Notes will appear on the order ticket
                  </p>
                )}
              </Card>

              {/* Quick Notes — selectable notes that append into the order notes */}
              <Card>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={iconClass('lucide:sticky-note', 'text-base-content/50')} />
                    <label className="text-sm font-medium text-base-content/80">{t('sale.quickNotes') || 'Quick Notes'}</label>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowQuickNoteForm(s => !s)}
                    className="btn btn-ghost btn-xs gap-1 text-primary"
                  >
                    <span className="icon-[tabler--plus] w-3 h-3" />
                    {t('sale.newNote') || 'New note'}
                  </button>
                </div>

                {showQuickNoteForm && (
                  <div className="space-y-2 mb-2">
                    <textarea
                      value={quickNoteText}
                      onChange={e => setQuickNoteText(e.target.value)}
                      placeholder={t('sale.newNotePlaceholder') || 'Note text...'}
                      rows={2}
                      className="textarea w-full text-xs resize-none"
                    />
                    <div className="flex gap-2 justify-end">
                      <button
                        type="button"
                        onClick={() => { setQuickNoteText(''); setShowQuickNoteForm(false); }}
                        className="btn btn-ghost btn-xs"
                      >
                        {t('common.cancel')}
                      </button>
                      <button
                        type="button"
                        onClick={handleQuickAddNote}
                        disabled={!quickNoteText.trim()}
                        className="btn btn-primary btn-xs gap-1"
                      >
                        <span className="icon-[tabler--check] w-3 h-3" />
                        {t('sale.quickAddNote') || 'Add to order'}
                      </button>
                    </div>
                  </div>
                )}

                {selectableNotes.length === 0 ? (
                  <p className="text-[10px] text-base-content/40 italic">
                    {t('sale.quickNotesHint') || 'No quick notes yet — mark notes as selectable in Notes.'}
                  </p>
                ) : (
                  <>
                    <div className="flex flex-wrap gap-1.5">
                      {selectableNotes.map(note => (
                        <button
                          key={note.id}
                          type="button"
                          onClick={() => appendQuickNote(note)}
                          className="tag tag--sm tag--ghost hover:tag--primary cursor-pointer transition-all"
                          title={note.template_body}
                        >
                          {note.name}
                        </button>
                      ))}
                    </div>
                    <p className="text-[10px] text-base-content/40 mt-1.5">
                      {t('sale.quickNotesHint') || 'Tap a note to add it to the order'}
                    </p>
                  </>
                )}
              </Card>

              {/* Receipt Template Notes Selector — pulls from notes with category=receipt or use_as_template flag */}
              {templateNotes.length > 0 && (
                <Card>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={iconClass('lucide:receipt', 'text-base-content/50')} />
                    <label className="text-sm font-medium text-base-content/80">{t('notes.receiptTemplate') || 'Receipt Template'}</label>
                  </div>
                  <select
                    value={selectedTemplateId}
                    onChange={e => setSelectedTemplateId(Number(e.target.value))}
                    disabled={isLoading}
                    className="select w-full text-sm"
                  >
                    <option value={0}>None</option>
                    {templateNotes.map(note => (
                      <option key={note.id} value={note.id}>
                        {note.name}{note.category ? ` (${note.category})` : ''}
                      </option>
                    ))}
                  </select>
                  {selectedTemplateId > 0 && (
                    <p className="text-[10px] text-accent mt-1">
                      Template content will be appended to receipt footer
                    </p>
                  )}
                </Card>
              )}

              {/* Total Amount Card — centered, enhanced */}
                <Card transitional className="text-center">
                <h2 className="text-xs font-medium text-base-content/50 uppercase tracking-wider mb-1.5 flex items-center justify-center gap-1.5">
                  <span className={iconClass('lucide:wallet', 'w-3.5 h-3.5 text-primary')} />
                  {t('sale.totalAmount')}
                </h2>
                <p className={`text-2xl font-extrabold mb-1 ${isLoading ? 'text-slate-400 animate-pulse' : 'text-primary dark:text-primary/80'}`}>
                  {isLoading ? '—' : `${settings.currency} ${(totalAmount + deliveryFee).toFixed(2)}`}
                </p>
                {deliveryFee > 0 && (
                  <p className="text-[11px] text-base-content/50">
                    Subtotal: {formatPrice(totalAmount)} + Delivery: {formatPrice(deliveryFee)}
                  </p>
                )}
                <span className="badge badge-soft badge-primary gap-1.5 mt-1.5">
                  <span className={iconClass('lucide:shopping-bag', 'w-3 h-3')} />
                  {t('sale.itemsSelected', { count: cart.length })}
                </span>
              </Card>

              {/* Cart mini-summary in sidebar */}
              {cart.length > 0 && (
                  <Card className="max-h-[200px] overflow-y-auto">
                  <h3 className="text-xs font-medium text-base-content/50 uppercase tracking-wider mb-2">{t('sale.cartSummary')}</h3>
                  <div className="space-y-1.5">
                    {cart.map(item => (
                      <div key={item.id} className="flex justify-between text-xs text-slate-700 dark:text-white/70">
                        <span className="truncate mr-2">{item.name} ×{item.quantity}</span>
                        <span className="font-medium flex-shrink-0">{formatPrice(item.price * item.quantity)}</span>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </div>
          </div>

          {/* Collapsed peek tab — visible on hover when sidebar is closed */}
          {!sidebarOpen && !sidebarHovered && (
            <div
              className="absolute right-0 top-24 w-4 h-32 rounded-l-lg bg-teal-400/30 dark:bg-primary/20 cursor-pointer hover:bg-teal-400/50 dark:hover:bg-primary/40 transition-colors"
              onMouseEnter={() => setSidebarHovered(true)}
            />
          )}
        </div>
      </div>

      {/* Success Dialog */}
      {showSuccessDialog && receiptData && (
        <div
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto"
        >
          <div
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-md w-full my-8 transition-colors duration-300"
          >
            <div className="text-center">
              <div
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="mx-auto mb-4"
              >
                <span className={iconClass('lucide:circle-check', 'w-16 h-16 text-primary mx-auto')} />
              </div>

              <h3
                className="text-2xl font-bold text-base-content mb-6"
              >
                {t('sale.saleComplete')}
              </h3>

              {/* Order Details Badge */}
              <div
                className="flex flex-wrap justify-center gap-2 mb-4"
              >
                <span className="px-3 py-1 bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80 rounded-full text-xs font-medium">
                  {receiptData.orderType.charAt(0).toUpperCase() + receiptData.orderType.slice(1)}
                </span>
                {receiptData.tableNumber && (
                  <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full text-xs font-medium">
                    Table {receiptData.tableNumber}
                  </span>
                )}
                {receiptData.deliveryTypeName && (
                  <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900/20 text-warning dark:text-warning/80 rounded-full text-xs font-medium">
                    {receiptData.deliveryTypeName}
                  </span>
                )}
                {receiptData.employeeName && (
                  <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900/20 text-secondary dark:text-purple-400 rounded-full text-xs font-medium">
                    {receiptData.employeeName}
                  </span>
                )}
              </div>

              {/* Receipt Preview */}
              <div className="mb-6">
                <Receipt
                  ref={receiptRef}
                  products={receiptData.products}
                  totalAmount={receiptData.totalAmount + (receiptData.deliveryFee || 0)}
                  date={receiptData.date}
                  time={receiptData.time}
                  settings={settings}
                  receiptNumber={receiptData.receiptNumber}
                  orderType={receiptData.orderType}
                  deliveryTypeName={receiptData.deliveryTypeName}
                  deliveryAddress={receiptData.deliveryAddress}
                  deliveryFee={receiptData.deliveryFee}
                  deliveryZoneName={receiptData.deliveryZoneName}
                  deliveryDistance={receiptData.deliveryDistance}
                />
              </div>

              {/* Invoice Type Selector */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-base-content/80 mb-1.5">
                  {t('invoice.typeLabel')}
                </label>
                <select
                  value={invoiceType}
                  onChange={(e) => setInvoiceType(e.target.value as InvoiceType)}
                  className="select w-full"
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
                <button
                  onClick={handleDownloadPDF}
                  disabled={isDownloadingPDF}
                  className={`py-3 px-4 text-white rounded-xl font-semibold
                    transition-all duration-300 flex items-center justify-center gap-2 ${
                      isDownloadingPDF ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-500'
                    }`}
                >
                  {isDownloadingPDF ? (
                    <>
                      <div
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
                      />
                      <span>{t('sale.saving')}</span>
                    </>
                  ) : (
                    <>
                      <span className={iconClass('lucide:download', 'text-xl')} />
                      {t('sale.pdf')}
                    </>
                  )}
                </button>

                <button
                  onClick={handlePrint}
                  disabled={isPrinting}
                  className={`py-3 px-4 text-white rounded-xl font-semibold
                    transition-all duration-300 flex items-center justify-center gap-2 ${
                      isPrinting ? 'bg-purple-300 cursor-not-allowed' : 'bg-purple-500'
                    }`}
                >
                  {isPrinting ? (
                    <>
                      <div
                        className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
                      />
                      <span>{t('sale.printing')}</span>
                    </>
                  ) : (
                    <>
                      <span className={iconClass('lucide:printer', 'text-xl')} />
                      {t('sale.print')}
                    </>
                  )}
                </button>
              </div>

              <button
                onClick={handleDownloadInvoice}
                disabled={isInvoiceDownloading}
                className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-semibold 
                  transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed mb-4"
              >
                {isInvoiceDownloading ? (
                  <div
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
                  />
                ) : (
                  <>
                    <span className={iconClass('lucide:file-text', 'text-xl')} />
                    {t('invoice.downloadInvoice')}
                  </>
                )}
              </button>

              <button
                onClick={handleNewSale}
                className="w-full py-3 px-4 bg-primary text-white rounded-xl font-semibold
                  transition-all duration-300 flex items-center justify-center gap-2"
              >
                <span className={iconClass('lucide:shopping-cart', 'text-xl')} />
                {t('sale.startNewSale')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PDF Success Dialog */}
      {showPDFSuccessDialog && (
        <div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={() => setShowPDFSuccessDialog(false)}
        >
          <div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-white dark:bg-slate-800 rounded-2xl p-6 max-w-md w-full transition-colors duration-300"
            onClick={e => e.stopPropagation()}
          >
            <div className="text-center">
              <div
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="mx-auto mb-4"
              >
                <span className={iconClass('lucide:circle-check', 'w-16 h-16 text-green-500 mx-auto')} />
              </div>

              <h3
                className="text-2xl font-bold text-base-content mb-2"
              >
                {t('sale.pdfSaved')}
              </h3>

              <p
                className="text-slate-600 dark:text-slate-300 mb-6 break-all text-sm"
              >
                {savedPDFPath}
              </p>

              <button
                onClick={() => setShowPDFSuccessDialog(false)}
                className="w-full py-3 px-4 bg-green-500 text-white rounded-xl font-semibold
                  transition-all duration-300 hover:bg-green-600"
              >
                {t('common.close')}
              </button>
            </div>
          </div>
        </div>
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

