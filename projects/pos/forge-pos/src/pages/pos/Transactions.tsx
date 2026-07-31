import { useState, useMemo, useEffect, useRef } from 'react';
import { useKeyboardTabNav } from '../../hooks/useKeyboardTabNav';
import { invoke } from '@tauri-apps/api/core';
import { Transaction, Settings } from '../../types';
import DatePicker from '../../components/ui/DatePicker';
import Receipt from '../../components/pos/Receipt';
import { InvoiceType } from '../../types';
import { downloadInvoicePDF } from '../../utils/invoicePdf';
import jsPDF from 'jspdf';
import PageLayout from '../../components/layout/PageLayout';
import { useStatusToast } from '../../hooks/useStatusToast';
import StatusToast from '../../components/ui/StatusToast';
import { SkeletonTable, SkeletonList } from '../../components/ui/Skeleton';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';
import Card from '../../components/ui/Card';
import StatCard from '../../components/ui/StatCard';

type TabId = 'timeTotal' | 'productStats' | 'relatedProducts' | 'invoices';

interface ProductStat {
  name: string;
  count: number;
  totalAmount: number;
}

export default function Transactions() {
  const { t } = useTranslation();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabId>('timeTotal');
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);
  const [productSearch, setProductSearch] = useState('');
  const [relatedSearch, setRelatedSearch] = useState('');
  type ProductSortField = 'name' | 'quantity' | 'revenue';
  interface ProductSortCriterion { field: ProductSortField; order: 'asc' | 'desc' }
  const [productSortChain, setProductSortChain] = useState<ProductSortCriterion[]>([{ field: 'revenue', order: 'desc' }]);
  const [productPage, setProductPage] = useState(1);
  type RelatedSortField = 'name' | 'units' | 'revenue';
  interface SortCriterion { field: RelatedSortField; order: 'asc' | 'desc' }
  const [relatedSortChain, setRelatedSortChain] = useState<SortCriterion[]>([{ field: 'revenue', order: 'desc' }]);
  type InvoiceSortField = 'date' | 'amount' | 'type';
  interface InvoiceSortCriterion { field: InvoiceSortField; order: 'asc' | 'desc' }
  const [invoiceSortChain, setInvoiceSortChain] = useState<InvoiceSortCriterion[]>([{ field: 'date', order: 'desc' }]);
  const PRODUCTS_PER_PAGE = 20;
  const [showReceiptDialog, setShowReceiptDialog] = useState<Transaction | null>(null);
  const [invoiceType, setInvoiceType] = useState<InvoiceType>('tax');
  const [isInvoiceDownloading, setIsInvoiceDownloading] = useState(false);
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);
  const [settings, setSettings] = useState<Settings>({
    restaurant_name: 'Forge POS',
    address: '',
    phone: '',
    currency: 'USD',
    receipt_footer: 'Thank you for your business!'
  });
  const receiptRef = useRef<HTMLDivElement>(null);

  // Status toast — load + delete errors surface visibly; quiet reload keeps
  // the skeleton from pulsing just because a delete succeeded.
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setLoading(true);
    try {
      const [transactionsRes, settingsRes] = await Promise.all([
        invoke<Transaction[]>('get_transactions'),
        invoke<Settings>('get_settings')
      ]);

      setTransactions(transactionsRes);
      if (settingsRes) {
        setSettings({
          restaurant_name: settingsRes.restaurant_name || 'Forge POS',
          address: settingsRes.address || '',
          phone: settingsRes.phone || '',
          currency: settingsRes.currency || 'USD',
          receipt_footer: settingsRes.receipt_footer || 'Thank you for your business!'
        });
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
      // Even quiet reloads must surface — silent reloads would leave the user
      // looking at a stale list with no indication their data is out of date.
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      if (!quiet) setLoading(false);
    }
  };

  const filteredTransactions = useMemo(() => {
    return transactions.filter(t => {
      if (!startDate && !endDate) return true;
      const transactionDate = new Date(t.date);
      const start = startDate ? new Date(startDate) : null;
      const end = endDate ? new Date(endDate) : null;

      if (start && end) {
        return transactionDate >= start && transactionDate <= end;
      } else if (start) {
        return transactionDate >= start;
      } else if (end) {
        return transactionDate <= end;
      }
      return true;
    });
  }, [transactions, startDate, endDate]);

  // ---- Time-based grouping ----
  const timeGrouped = useMemo(() => {
    const groups = new Map<string, { transactions: Transaction[]; totalRevenue: number; orderCount: number }>();

    for (const tx of filteredTransactions) {
      const key = tx.date;
      if (!groups.has(key)) {
        groups.set(key, { transactions: [], totalRevenue: 0, orderCount: 0 });
      }
      const group = groups.get(key)!;
      group.transactions.push(tx);
      group.totalRevenue += tx.total_amount;
      group.orderCount++;
    }

    return Array.from(groups.entries())
      .map(([date, data]) => ({ date, ...data }))
      .sort((a, b) => b.date.localeCompare(a.date));
  }, [filteredTransactions]);

  // ---- Product Statistics ----
  const productStats = useMemo((): ProductStat[] => {
    const stats = new Map<string, { count: number; totalAmount: number }>();

    transactions.forEach(transaction => {
      transaction.items.forEach(item => {
        const existing = stats.get(item.name) || { count: 0, totalAmount: 0 };
        stats.set(item.name, {
          count: existing.count + item.quantity,
          totalAmount: existing.totalAmount + (item.price * item.quantity)
        });
      });
    });

    return Array.from(stats.entries()).map(([name, data]) => ({
      name,
      count: data.count,
      totalAmount: data.totalAmount
    })).sort((a, b) => b.totalAmount - a.totalAmount);
  }, [transactions]);

  // ---- Related Products — group invoices by product ----
  const productInvoices = useMemo(() => {
    const map = new Map<string, { productName: string; invoices: { id: number; date: string; time: string; quantity: number; price: number; total: number; currency: string }[]; totalQty: number; totalRev: number }>();

    for (const tx of filteredTransactions) {
      for (const item of tx.items) {
        if (!map.has(item.name)) {
          map.set(item.name, { productName: item.name, invoices: [], totalQty: 0, totalRev: 0 });
        }
        const entry = map.get(item.name)!;
        entry.invoices.push({
          id: tx.id,
          date: tx.date,
          time: tx.time,
          quantity: item.quantity,
          price: item.price,
          total: item.subtotal || (item.price * item.quantity),
          currency: tx.currency,
        });
        entry.totalQty += item.quantity;
        entry.totalRev += item.subtotal || (item.price * item.quantity);
      }
    }

    return Array.from(map.values()).sort((a, b) => b.totalRev - a.totalRev);
  }, [filteredTransactions]);

  // ── Time-bucketed KPIs (Today / This Week / This Month / Outstanding) ──
  // Uses full transactions (unfiltered) so KPIs always show true calendar periods
  const todayKpis = useMemo(() => {
    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);
    const weekStart = new Date(now); weekStart.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1));
    const monthStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;

    const todayTx = transactions.filter(t => t.date === todayStr);
    const weekTx = transactions.filter(t => t.date >= weekStart.toISOString().slice(0, 10));
    const monthTx = transactions.filter(t => t.date >= monthStart);
    const outstandingTx = transactions.filter(t => t.status !== 'completed');

    return {
      todayRevenue: todayTx.reduce((s, t) => s + t.total_amount, 0),
      todayOrders: todayTx.length,
      weekRevenue: weekTx.reduce((s, t) => s + t.total_amount, 0),
      weekOrders: weekTx.length,
      monthRevenue: monthTx.reduce((s, t) => s + t.total_amount, 0),
      monthOrders: monthTx.length,
      outstanding: outstandingTx.length,
    };
  }, [transactions]);

  const handleDeleteTransaction = async (id: number) => {
    if (!confirm(t('transactions.deleteConfirm'))) return;

    try {
      await invoke('delete_transaction', { id });
      setTransactions(prev => prev.filter(t => t.id !== id));
      showSuccess(t('common.deleted'));
      // Quiet reload reconciles list + analytics dependencies without
      // re-pulsing the skeleton.
      loadData({ quiet: true });
    } catch (error) {
      console.error('Error deleting transaction:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const clearFilters = () => {
    setStartDate("");
    setEndDate("");
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadInvoice = async () => {
    if (!showReceiptDialog) return;
    setIsInvoiceDownloading(true);
    try {
      await downloadInvoicePDF({
        invoiceType,
        invoiceNumber: `INV-${showReceiptDialog.id}`,
        date: showReceiptDialog.date,
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
        items: showReceiptDialog.items.map(item => ({
          name: item.name,
          quantity: item.quantity,
          unit: item.unit,
          price: item.price,
        })),
        currency: showReceiptDialog.currency,
        taxRate: settings.tax_rate ? parseFloat(settings.tax_rate) : 0,
        notes: settings.receipt_footer,
        orderType: showReceiptDialog.order_type,
      });
    } catch (error) {
      console.error('Error generating invoice PDF:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsInvoiceDownloading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!showReceiptDialog) {
      alert(t('transactions.receiptReady'));
      return;
    }

    try {
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: [80, 297]
      });

      let yPos = 10;
      const pageWidth = 80;
      const margin = 5;
      const contentWidth = pageWidth - (margin * 2);

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

      pdf.text(`Date: ${showReceiptDialog.date}  Time: ${showReceiptDialog.time}`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 4;
      pdf.text(`Receipt #: ${showReceiptDialog.id}`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 6;

      pdf.setDrawColor(0);
      pdf.setLineWidth(0.3);
      for (let i = 0; i < contentWidth; i += 2) {
        pdf.line(margin + i, yPos, margin + i + 1, yPos);
      }
      yPos += 5;

      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Item', margin, yPos);
      pdf.text('Qty', pageWidth / 2, yPos, { align: 'center' });
      pdf.text('Price', pageWidth - margin, yPos, { align: 'right' });
      yPos += 5;

      pdf.setFont('helvetica', 'normal');
      showReceiptDialog.items.forEach(item => {
        const itemName = item.name.length > 18 ? item.name.substring(0, 18) + '...' : item.name;
        const itemPrice = item.subtotal || (item.price * item.quantity);
        pdf.text(itemName, margin, yPos);
        pdf.text(`${item.quantity} ${item.unit}`, pageWidth / 2, yPos, { align: 'center' });
        pdf.text(`${showReceiptDialog.currency} ${itemPrice.toFixed(2)}`, pageWidth - margin, yPos, { align: 'right' });
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
      pdf.text(`${showReceiptDialog.currency} ${showReceiptDialog.total_amount.toFixed(2)}`, pageWidth - margin, yPos, { align: 'right' });
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

      const filename = `receipt-${showReceiptDialog.id}.pdf`;
      pdf.save(filename);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert(t('transactions.pdfError'));
    }
  };

  // ---- Filtered Related Products ----
  const filteredRelatedProducts = useMemo(() => {
    if (!relatedSearch.trim()) return productInvoices;
    const q = relatedSearch.toLowerCase().trim();
    return productInvoices.filter(p => p.productName.toLowerCase().includes(q));
  }, [productInvoices, relatedSearch]);

  // ---- CSV Export ----
  const downloadCSV = useMemo(() => (filename: string, headers: string[], rows: string[][]) => {
    const escapeField = (v: string) => {
      if (v.includes(',') || v.includes('"') || v.includes('\n')) return `"${v.replace(/"/g, '""')}"`;
      return v;
    };
    const csv = [
      headers.map(h => escapeField(h)).join(','),
      ...rows.map(r => r.map(v => escapeField(v)).join(',')),
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  // ---- Filtered + Sorted Product Stats (multi-column sort chain) ----
  const sortedProductStats = useMemo(() => {
    let items = productStats;
    // Apply search filter
    if (productSearch.trim()) {
      const query = productSearch.toLowerCase().trim();
      items = items.filter(p => p.name.toLowerCase().includes(query));
    }
    // Apply sorting in reverse order so the primary sort (first in chain) takes precedence
    const sorted = [...items];
    for (let i = productSortChain.length - 1; i >= 0; i--) {
      const { field, order } = productSortChain[i];
      const dir = order === 'asc' ? 1 : -1;
      switch (field) {
        case 'name':
          sorted.sort((a, b) => dir * a.name.localeCompare(b.name));
          break;
        case 'quantity':
          sorted.sort((a, b) => dir * (a.count - b.count));
          break;
        case 'revenue':
        default:
          sorted.sort((a, b) => dir * (a.totalAmount - b.totalAmount));
          break;
      }
    }
    return sorted;
  }, [productStats, productSearch, productSortChain]);

  // ---- Paginated Product Stats ----
  const totalProductPages = useMemo(() => Math.max(1, Math.ceil(sortedProductStats.length / PRODUCTS_PER_PAGE)), [sortedProductStats]);
  const paginatedProductStats = useMemo(() => {
    const start = (productPage - 1) * PRODUCTS_PER_PAGE;
    return sortedProductStats.slice(start, start + PRODUCTS_PER_PAGE);
  }, [sortedProductStats, productPage]);

  // ---- Sorted Related Products (multi-column sort chain) ----
  const sortedRelatedProducts = useMemo(() => {
    let items = filteredRelatedProducts;
    const sorted = [...items];
    // Apply sorts in reverse order so the primary sort (first in chain) takes precedence
    for (let i = relatedSortChain.length - 1; i >= 0; i--) {
      const { field, order } = relatedSortChain[i];
      const dir = order === 'asc' ? 1 : -1;
      switch (field) {
        case 'name':
          sorted.sort((a, b) => dir * a.productName.localeCompare(b.productName));
          break;
        case 'units':
          sorted.sort((a, b) => dir * (a.totalQty - b.totalQty));
          break;
        case 'revenue':
          sorted.sort((a, b) => dir * (a.totalRev - b.totalRev));
          break;
      }
    }
    return sorted;
  }, [filteredRelatedProducts, relatedSortChain]);

  // ---- Sorted Invoices (multi-column sort chain) ----
  const sortedInvoices = useMemo(() => {
    const sorted = [...filteredTransactions];
    // Apply sorts in reverse order so the primary sort (first in chain) takes precedence
    for (let i = invoiceSortChain.length - 1; i >= 0; i--) {
      const { field, order } = invoiceSortChain[i];
      const dir = order === 'asc' ? 1 : -1;
      switch (field) {
        case 'date':
          sorted.sort((a, b) => dir * (`${a.date}T${a.time}`).localeCompare(`${b.date}T${b.time}`));
          break;
        case 'amount':
          sorted.sort((a, b) => dir * (a.total_amount - b.total_amount));
          break;
        case 'type':
          sorted.sort((a, b) => dir * a.order_type.localeCompare(b.order_type));
          break;
      }
    }
    return sorted;
  }, [filteredTransactions, invoiceSortChain]);

  // ---- Keyboard shortcuts for sort toggles, pagination & help ----
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't fire when typing in inputs/textareas
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      // Don't intercept browser shortcuts
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const key = e.key;

      // '?' opens shortcut help on any tab
      if (key === '?' || key === '/') {
        e.preventDefault();
        setShowShortcutHelp(prev => !prev);
        return;
      }

      const lower = key.toLowerCase();

      // Tab navigation — 1=Time Total, 2=Product Stats, 3=Related Products, 4=Invoices
      if (key >= '1' && key <= '4') {
        const tabMap: Record<string, TabId> = {
          '1': 'timeTotal',
          '2': 'productStats',
          '3': 'relatedProducts',
          '4': 'invoices',
        };
        const target = tabMap[key];
        if (target && target !== activeTab) {
          e.preventDefault();
          setActiveTab(target);
        }
        return;
      }

      // Filters: F to toggle, C to clear
      if (lower === 'f') {
        e.preventDefault();
        setShowFilters(prev => !prev);
        return;
      }
      if (lower === 'c' && (startDate || endDate)) {
        e.preventDefault();
        clearFilters();
        return;
      }

      // Arrow keys for pagination — only on Product Stats tab
      if (key === 'ArrowLeft' || key === 'ArrowRight') {
        if (activeTab === 'productStats' && totalProductPages > 1) {
          e.preventDefault();
          setProductPage(prev => {
            if (key === 'ArrowLeft') return Math.max(1, prev - 1);
            return Math.min(totalProductPages, prev + 1);
          });
        }
        return;
      }

      if (activeTab === 'productStats') {
        if (lower === 'n' || lower === 'q' || lower === 'r') {
          const shortcutMap: Record<string, ProductSortField> = {
            n: 'name',
            q: 'quantity',
            r: 'revenue',
          };
          const target = shortcutMap[lower];
          if (target) {
            e.preventDefault();
            const isShift = e.shiftKey;
            setProductPage(1);
            setProductSortChain(prev => {
              const existing = prev.find(c => c.field === target);
              if (isShift) {
                // Shift+key: add to chain or toggle order
                if (existing) {
                  return prev.map(c =>
                    c.field === target ? { ...c, order: c.order === 'asc' ? 'desc' : 'asc' } : c
                  );
                }
                return [...prev, { field: target, order: 'desc' }];
              } else {
                // Normal key: replace chain
                if (existing && prev.length === 1) {
                  return [{ field: target, order: prev[0].order === 'asc' ? 'desc' : 'asc' }];
                }
                return [{ field: target, order: 'desc' }];
              }
            });
          }
        }
      } else if (activeTab === 'invoices') {
        if (lower === 'd' || lower === 'a' || lower === 'o') {
          const shortcutMap: Record<string, InvoiceSortField> = {
            d: 'date',
            a: 'amount',
            o: 'type',
          };
          const target = shortcutMap[lower];
          if (target) {
            e.preventDefault();
            const isShift = e.shiftKey;
            setInvoiceSortChain(prev => {
              const existing = prev.find(c => c.field === target);
              if (isShift) {
                // Shift+key: add to chain or toggle order
                if (existing) {
                  return prev.map(c =>
                    c.field === target ? { ...c, order: c.order === 'asc' ? 'desc' : 'asc' } : c
                  );
                }
                return [...prev, { field: target, order: 'desc' }];
              } else {
                // Normal key: replace chain
                if (existing && prev.length === 1) {
                  return [{ field: target, order: prev[0].order === 'asc' ? 'desc' : 'asc' }];
                }
                return [{ field: target, order: 'desc' }];
              }
            });
          }
        }
      } else if (activeTab === 'relatedProducts') {
        if (lower === 'n' || lower === 'u' || lower === 'r') {
          const shortcutMap: Record<string, RelatedSortField> = {
            n: 'name',
            u: 'units',
            r: 'revenue',
          };
          const target = shortcutMap[lower];
          if (target) {
            e.preventDefault();
            const isShift = e.shiftKey;
            setRelatedSortChain(prev => {
              const existing = prev.find(c => c.field === target);
              if (isShift) {
                // Shift+key: add to chain or toggle order
                if (existing) {
                  return prev.map(c =>
                    c.field === target ? { ...c, order: c.order === 'asc' ? 'desc' : 'asc' } : c
                  );
                }
                return [...prev, { field: target, order: 'desc' }];
              } else {
                // Normal key: replace chain
                if (existing && prev.length === 1) {
                  return [{ field: target, order: prev[0].order === 'asc' ? 'desc' : 'asc' }];
                }
                return [{ field: target, order: 'desc' }];
              }
            });
          }
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, productSortChain, totalProductPages, relatedSortChain, invoiceSortChain, startDate, endDate]);

  const handleExportProductStatsCSV = () => {
    downloadCSV(
      `product-stats-${new Date().toISOString().split('T')[0]}.csv`,
      ['Product', 'Total Sold', 'Revenue', 'Avg. Price'],
      sortedProductStats.map(p => [
        p.name,
        String(p.count),
        (transactions[0]?.currency || '') + ' ' + p.totalAmount.toFixed(2),
        (transactions[0]?.currency || '') + ' ' + (p.totalAmount / p.count).toFixed(2),
      ])
    );
  };

  const handleExportRelatedProductsCSV = () => {
    const rows: string[][] = [];
    const source = sortedRelatedProducts;
    for (const product of source) {
      for (const inv of product.invoices) {
        rows.push([
          product.productName,
          String(inv.id),
          inv.date,
          inv.time,
          String(inv.quantity),
          (inv.currency || transactions[0]?.currency || '') + ' ' + inv.price.toFixed(2),
          (inv.currency || transactions[0]?.currency || '') + ' ' + inv.total.toFixed(2),
        ]);
      }
    }
    downloadCSV(
      `product-invoices-${new Date().toISOString().split('T')[0]}.csv`,
      ['Product', 'Invoice #', 'Date', 'Time', 'Qty', 'Unit Price', 'Total'],
      rows
    );
  };

  // ---- Tab Definition ----
  const tabs: { key: TabId; label: string; icon: React.ReactNode }[] = [
    { key: 'timeTotal', label: 'Time Total', icon: <span className="icon-[tabler--calendar] w-5 h-5" /> },
    { key: 'productStats', label: 'Product Statistics', icon: <span className="icon-[tabler--chart-bar] w-5 h-5" /> },
    { key: 'relatedProducts', label: 'Related Products', icon: <span className="icon-[tabler--file-invoice] w-5 h-5" /> },
    { key: 'invoices', label: 'Invoices', icon: <span className="icon-[tabler--receipt] w-5 h-5" /> },
  ];

  // ── Arrow-key tab nav ──
  const txTabKeys: TabId[] = tabs.map(t => t.key);
  const { onKeyDown: onTxTabKeyDown } = useKeyboardTabNav(txTabKeys, activeTab, setActiveTab);

  if (loading) {
    return (
      <PageLayout title={t('transactions.title')}>
        <div className="space-y-6">
          <SkeletonList items={5} />
          <SkeletonTable rows={6} columns={5} />
        </div>
        {/* Render the toast here too so that load errors during the initial
            mount aren't swallowed by the skeleton-only branch — otherwise the
            <StatusToast /> JSX in the main return below wouldn't render until
            the failure had already auto-dismissed. */}
        <StatusToast
          type={status?.type ?? 'success'}
          message={status?.message ?? ''}
          visible={!!status}
          onDismiss={dismiss}
        />
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={t('transactions.title')}
      background="bg-linear-to-br from-base-200 via-secondary/15 to-base-200"
    >
      {/* Filters Button */}
      <div className="flex justify-end mb-4">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center text-base-content gap-2
            bg-secondary/20 px-4 py-2 rounded-lg
            transition-all duration-300 active:scale-[0.95]"
        >
          <span className="icon-[tabler--filter] w-5 h-5" />
          <span>{t('transactions.filters')}</span>
        </button>
      </div>

      {/* Tab Navigation */}
      <nav className="tabs tabs-boxed gap-1 mb-6 overflow-x-auto" aria-label="Transaction tabs" role="tablist" data-tab-prefix="tx-tab" onKeyDown={onTxTabKeyDown}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            type="button"
            role="tab"
            id={`tx-tab-${tab.key}`}
            aria-controls={`tx-panel-${tab.key}`}
            aria-selected={activeTab === tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`tab ${activeTab === tab.key ? 'tab-active' : ''}`}
          >
            {tab.icon}
            <span className="text-sm sm:text-base">{t('transactions.' + tab.key)}</span>
          </button>
        ))}
      </nav>

      {/* Filters */}
      {showFilters && (
        <div
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          <Card padding="md" transitional className="mb-6 overflow-visible">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <DatePicker
                label={t('transactions.startDate')}
                value={startDate}
                onChange={setStartDate}
              />
              <DatePicker
                label={t('transactions.endDate')}
                value={endDate}
                onChange={setEndDate}
              />
            </div>
            {(startDate || endDate) && (
              <div className="mt-4 flex justify-end">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 text-error hover:text-error
                    hover:bg-error/10 rounded-lg transition-colors"
                >
                  {t('transactions.clearFilters')}
                </button>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* ── Tab Content ── */}
      <div
        key={activeTab}
        role="tabpanel"
        id={`tx-panel-${activeTab}`}
        aria-labelledby={`tx-tab-${activeTab}`}
        transition={{ duration: 0.3 }}
      >
        {/* ========== TIME TOTAL TAB ========== */}
        {activeTab === 'timeTotal' && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                title={t('transactions.today') || 'Today'}
                value={`${transactions[0]?.currency || ''} ${todayKpis.todayRevenue.toFixed(2)}`}
                desc={todayKpis.todayOrders === 1 ? '1 order' : `${todayKpis.todayOrders} orders`}
                icon={<span className="icon-[tabler--calendar] w-6 h-6" />}
                color="primary"
              />
              <StatCard
                title={t('transactions.thisWeek') || 'This Week'}
                value={`${transactions[0]?.currency || ''} ${todayKpis.weekRevenue.toFixed(2)}`}
                desc={todayKpis.weekOrders === 1 ? '1 order' : `${todayKpis.weekOrders} orders`}
                icon={<span className="icon-[tabler--calendar-week] w-6 h-6" />}
                color="info"
              />
              <StatCard
                title={t('transactions.thisMonth') || 'This Month'}
                value={`${transactions[0]?.currency || ''} ${todayKpis.monthRevenue.toFixed(2)}`}
                desc={todayKpis.monthOrders === 1 ? '1 order' : `${todayKpis.monthOrders} orders`}
                icon={<span className="icon-[tabler--calendar-month] w-6 h-6" />}
                color="secondary"
              />
              <StatCard
                title={t('transactions.outstanding') || 'Outstanding'}
                value={todayKpis.outstanding}
                desc={todayKpis.outstanding === 0 ? 'All settled' : `${todayKpis.outstanding} pending`}
                icon={<span className="icon-[tabler--clock-exclamation] w-6 h-6" />}
                color={todayKpis.outstanding > 0 ? 'warning' : 'success'}
              />
            </div>

            {/* Time-based Groups */}
            {timeGrouped.length > 0 ? (
              <div className="space-y-4">
                {timeGrouped.map(group => (
                  <div
                    key={group.date}
                  >
                    <Card padding="md">
                      <div className="flex items-center justify-between mb-3 pb-2 border-b border-base-300/30">
                        <div className="flex items-center gap-2">
                          <span className="icon-[tabler--calendar] w-5 h-5 text-info" />
                          <h3 className="font-bold text-base-content">
                            {new Date(group.date + 'T00:00:00').toLocaleDateString('en-US', {
                              weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                            })}
                          </h3>
                      </div>
                      <div className="text-right tabular-nums">
                        <p className="text-sm text-base-content/50">{group.orderCount} {t('transactions.orders')}</p>
                        <p className="text-lg font-bold text-primary">
                          {transactions[0]?.currency || ''} {group.totalRevenue.toFixed(2)}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      {group.transactions.map(tx => (
                        <div key={tx.id} className="flex items-center justify-between p-2 rounded-lg bg-base-100/40">
                          <div className="flex items-center gap-3">
                            <span className="text-xs font-mono text-base-content/50">{tx.time}</span>
                            <span className="text-sm text-base-content font-medium">#{tx.id}</span>
                            <span className="text-xs text-base-content/50">{tx.items.length} {t('transactions.transactionItems')}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-base-content">
                              {tx.currency} {tx.total_amount.toFixed(2)}
                            </span>
                            <button
                              onClick={() => setShowReceiptDialog(tx)}
                              className="text-primary-content p-1.5 bg-primary dark:bg-primary/30 hover:bg-primary dark:hover:bg-primary/50 rounded-lg transition-all active:scale-[0.9]"
                            >
                              <span className="icon-[tabler--printer] w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteTransaction(tx.id)}
                              className="text-error hover:text-error p-1.5 transition-all active:scale-[0.9]"
                            >
                              <span className="icon-[tabler--trash] w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--calendar] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('transactions.noTimeTotalData')}</p>
              </div>
            )}
          </div>
        )}

        {/* ========== PRODUCT STATISTICS TAB ========== */}
        {activeTab === 'productStats' && (
          <div className="space-y-6">
            {/* Summary cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard
                title={t('reports.totalProductsSold')}
                value={productStats.reduce((s, p) => s + p.count, 0)}
                icon={<span className="icon-[tabler--chart-bar] w-6 h-6" />}
                color="info"
              />
              <StatCard
                title={t('transactions.revenue')}
                value={`${transactions[0]?.currency || ''} ${productStats.reduce((s, p) => s + p.totalAmount, 0).toFixed(2)}`}
                icon={<span className="icon-[tabler--moneybag] w-6 h-6" />}
                color="primary"
              />
              <StatCard
                title={t('transactions.uniqueProducts')}
                value={productStats.length}
                icon={<span className="icon-[tabler--apps] w-6 h-6" />}
                color="secondary"
              />
            </div>

            {/* Search + CSV Export */}
            {productStats.length > 0 && (
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-2">
                <div className="relative flex-1 max-w-xs">
                  <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-base-content/50" />
                  <input
                    type="text"
                    value={productSearch}
                    onChange={e => { setProductPage(1); setProductSearch(e.target.value); }}
                    placeholder={t('transactions.searchProduct')}
                    className="input__field w-full text-xs pl-9"
                  />
                  {productSearch && (
                    <button
                      onClick={() => { setProductPage(1); setProductSearch(''); }}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content transition-colors"
                    >
                      <span className="icon-[tabler--x] w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                <div className="flex items-center gap-1 bg-base-200/50 rounded-lg p-0.5">
                  {([
                    { key: 'name' as ProductSortField, label: t('transactions.sortName') },
                    { key: 'quantity' as ProductSortField, label: t('transactions.sortQuantity') },
                    { key: 'revenue' as ProductSortField, label: t('transactions.sortRevenue') },
                  ]).map(opt => {
                    const chainIdx = productSortChain.findIndex(c => c.field === opt.key);
                    const isInChain = chainIdx !== -1;
                    const criterion = isInChain ? productSortChain[chainIdx] : null;
                    const handleSortClick = (e: React.MouseEvent) => {
                      if (e.shiftKey) {
                        // Shift-click: add to chain or toggle order
                        setProductPage(1);
                        if (isInChain) {
                          setProductSortChain(prev => prev.map(c =>
                            c.field === opt.key ? { ...c, order: c.order === 'asc' ? 'desc' : 'asc' } : c
                          ));
                        } else {
                          setProductSortChain(prev => [...prev, { field: opt.key, order: 'desc' }]);
                        }
                      } else {
                        // Normal click: replace chain with just this field
                        setProductPage(1);
                        if (isInChain && productSortChain.length === 1) {
                          setProductSortChain([{ field: opt.key, order: criterion!.order === 'asc' ? 'desc' : 'asc' }]);
                        } else {
                          setProductSortChain([{ field: opt.key, order: 'desc' }]);
                        }
                      }
                    };
                    return (
                      <button
                        key={opt.key}
                        onClick={handleSortClick}
                        className={`flex items-center gap-0.5 px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                          isInChain
                            ? 'bg-info/10 dark:bg-info/40 text-info dark:text-info/70'
                            : 'text-base-content/50 hover:bg-base-100/50'
                        }`}
                        title={`${opt.label} (${opt.key === 'name' ? 'N' : opt.key === 'quantity' ? 'Q' : 'R'})${isInChain ? ` — #${chainIdx + 1} (shift-click to toggle)` : ' — shift-click to add to chain'}`}
                      >
                        <span className="hidden sm:inline text-[10px] font-mono opacity-60 mr-0.5">
                          {opt.key === 'name' ? 'N' : opt.key === 'quantity' ? 'Q' : 'R'}
                        </span>
                        {opt.label}
                        {isInChain && criterion && (
                          <>
                            {criterion.order === 'asc'
                              ? <span className="icon-[tabler--arrow-up] w-3 h-3" />
                              : <span className="icon-[tabler--arrow-down] w-3 h-3" />
                            }
                            <span className="text-[10px] font-bold text-info dark:text-info/80 ml-0.5">
                              {chainIdx + 1}
                            </span>
                          </>
                        )}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => setShowShortcutHelp(true)}
                  className="flex items-center justify-center w-7 h-7 rounded-lg text-xs font-medium shrink-0
                    bg-base-300/50 text-base-content/50
                    hover:bg-base-300/80 transition-colors"
                  title={t('transactions.shortcutHelp')}
                >
                  <span className="icon-[tabler--help-circle] w-4 h-4" />
                </button>
                <button
                  onClick={handleExportProductStatsCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium shrink-0
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="icon-[tabler--download] w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>
            )}
            {productStats.length > 0 && sortedProductStats.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--search] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('transactions.noSearchMatch')}</p>
                <button
                  onClick={() => setProductSearch('')}
                  className="text-sm font-medium text-primary hover:underline transition-colors"
                >
                  {t('common.clear')}
                </button>
              </div>
            ) : sortedProductStats.length > 0 ? (
              <Card>
                <h2 className="text-xl text-base-content mb-4">
                  {t('transactions.statsBreakdown')}
                  {productSearch && sortedProductStats.length !== productStats.length && (
                    <span className="text-sm font-normal text-base-content/50 ml-2">
                      ({sortedProductStats.length} / {productStats.length})
                    </span>
                  )}
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4">
                  {paginatedProductStats.map((stat) => (
                    <div
                      key={stat.name}
                      className="bg-base-100/50 rounded-lg p-3"
                    >
                      <h3 className="text-base-content font-medium mb-2">{stat.name}</h3>
                      <div className="flex justify-between text-sm">
                        <span className="text-base-content/60">{t('transactions.totalSold')}:</span>
                        <span className="text-base-content">{stat.count} {t('transactions.units')}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-base-content/60">{t('transactions.revenue')}:</span>
                        <span className="text-primary">{transactions[0]?.currency || ''} {stat.totalAmount.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-base-content/60">{t('transactions.avgPrice')}:</span>
                        <span className="text-base-content">{transactions[0]?.currency || ''} {(stat.totalAmount / stat.count).toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {sortedProductStats.length > PRODUCTS_PER_PAGE && (
                  <div className="flex items-center justify-between pt-4 mt-4 border-t border-base-300/30">
                    <span className="text-xs text-base-content/50">
                      {t('transactions.showingPage', { page: productPage, total: totalProductPages })}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => setProductPage(p => Math.max(1, p - 1))}
                        disabled={productPage <= 1}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                          disabled:opacity-30 disabled:cursor-not-allowed
                          bg-base-200/50 text-base-content/70
                          hover:bg-base-300"
                      >
                        {t('common.previous') || '‹'}
                      </button>
                      <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(totalProductPages, 7) }, (_, i) => {
                          let pageNum: number;
                          if (totalProductPages <= 7) {
                            pageNum = i + 1;
                          } else if (productPage <= 4) {
                            pageNum = i + 1;
                          } else if (productPage >= totalProductPages - 3) {
                            pageNum = totalProductPages - 6 + i;
                          } else {
                            pageNum = productPage - 3 + i;
                          }
                          return (
                            <button
                              key={pageNum}
                              onClick={() => setProductPage(pageNum)}
                              className={`w-7 h-7 rounded-lg text-xs font-medium transition-colors ${
                                pageNum === productPage
                                  ? 'bg-primary text-primary-content'
                                  : 'text-base-content/60 hover:bg-base-200/50'
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        })}
                      </div>
                      <button
                        onClick={() => setProductPage(p => Math.min(totalProductPages, p + 1))}
                        disabled={productPage >= totalProductPages}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors
                          disabled:opacity-30 disabled:cursor-not-allowed
                          bg-base-200/50 text-base-content/70
                          hover:bg-base-300"
                      >
                        {t('common.next') || '›'}
                      </button>
                    </div>
                  </div>
                )}
              </Card>
            ) : (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--chart-bar] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('transactions.noProductStatsData')}</p>
              </div>
            )}
          </div>
        )}

        {/* ========== RELATED PRODUCTS TAB ========== */}
        {activeTab === 'relatedProducts' && (
          <div className="space-y-4">
            {productInvoices.length > 0 && (
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-2">
                <div className="relative flex-1 max-w-xs">
                  <span className="icon-[tabler--search] absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-base-content/50" />
                  <input
                    type="text"
                    value={relatedSearch}
                    onChange={e => setRelatedSearch(e.target.value)}
                    placeholder={t('transactions.searchProduct')}
                    className="input__field w-full text-xs pl-9"
                  />
                  {relatedSearch && (
                    <button
                      onClick={() => setRelatedSearch('')}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-base-content transition-colors"
                    >
                      <span className="icon-[tabler--x] w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                <div className="flex items-center gap-1 bg-base-200/50 rounded-lg p-0.5">
                  {([
                    { key: 'name' as RelatedSortField, label: t('transactions.sortName') },
                    { key: 'units' as RelatedSortField, label: t('reports.sortUnits') },
                    { key: 'revenue' as RelatedSortField, label: t('transactions.sortRevenue') },
                  ]).map(opt => {
                    const chainIdx = relatedSortChain.findIndex(c => c.field === opt.key);
                    const isInChain = chainIdx !== -1;
                    const criterion = isInChain ? relatedSortChain[chainIdx] : null;
                    const handleSortClick = (e: React.MouseEvent) => {
                      if (e.shiftKey) {
                        // Shift-click: add to chain or toggle order
                        if (isInChain) {
                          setRelatedSortChain(prev => prev.map(c =>
                            c.field === opt.key ? { ...c, order: c.order === 'asc' ? 'desc' : 'asc' } : c
                          ));
                        } else {
                          setRelatedSortChain(prev => [...prev, { field: opt.key, order: 'desc' }]);
                        }
                      } else {
                        // Normal click: replace chain with just this field
                        if (isInChain && relatedSortChain.length === 1) {
                          setRelatedSortChain([{ field: opt.key, order: criterion!.order === 'asc' ? 'desc' : 'asc' }]);
                        } else {
                          setRelatedSortChain([{ field: opt.key, order: 'desc' }]);
                        }
                      }
                    };
                    return (
                      <button
                        key={opt.key}
                        onClick={handleSortClick}
                        className={`flex items-center gap-0.5 px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                          isInChain
                            ? 'bg-info/10 dark:bg-info/40 text-info dark:text-info/70'
                            : 'text-base-content/50 hover:bg-base-100/50'
                        }`}
                        title={`${opt.label} (${opt.key === 'name' ? 'N' : opt.key === 'units' ? 'U' : 'R'})${isInChain ? ` — #${chainIdx + 1} (shift-click to toggle)` : ' — shift-click to add to chain'}`}
                      >
                        <span className="hidden sm:inline text-[10px] font-mono opacity-60 mr-0.5">
                          {opt.key === 'name' ? 'N' : opt.key === 'units' ? 'U' : 'R'}
                        </span>
                        {opt.label}
                        {isInChain && criterion && (
                          <>
                            {criterion.order === 'asc'
                              ? <span className="icon-[tabler--arrow-up] w-3 h-3" />
                              : <span className="icon-[tabler--arrow-down] w-3 h-3" />
                            }
                            <span className="text-[10px] font-bold text-info dark:text-info/80 ml-0.5">
                              {chainIdx + 1}
                            </span>
                          </>
                        )}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={handleExportRelatedProductsCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium shrink-0
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="icon-[tabler--download] w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>
            )}
            {productInvoices.length > 0 && filteredRelatedProducts.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--search] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('transactions.noSearchMatch')}</p>
                <button
                  onClick={() => setRelatedSearch('')}
                  className="text-sm font-medium text-primary hover:underline transition-colors"
                >
                  {t('common.clear')}
                </button>
              </div>
            ) : filteredRelatedProducts.length > 0 ? (
              sortedRelatedProducts.map(product => (
                <div
                  key={product.productName}
                >
                  <Card padding="md">
                    <div className="flex items-center justify-between mb-3 pb-2 border-b border-base-300/30">
                      <div className="flex items-center gap-2">
                        <span className="icon-[tabler--chart-bar] w-5 h-5 text-info" />
                        <div>
                          <div className="flex items-center gap-1.5">
                            <h3 className="font-bold text-base-content">{product.productName}</h3>
                          {(() => {
                            const idx = relatedSortChain.findIndex(c => c.field === 'name');
                            if (idx === -1) return null;
                            const crit = relatedSortChain[idx];
                            return (
                              <span className="inline-flex items-center gap-0.5 text-primary text-xs">
                                {crit.order === 'asc' ? <span className="icon-[tabler--arrow-up] w-3 h-3" /> : <span className="icon-[tabler--arrow-down] w-3 h-3" />}
                                {relatedSortChain.length > 1 && <span className="text-[10px] font-bold">{idx + 1}</span>}
                              </span>
                            );
                          })()}
                        </div>
                        <p className="text-xs text-base-content/50">
                          {product.totalQty} {t('transactions.units')} sold across {product.invoices.length} {t('transactions.invoices')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right tabular-nums">
                      <p className="text-lg font-bold text-primary">
                        {product.invoices[0]?.currency || transactions[0]?.currency || ''} {product.totalRev.toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {/* Inline invoices table */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-2 px-3 text-base-content/50 font-medium text-xs">{t('reports.tableInvoice')}</th>
                          <th className="py-2 px-3 text-base-content/50 font-medium text-xs">{t('reports.tableDate')}</th>
                          <th className="py-2 px-3 text-base-content/50 font-medium text-xs">{t('reports.tableTime')}</th>
                          <th className="py-2 px-3 text-base-content/50 font-medium text-xs text-right">
                            <span className="inline-flex items-center gap-1">
                              {t('transactions.qty')}
                              {(() => {
                                const idx = relatedSortChain.findIndex(c => c.field === 'units');
                                if (idx === -1) return null;
                                const crit = relatedSortChain[idx];
                                return (
                                  <span className="inline-flex items-center gap-0.5 text-primary">
                                    {crit.order === 'asc' ? <span className="icon-[tabler--arrow-up] w-3 h-3" /> : <span className="icon-[tabler--arrow-down] w-3 h-3" />}
                                    {relatedSortChain.length > 1 && <span className="text-[10px] font-bold">{idx + 1}</span>}
                                  </span>
                                );
                              })()}
                            </span>
                          </th>
                          <th className="py-2 px-3 text-base-content/50 font-medium text-xs text-right">{t('transactions.unitPrice')}</th>
                          <th className="py-2 px-3 text-base-content/50 font-medium text-xs text-right">
                            <span className="inline-flex items-center gap-1">
                              {t('reports.tableAmount')}
                              {(() => {
                                const idx = relatedSortChain.findIndex(c => c.field === 'revenue');
                                if (idx === -1) return null;
                                const crit = relatedSortChain[idx];
                                return (
                                  <span className="inline-flex items-center gap-0.5 text-primary">
                                    {crit.order === 'asc' ? <span className="icon-[tabler--arrow-up] w-3 h-3" /> : <span className="icon-[tabler--arrow-down] w-3 h-3" />}
                                    {relatedSortChain.length > 1 && <span className="text-[10px] font-bold">{idx + 1}</span>}
                                  </span>
                                );
                              })()}
                            </span>
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {product.invoices.map(inv => (
                          <tr key={`${inv.id}-${product.productName}`} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-2 px-3 text-sm font-medium text-base-content">#{inv.id}</td>
                            <td className="py-2 px-3 text-sm text-base-content/70">{inv.date}</td>
                            <td className="py-2 px-3 text-sm text-base-content/70">{inv.time}</td>
                            <td className="py-2 px-3 text-sm text-right text-base-content tabular-nums">{inv.quantity}</td>
                            <td className="py-2 px-3 text-sm text-right text-base-content tabular-nums">{inv.currency} {inv.price.toFixed(2)}</td>
                            <td className="py-2 px-3 text-sm text-right font-bold text-primary tabular-nums">{inv.currency} {inv.total.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--file-invoice] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('transactions.noRelatedProductsData')}</p>
              </div>
            )}
          </div>
        )}

        {/* ========== INVOICES TAB ========== */}
        {activeTab === 'invoices' && (
          <div className="space-y-4">
            {filteredTransactions.length > 0 && (
              <div className="flex items-center gap-1 bg-base-200/50 rounded-lg p-0.5 w-fit">
                {([
                  { key: 'date' as InvoiceSortField, label: t('transactions.sortDate') },
                  { key: 'amount' as InvoiceSortField, label: t('transactions.sortAmount') },
                  { key: 'type' as InvoiceSortField, label: t('transactions.sortType') },
                ]).map(opt => {
                  const chainIdx = invoiceSortChain.findIndex(c => c.field === opt.key);
                  const isInChain = chainIdx !== -1;
                  const criterion = isInChain ? invoiceSortChain[chainIdx] : null;
                  const handleSortClick = (e: React.MouseEvent) => {
                    if (e.shiftKey) {
                      // Shift-click: add to chain or toggle order
                      if (isInChain) {
                        setInvoiceSortChain(prev => prev.map(c =>
                          c.field === opt.key ? { ...c, order: c.order === 'asc' ? 'desc' : 'asc' } : c
                        ));
                      } else {
                        setInvoiceSortChain(prev => [...prev, { field: opt.key, order: 'desc' }]);
                      }
                    } else {
                      // Normal click: replace chain with just this field
                      if (isInChain && invoiceSortChain.length === 1) {
                        setInvoiceSortChain([{ field: opt.key, order: criterion!.order === 'asc' ? 'desc' : 'asc' }]);
                      } else {
                        setInvoiceSortChain([{ field: opt.key, order: 'desc' }]);
                      }
                    }
                  };
                  return (
                    <button
                      key={opt.key}
                      onClick={handleSortClick}
                      className={`flex items-center gap-0.5 px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                        isInChain
                          ? 'bg-info/10 dark:bg-info/40 text-info dark:text-info/70'
                          : 'text-base-content/50 hover:bg-base-100/50'
                      }`}
                      title={`${opt.label} (${opt.key === 'date' ? 'D' : opt.key === 'amount' ? 'A' : 'O'})${isInChain ? ` — #${chainIdx + 1} (shift-click to toggle)` : ' — shift-click to add to chain'}`}
                    >
                      <span className="hidden sm:inline text-[10px] font-mono opacity-60 mr-0.5">
                        {opt.key === 'date' ? 'D' : opt.key === 'amount' ? 'A' : 'O'}
                      </span>
                      {opt.label}
                      {isInChain && criterion && (
                        <>
                          {criterion.order === 'asc'
                            ? <span className="icon-[tabler--arrow-up] w-3 h-3" />
                            : <span className="icon-[tabler--arrow-down] w-3 h-3" />
                          }
                          <span className="text-[10px] font-bold text-info dark:text-info/80 ml-0.5">
                            {chainIdx + 1}
                          </span>
                        </>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
            {filteredTransactions.length > 0 ? (
              sortedInvoices.map((transaction) => (
                <div
                  key={transaction.id}
                  exit={{ opacity: 0, x: 20 }}
                >
                  <Card padding="md" hover>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="icon-[tabler--receipt] w-5 h-5 text-info" />
                        <span className="font-bold text-base-content">#{transaction.id}</span>
                        {(() => {
                          const idx = invoiceSortChain.findIndex(c => c.field === 'type');
                          if (idx === -1) return null;
                          const crit = invoiceSortChain[idx];
                          return (
                            <span className="inline-flex items-center gap-0.5 text-primary text-xs">
                              {crit.order === 'asc' ? <span className="icon-[tabler--arrow-up] w-3 h-3" /> : <span className="icon-[tabler--arrow-down] w-3 h-3" />}
                              {invoiceSortChain.length > 1 && <span className="text-[10px] font-bold">{idx + 1}</span>}
                            </span>
                          );
                        })()}
                      </div>
                      <div className="flex items-center gap-1.5 text-base-content/60 text-sm mt-1">
                        <span>
                          {new Date(transaction.date).toLocaleDateString('en-US', {
                            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                          })}
                        </span>
                        {(() => {
                          const idx = invoiceSortChain.findIndex(c => c.field === 'date');
                          if (idx === -1) return null;
                          const crit = invoiceSortChain[idx];
                          return (
                            <span className="inline-flex items-center gap-0.5 text-primary">
                              {crit.order === 'asc' ? <span className="icon-[tabler--arrow-up] w-3 h-3" /> : <span className="icon-[tabler--arrow-down] w-3 h-3" />}
                              {invoiceSortChain.length > 1 && <span className="text-[10px] font-bold">{idx + 1}</span>}
                            </span>
                          );
                        })()}
                      </div>
                      <div className="text-base-content/60 text-sm">{transaction.time}</div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setShowReceiptDialog(transaction)}
                        className="text-primary-content p-2 bg-primary dark:bg-primary/30 hover:bg-primary dark:hover:bg-primary/50 rounded-lg transition-colors"
                      >
                        <span className="icon-[tabler--printer] w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteTransaction(transaction.id)}
                        className="text-error hover:text-error p-2"
                      >
                        <span className="icon-[tabler--trash] w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    {transaction.items.map((item, index) => (
                      <div key={index} className="flex flex-col sm:flex-row sm:justify-between text-base-content py-1">
                        <div className="flex-1">
                          <span className="font-medium">{item.name}</span>
                          <span className="text-base-content/60 ml-2">
                            ({item.quantity} {item.unit} × {transaction.currency} {(item.price || 0).toFixed(2)})
                          </span>
                        </div>
                        <div className="text-primary sm:ml-4">
                          {transaction.currency} {(item.subtotal || 0).toFixed(2)}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="border-t border-base-300/50 pt-3 flex justify-between items-center">
                    <span className="text-base-content font-semibold">{t('transactions.totalLabel')}</span>
                    <span className="flex items-center gap-1.5 text-xl font-bold text-primary">
                      {transaction.currency} {transaction.total_amount.toFixed(2)}
                      {(() => {
                        const idx = invoiceSortChain.findIndex(c => c.field === 'amount');
                        if (idx === -1) return null;
                        const crit = invoiceSortChain[idx];
                        return (
                          <span className="inline-flex items-center gap-0.5 text-primary">
                            {crit.order === 'asc' ? <span className="icon-[tabler--arrow-up] w-4 h-4" /> : <span className="icon-[tabler--arrow-down] w-4 h-4" />}
                            {invoiceSortChain.length > 1 && <span className="text-[10px] font-bold">{idx + 1}</span>}
                          </span>
                        );
                      })()}
                    </span>
                  </div>
                </Card>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center text-center py-12">
                <span className="icon-[tabler--receipt] w-12 h-12 text-base-content/40 mb-4" />
                <p className="text-base-content/70 text-lg mb-2">{t('transactions.noInvoicesData')}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Receipt Dialog */}
      {showReceiptDialog && (
        <div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-neutral/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 overflow-y-auto"
          onClick={() => setShowReceiptDialog(null)}
        >
          <div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            className="bg-base-100 rounded-2xl p-6 max-w-md w-full my-8 transition-colors duration-300"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-base-content">{t('transactions.receipt')}</h3>
              <button
                onClick={() => setShowReceiptDialog(null)}
                className="text-base-content/60 hover:text-base-content p-2"
              >
                <span className="icon-[tabler--x] w-6 h-6" />
              </button>
            </div>

            {/* Invoice Type Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-base-content/80 mb-1.5">
                {t('invoice.typeLabel')}
              </label>
              <select
                value={invoiceType}
                onChange={(e) => setInvoiceType(e.target.value as InvoiceType)}className="input__field input__field--select w-full"
              >
                <option value="tax">{t('invoice.typeTax')}</option>
                <option value="commercial">{t('invoice.typeCommercial')}</option>
                <option value="proforma">{t('invoice.typeProforma')}</option>
                <option value="credit">{t('invoice.typeCredit')}</option>
                <option value="receipt">{t('invoice.typeReceipt')}</option>
              </select>
            </div>

            <div className="mb-6">
              <Receipt
                ref={receiptRef}
                products={showReceiptDialog.items.map(item => ({
                  name: item.name,
                  quantity: item.quantity,
                  unit: item.unit,
                  price: item.subtotal || (item.price * item.quantity)
                }))}
                totalAmount={showReceiptDialog.total_amount}
                date={showReceiptDialog.date}
                time={showReceiptDialog.time}
                settings={settings}
                receiptNumber={showReceiptDialog.id.toString()}
                orderType={showReceiptDialog.order_type}
              />
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3">
              <button
                onClick={handleDownloadPDF}
                className="py-3 px-4 bg-info text-info-content rounded-xl font-semibold
                  transition-all duration-300 flex items-center justify-center gap-2"
              >
                <span className="icon-[tabler--file-download] text-xl" />
                {t('transactions.receiptPDF')}
              </button>

              <button
                onClick={handlePrint}
                className="py-3 px-4 bg-secondary text-secondary-content rounded-xl font-semibold
                  transition-all duration-300 flex items-center justify-center gap-2"
              >
                <span className="icon-[tabler--printer] text-xl" />
                {t('transactions.print')}
              </button>
            </div>

            <button
              onClick={handleDownloadInvoice}
              disabled={isInvoiceDownloading}
              className="w-full py-3 px-4 bg-primary hover:bg-primary/80 text-primary-content rounded-xl font-semibold
                transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isInvoiceDownloading ? (
                <div
                  className="w-5 h-5 border-2 border-primary-content/30 border-t-primary-content rounded-full animate-spin"
                />
              ) : (
                <>
                  <span className="icon-[tabler--file-invoice] text-xl" />
                  {t('invoice.downloadInvoice')}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Keyboard Shortcut Help Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcutHelp}
        onClose={() => setShowShortcutHelp(false)}
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

