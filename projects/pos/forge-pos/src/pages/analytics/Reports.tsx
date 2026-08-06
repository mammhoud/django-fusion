import { useState, useEffect, useMemo, useCallback } from 'react';
import { useKeyboardTabNav } from '../../hooks/useKeyboardTabNav';
import { useDashboardDeltas } from '../../hooks/useDashboardDeltas';
import { useSearchParams } from 'react-router-dom';
import PageLayout from '../../components/layout/PageLayout';
import { SkeletonTable, SkeletonCard } from '../../components/ui/Skeleton';
import Card from '../../components/ui/Card';
import { Badge } from '@/components/ui/badge';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../../components/shared/KeyboardShortcutsModal';
import StatCard from '../../components/ui/StatCard';
import TaxReportsPanel from '../../components/analytics/TaxReportsPanel';
import { useCurrency } from '../../contexts/CurrencyContext';
import ComparisonTable, { type ComparisonFilter } from '../../components/ui/ComparisonTable';
import { useApiQueries } from '../../hooks/useApi';
import {
  Sale, Settings, AnalyticsData, Ingredient, InventoryTransaction,
  Recipe, Employee, Product, Transaction, DeliveryType, DeliveryZone,
  Category, PaymentMethodRevenue, PaymentMethod, PAYMENT_METHODS, PAYMENT_METHOD_LABELS,
  PAYMENT_ICONS
} from '../../types';
import jsPDF from 'jspdf';
import { downloadExcel } from '../../utils/export';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

type Tab = 'overview' | 'sales' | 'inventory' | 'recipes' | 'employees' | 'transactions' | 'productsSales' | 'invoices' | 'dailyComparison' | 'deliveryTracking' | 'periodComparison' | 'taxReports';

interface EmployeeSalesData {
  employeeId: number;
  employeeName: string;
  orderCount: number;
  averageOrderValue: number;
  revenue: number;
}

interface RecipePerformance {
  recipeId: number;
  productName: string;
  productPrice: number;
  yieldQuantity: number;
  ingredientCount: number;
  isActive: boolean;
}

interface LowStockItem {
  name: string;
  currentQuantity: number;
  reorderLevel: number;
  unit: string;
  shortage: number;
}

/** Colored category pill shown beside a product name in report tables. */
function CategoryPill({ productName, productCategoryMap }: {
  productName: string;
  productCategoryMap: Map<string, { name: string; color: string }>;
}) {
  const cat = productCategoryMap.get(productName);
  if (!cat) return null;
  // Only 6-digit hex category colors get a color-tinted badge; anything else
  // (named colors, rgb(), missing) falls back to a neutral theme pill.
  const hex = cat.color && /^#[0-9a-fA-F]{6}$/.test(cat.color) ? cat.color : null;
  return (
    <span
      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium shrink-0 ${
        hex ? '' : 'bg-base-200/60 text-base-content/60'
      }`}
      style={hex ? { backgroundColor: `${hex}26`, color: hex } : undefined}
      title={cat.name}
    >
      {cat.name}
    </span>
  );
}

export default function Reports() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('sales');
  const [exporting, setExporting] = useState(false);
  // Date range filter for sales
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: '',
  });
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [zoneFilterId, setZoneFilterId] = useState<number | null>(null);
  const [orderTypeFilter, setOrderTypeFilter] = useState<string>('');
  const [comparisonFilter, setComparisonFilter] = useState<ComparisonFilter | null>(null);
  const [searchParams] = useSearchParams();

  // Clear comparison filter when switching tabs
  useEffect(() => {
    setComparisonFilter(null);
  }, [activeTab]);

  // Deep-link support: /reports?tab=taxReports opens the Tax Reports tab
  // (used by the sidebar / dashboard menu items).
  useEffect(() => {
    if (searchParams.get('tab') === 'taxReports') setActiveTab('taxReports');
  }, [searchParams]);

  // ── Data fetching via shared useApiQueries hook ──
  const {
    data: [
      settingsRes, analyticsRes, salesRes,
      ingredientsRes, invTxnsRes, recipesRes,
      productsRes, employeesRes,
      transactionsRes,
      deliveryTypesRes,
      deliveryZonesRes,
      paymentRevRes,
      categoriesRes,
    ],
    isLoading: loading,
  } = useApiQueries([
    { command: 'get_settings' },
    { command: 'get_analytics' },
    { command: 'get_sales' },
    { command: 'get_ingredients', params: { includeInactive: true } },
    { command: 'get_inventory_transactions', params: { ingredientId: null } },
    { command: 'get_recipes', params: { includeInactive: true } },
    { command: 'get_products' },
    { command: 'get_employees', params: { includeInactive: true } },
    { command: 'get_transactions' },
    { command: 'get_delivery_types', params: { includeInactive: true } },
    { command: 'get_delivery_zones', params: { includeInactive: true } },
    { command: 'get_revenue_by_payment_method' },
    { command: 'get_categories' },
  ]);

  const settings = (settingsRes as Settings | undefined) ?? null;
  const { formatPrice, currency } = useCurrency();
  const restaurantName = settings?.restaurant_name || 'Forge POS';
  const analytics = (analyticsRes as AnalyticsData | null) ?? null;
  const sales = (Array.isArray(salesRes) ? (salesRes as Sale[]) : []) as Sale[];
  const ingredients = (Array.isArray(ingredientsRes) ? (ingredientsRes as Ingredient[]) : []) as Ingredient[];
  const inventoryTxns = (Array.isArray(invTxnsRes) ? (invTxnsRes as InventoryTransaction[]) : []) as InventoryTransaction[];
  const recipes = (Array.isArray(recipesRes) ? (recipesRes as Recipe[]) : []) as Recipe[];
  const products = (Array.isArray(productsRes) ? (productsRes as Product[]) : []) as Product[];
  const employees = (Array.isArray(employeesRes) ? (employeesRes as Employee[]) : []) as Employee[];
  const transactions = (Array.isArray(transactionsRes) ? (transactionsRes as Transaction[]) : []) as Transaction[];
  const deliveryTypes = (Array.isArray(deliveryTypesRes) ? (deliveryTypesRes as DeliveryType[]) : []) as DeliveryType[];
  const deliveryZones = (Array.isArray(deliveryZonesRes) ? (deliveryZonesRes as DeliveryZone[]) : []) as DeliveryZone[];
  const paymentRevenue = (Array.isArray(paymentRevRes) ? (paymentRevRes as PaymentMethodRevenue[]) : []) as PaymentMethodRevenue[];
  const categories = (Array.isArray(categoriesRes) ? (categoriesRes as Category[]) : []) as Category[];

  // Product name → { category name, color } — used to color top products by
  // their category across the report tables (matches ProductManager's picker).
  const productCategoryMap = useMemo(() => {
    const catById = new Map(categories.map(c => [c.id, c]));
    const map = new Map<string, { name: string; color: string }>();
    for (const p of products) {
      if (p.category_id == null) continue;
      const cat = catById.get(p.category_id);
      if (cat) map.set(p.name, { name: cat.name, color: cat.color || '' });
    }
    return map;
  }, [categories, products]);

  // ---- Help Modal State ----
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);


  // ---- Derived Data ----

  // Filtered sales for date range
  const filteredSales = useMemo(() => {
    let filtered = sales;
    if (dateRange.start || dateRange.end) {
      filtered = filtered.filter(sale => {
        if (dateRange.start && sale.date < dateRange.start) return false;
        if (dateRange.end && sale.date > dateRange.end) return false;
        return true;
      });
    }
    if (zoneFilterId != null) {
      filtered = filtered.filter(sale => sale.delivery_zone_id === zoneFilterId);
    }
    if (orderTypeFilter) {
      filtered = filtered.filter(sale => sale.order_type?.toLowerCase() === orderTypeFilter.toLowerCase());
    }
    return filtered;
  }, [sales, dateRange, zoneFilterId, orderTypeFilter]);

  // Quick date presets
  const applyDatePreset = useCallback((preset: string) => {
    const now = new Date();
    const fmt = (d: Date) => d.toISOString().split('T')[0];
    switch (preset) {
      case 'today':
        setDateRange({ start: fmt(now), end: fmt(now) });
        setActivePreset('today');
        break;
      case '7d': {
        const d = new Date(now); d.setDate(d.getDate() - 7);
        setDateRange({ start: fmt(d), end: fmt(now) });
        setActivePreset('7d');
        break;
      }
      case '30d': {
        const d = new Date(now); d.setDate(d.getDate() - 30);
        setDateRange({ start: fmt(d), end: fmt(now) });
        setActivePreset('30d');
        break;
      }
      case 'month': {
        const d = new Date(now.getFullYear(), now.getMonth(), 1);
        setDateRange({ start: fmt(d), end: fmt(now) });
        setActivePreset('month');
        break;
      }
      case 'clear':
        setDateRange({ start: '', end: '' });
        setActivePreset(null);
        break;
    }
  }, []);

  // Order type breakdown from filtered sales
  const orderTypeBreakdown = useMemo(() => {
    const breakdown: Record<string, { count: number; revenue: number }> = {};
    for (const sale of filteredSales) {
      const type = sale.order_type || 'unknown';
      if (!breakdown[type]) breakdown[type] = { count: 0, revenue: 0 };
      breakdown[type].count++;
      breakdown[type].revenue += sale.total_amount || 0;
    }
    return Object.entries(breakdown).map(([type, data]) => ({
      type: type.charAt(0).toUpperCase() + type.slice(1),
      ...data,
      revenue: Number(data.revenue.toFixed(2)),
    }));
  }, [filteredSales]);

  const lowStockItems = useMemo((): LowStockItem[] => {
    return ingredients
      .filter(ing => ing.is_active && ing.current_quantity <= ing.reorder_level)
      .map(ing => ({
        name: ing.name,
        currentQuantity: ing.current_quantity,
        reorderLevel: ing.reorder_level,
        unit: ing.unit,
        shortage: ing.reorder_level - ing.current_quantity,
      }))
      .sort((a, b) => b.shortage - a.shortage);
  }, [ingredients]);

  // Stock value
  const stockValue = useMemo(() => {
    return ingredients
      .filter(ing => ing.is_active)
      .reduce((sum, ing) => sum + ing.current_quantity * ing.cost_per_unit, 0);
  }, [ingredients]);

  // Employee performance (uses filtered sales for consistency)
  const employeePerformance = useMemo((): EmployeeSalesData[] => {
    const empMap = new Map<number, { name: string; totalAmount: number; count: number }>();

    for (const sale of filteredSales) {
      const empId = sale.employee_id;
      if (!empId) continue;

      if (!empMap.has(empId)) {
        const emp = employees.find(e => e.id === empId);
        empMap.set(empId, {
          name: emp?.name || `Employee #${empId}`,
          totalAmount: 0,
          count: 0,
        });
      }
      const entry = empMap.get(empId)!;
      entry.totalAmount += sale.total_amount || 0;
      entry.count++;
    }

    return Array.from(empMap.entries())
      .map(([empId, data]) => ({
        employeeId: empId,
        employeeName: data.name,
        orderCount: data.count,
        averageOrderValue: data.count > 0 ? Number((data.totalAmount / data.count).toFixed(2)) : 0,
        revenue: Number(data.totalAmount.toFixed(2)),
      }))
      .sort((a, b) => b.revenue - a.revenue);
  }, [filteredSales, employees]);

  // Recipe performance
  const recipePerformance = useMemo((): RecipePerformance[] => {
    const productMap = new Map(products.map(p => [p.id, p]));
    return recipes
      .filter(r => r.is_active)
      .map(recipe => {
        const product = productMap.get(recipe.product_id);
        return {
          recipeId: recipe.id,
          productName: product?.name || `Product #${recipe.product_id}`,
          productPrice: product?.price || 0,
          yieldQuantity: recipe.yield_quantity,
          ingredientCount: 0, // Would need per-recipe DB queries
          isActive: recipe.is_active,
        };
      });
  }, [recipes, products]);

  // Recent inventory transactions for display
  const recentInventoryTxns = useMemo(() => {
    return inventoryTxns.slice(0, 10);
  }, [inventoryTxns]);

  // Ingredient map for transaction display
  const ingredientMap = useMemo(() => {
    const map = new Map<number, Ingredient>();
    for (const ing of ingredients) map.set(ing.id, ing);
    return map;
  }, [ingredients]);

  // Best selling category from product_distribution
  const bestSellingCategory = useMemo(() => {
    if (!analytics?.product_distribution || analytics.product_distribution.length === 0) {
      return t('reports.none');
    }
    const sorted = [...analytics.product_distribution].sort((a, b) => b.value - a.value);
    const top = sorted[0];
    return `${top.name} (${top.value} sold)`;
  }, [analytics, t]);

  // Average items per order from transactions
  const avgItemsPerOrder = useMemo(() => {
    if (transactions.length === 0) return '0.0';
    const totalItems = transactions.reduce((sum, tx) => sum + tx.items.length, 0);
    return (totalItems / transactions.length).toFixed(1);
  }, [transactions]);

  // ---- Tab Navigation ----
  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'overview' as Tab, label: 'Overview', icon: <span className="ri-dashboard-2-line ri-20px" /> },
    { key: 'sales' as Tab, label: 'Sales', icon: <span className="ri-money-dollar-box-line ri-20px" /> },
    { key: 'productsSales' as Tab, label: 'Products Sales', icon: <span className="ri-bar-chart-2-line ri-20px" /> },
    { key: 'invoices' as Tab, label: 'Invoices', icon: <span className="ri-receipt-line ri-20px" /> },
    { key: 'dailyComparison' as Tab, label: 'Daily Comparison', icon: <span className="ri-stock-line ri-20px" /> },
    { key: 'periodComparison' as Tab, label: 'Period Comparison', icon: <span className="ri-calendar-line ri-20px" /> },
    { key: 'deliveryTracking' as Tab, label: 'Delivery Tracking', icon: <span className="ri-store-2-line ri-20px" /> },
    { key: 'inventory' as Tab, label: 'Inventory', icon: <span className="ri-archive-line ri-20px" /> },
    { key: 'recipes' as Tab, label: 'Recipes', icon: <span className="ri-menu-2-line ri-20px" /> },
    { key: 'employees' as Tab, label: 'Employees', icon: <span className="ri-group-line ri-20px" /> },
    { key: 'transactions' as Tab, label: 'Transactions', icon: <span className="ri-calendar-line ri-20px" /> },
    { key: 'taxReports' as Tab, label: 'Tax Reports', icon: <span className="ri-bank-line ri-20px" /> },
  ];

  // ── Arrow-key tab nav ──
  const tabKeys: Tab[] = tabs.map(t => t.key);
  const { onKeyDown: onReportsTabKeyDown } = useKeyboardTabNav(tabKeys, activeTab, setActiveTab);

  // ---- Keyboard Shortcuts ----
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const key = e.key;
      const lower = key.toLowerCase();

      // '?' / '/' opens shortcut help
      if (key === '?' || key === '/') {
        e.preventDefault();
        setShowShortcutHelp(prev => !prev);
        return;
      }

      // Number keys for tab navigation
      const tabKeys: Tab[] = ['overview', 'sales', 'productsSales', 'invoices', 'dailyComparison', 'periodComparison', 'deliveryTracking', 'inventory', 'recipes', 'employees', 'transactions', 'taxReports'];
      const num = parseInt(key);
      if (num >= 1 && num <= 9 && num <= tabKeys.length) {
        setActiveTab(tabKeys[num - 1]);
        return;
      }
      if (key === '0') { setActiveTab('employees'); return; }
      if (key === '-') { setActiveTab('transactions'); return; }

      // Date presets
      if (lower === 't') { applyDatePreset('today'); return; }
      if (lower === 'w') { applyDatePreset('7d'); return; }
      if (lower === 'm') { applyDatePreset('30d'); return; }
      if (lower === 'r') { applyDatePreset('month'); return; }
      if (lower === 'c') { applyDatePreset('clear'); return; }

      // Export
      if (lower === 'p') { e.preventDefault(); exportPDF(); return; }
      if (lower === 's') {
        e.preventDefault();
        const csvHandlers: Record<string, () => void> = {
          sales: handleExportSalesCSV,
          productsSales: handleExportProductsSalesCSV,
          invoices: handleExportInvoicesCSV,
          inventory: handleExportInventoryCSV,
          recipes: handleExportRecipesCSV,
          employees: handleExportEmployeesCSV,
          transactions: handleExportTransactionsCSV,
          deliveryTracking: handleExportDeliveryCSV,
        };
        csvHandlers[activeTab]?.();
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, applyDatePreset]);

  // ---- Daily Sales Comparison ----

  // ── Shared delta computations ──
  const {
    delta,
    todayStats,
    yesterdayStats,
    lastWeekStats,
    dailyTrend,
    revDelta,
    orderDelta,
    wkRevDelta,
    wkOrderDelta,
    periodView,
    setPeriodView,
    currentStats,
    previousStats,
    periodRevDelta,
    periodOrderDelta,
    salesRevDelta,
    salesOrderDelta,
    salesAvgDelta,
    periodTrend,
    todayStr,
    yesterdayStr,
    thisWeekStart,
    currentMonthStart,
    salesByDate,
    last30Start,
    last30End,
    prior30Start,
    prior30End,
    prevWeekStart,
    prevWeekEnd,
    prevMonthStart,
    prevMonthEnd,
  } = useDashboardDeltas(sales);

  // ---- Employee Daily Breakdown ----
  const employeeDailyStats = useMemo(() => {
    if (employees.length === 0) return [];

    // Group sales by date for quick lookup
    const todaySales = salesByDate.get(todayStr) || [];
    const yesterdaySales = salesByDate.get(yesterdayStr) || [];

    // Build per-employee maps
    const todayMap = new Map<number, { orders: number; revenue: number }>();
    for (const sale of todaySales) {
      if (!sale.employee_id) continue;
      const entry = todayMap.get(sale.employee_id) || { orders: 0, revenue: 0 };
      entry.orders++;
      entry.revenue += sale.total_amount;
      todayMap.set(sale.employee_id, entry);
    }

    const yesterdayMap = new Map<number, { orders: number; revenue: number }>();
    for (const sale of yesterdaySales) {
      if (!sale.employee_id) continue;
      const entry = yesterdayMap.get(sale.employee_id) || { orders: 0, revenue: 0 };
      entry.orders++;
      entry.revenue += sale.total_amount;
      yesterdayMap.set(sale.employee_id, entry);
    }

    // Merge into result array, sorted by today's revenue descending
    const result = employees
      .filter(e => e.is_active)
      .map(emp => {
        const today = todayMap.get(emp.id) || { orders: 0, revenue: 0 };
        const yesterday = yesterdayMap.get(emp.id) || { orders: 0, revenue: 0 };
        const orderDelta = delta(today.orders, yesterday.orders);
        const revDelta = delta(today.revenue, yesterday.revenue);
        return {
          id: emp.id,
          name: emp.name,
          todayOrders: today.orders,
          todayRevenue: today.revenue,
          yesterdayOrders: yesterday.orders,
          yesterdayRevenue: yesterday.revenue,
          orderChange: orderDelta.pct,
          orderDirection: orderDelta.direction,
          orderColor: orderDelta.color,
          revChange: revDelta.pct,
          revDirection: revDelta.direction,
          revColor: revDelta.color,
        };
      })
      .sort((a, b) => b.todayRevenue - a.todayRevenue);

    return result;
  }, [employees, salesByDate, todayStr, yesterdayStr]);

  // ---- Delivery Tracking ----
  // Build a lookup map for delivery type names
  const deliveryTypeMap = useMemo(() => {
    const map = new Map<number, string>();
    for (const dt of deliveryTypes) map.set(dt.id, dt.name);
    return map;
  }, [deliveryTypes]);

  // Delivery zone lookup map
  const deliveryZoneMap = useMemo(() => {
    const map = new Map<number, string>();
    for (const z of deliveryZones) map.set(z.id, z.name);
    return map;
  }, [deliveryZones]);

  // Filter sales by delivery order_type and optionally by date range
  const deliverySales = useMemo(() => {
    return sales.filter(s => s.order_type?.toLowerCase() === 'delivery');
  }, [sales]);

  const filteredDeliverySales = useMemo(() => {
    if (!dateRange.start && !dateRange.end) return deliverySales;
    return deliverySales.filter(s => {
      if (dateRange.start && s.date < dateRange.start) return false;
      if (dateRange.end && s.date > dateRange.end) return false;
      return true;
    });
  }, [deliverySales, dateRange]);

  // Aggregate delivery stats
  const deliveryStats = useMemo(() => {
    const totalOrders = filteredDeliverySales.length;
    const totalRevenue = filteredDeliverySales.reduce((s, sale) => s + sale.total_amount, 0);
    const avgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
    const completedOrders = filteredDeliverySales.filter(s => s.status === 'completed').length;
    const pendingOrders = filteredDeliverySales.filter(s => s.status !== 'completed').length;
    const withAddress = filteredDeliverySales.filter(s => s.delivery_address).length;
    return { totalOrders, totalRevenue, avgOrderValue, completedOrders, pendingOrders, withAddress };
  }, [filteredDeliverySales]);

  // ---- PDF Export ----
  const exportPDF = async () => {
    setExporting(true);
    try {
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      let y = 20;

      // Helper
      const addSection = (title: string) => {
        if (y > 260) { doc.addPage(); y = 20; }
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text(title, 14, y);
        y += 10;
        doc.setDrawColor(100, 100, 100);
        doc.line(14, y, pageWidth - 14, y);
        y += 8;
      };

      const addText = (label: string, value: string) => {
        if (y > 270) { doc.addPage(); y = 20; }
        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        doc.text(`${label}: ${value}`, 20, y);
        y += 7;
      };

      // Title
      doc.setFontSize(22);
      doc.setFont('helvetica', 'bold');
      doc.text(restaurantName, pageWidth / 2, y, { align: 'center' });
      y += 12;
      doc.setFontSize(14);
      doc.setFont('helvetica', 'normal');
      doc.text('Comprehensive Report', pageWidth / 2, y, { align: 'center' });
      y += 8;
      doc.setFontSize(10);
      doc.text(`Generated: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`, pageWidth / 2, y, { align: 'center' });
      y += 15;

      // Sales Summary
      if (analytics?.summary) {
        addSection('Sales Summary');
        addText('Total Revenue', `${formatPrice(analytics.summary.total_revenue)}`);
        addText('Total Orders', analytics.summary.total_orders.toString());
        addText('Average Order Value', `${formatPrice(analytics.summary.average_order_value)}`);
        y += 5;
      }

      // Order Type Breakdown
      addSection('Orders by Type');
      orderTypeBreakdown.forEach(ot => {
        addText(ot.type, `${ot.count} orders · ${formatPrice(ot.revenue)}`);
      });
      y += 5;

      // Top Products
      if (analytics?.top_products && analytics.top_products.length > 0) {
        addSection('Top Products');
        const topSlice = analytics.top_products.slice(0, 5);
        topSlice.forEach((p, i) => {
          addText(`#${i + 1} ${p.name}`, `${p.sales} sold · ${formatPrice(p.revenue)}`);
        });
        y += 5;
      }

      // Low Stock Alert
      if (lowStockItems.length > 0) {
        addSection('Low Stock Alerts');
        lowStockItems.slice(0, 5).forEach(item => {
          addText(
            item.name,
            `${item.currentQuantity} / ${item.reorderLevel} ${item.unit} (need ${item.shortage})`
          );
        });
        y += 5;
      }

      // Inventory Summary
      addSection('Inventory Summary');
      addText('Total Stock Value', `${formatPrice(stockValue)}`);
      addText('Active Ingredients', ingredients.filter(i => i.is_active).length.toString());
      addText('Low Stock Items', lowStockItems.length.toString());
      y += 5;

      // Employee Performance
      if (employeePerformance.length > 0) {
        addSection('Employee Performance');
        employeePerformance.slice(0, 5).forEach((emp, i) => {
          addText(
            `#${i + 1} ${emp.employeeName}`,
            `${emp.orderCount} orders · ${formatPrice(emp.revenue)}`
          );
        });
        y += 5;
      }

      // Footer
      const dateStr = new Date().toLocaleDateString();
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.text(
        `Report generated on ${dateStr} · ${restaurantName}`,
        pageWidth / 2,
        doc.internal.pageSize.getHeight() - 10,
        { align: 'center' }
      );

      doc.save(`report-${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (error) {
      console.error('Error exporting PDF:', error);
    } finally {
      setExporting(false);
    }
  };

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

  const handleExportSalesCSV = () => {
    downloadCSV(
      `sales-${new Date().toISOString().split('T')[0]}.csv`,
      ['Date', 'Time', 'Order Type', 'Status', 'Total Amount', 'Currency', 'Table'],
      filteredSales.map(s => [
        s.date || '', s.time || '', s.order_type || '', s.status || '',
        s.total_amount.toFixed(2), s.currency || currency,
        s.table_number ? String(s.table_number) : ''
      ])
    );
  };

  const handleExportInventoryCSV = () => {
    downloadCSV(
      `inventory-${new Date().toISOString().split('T')[0]}.csv`,
      ['Ingredient', 'Quantity', 'Unit', 'Cost/Unit', 'Total Value', 'Status'],
      ingredients.filter(i => i.is_active).map(ing => [
        ing.name, String(ing.current_quantity), ing.unit,
        ing.cost_per_unit.toFixed(2),
        (ing.current_quantity * ing.cost_per_unit).toFixed(2),
        ing.current_quantity <= ing.reorder_level ? 'Low Stock' : 'In Stock'
      ])
    );
  };

  const handleExportRecipesCSV = () => {
    downloadCSV(
      `recipes-${new Date().toISOString().split('T')[0]}.csv`,
      ['Product', 'Price', 'Yield', 'Status'],
      recipePerformance.map(rp => [
        rp.productName, rp.productPrice.toFixed(2),
        String(rp.yieldQuantity), rp.isActive ? 'Active' : 'Inactive'
      ])
    );
  };

  const handleExportProductsSalesCSV = () => {
    const totalRev = analytics?.summary?.total_revenue ?? 0;
    downloadCSV(
      `product-sales-${new Date().toISOString().split('T')[0]}.csv`,
      ['Product', 'Sold', 'Revenue', 'Share'],
      (analytics?.top_products || []).map(p => [
        p.name, String(p.sales), p.revenue.toFixed(2),
        totalRev > 0
          ? `${((p.revenue / totalRev) * 100).toFixed(1)}%`
          : '0%'
      ])
    );
  };

  const handleExportDeliveryCSV = () => {
    downloadCSV(
      `deliveries-${new Date().toISOString().split('T')[0]}.csv`,
      ['Invoice #', 'Date', 'Time', 'Status', 'Zone', 'Delivery Address', 'Delivery Type', 'Amount', 'Currency', 'Employee'],
      filteredDeliverySales.map(s => {
        const dtName = s.delivery_type_id ? deliveryTypeMap.get(s.delivery_type_id) : null;
        const zoneName = s.delivery_zone_id ? deliveryZoneMap.get(s.delivery_zone_id) : null;
        const emp = employees.find(e => e.id === s.employee_id);
        return [
          String(s.id), s.date || '', s.time || '', s.status || '',
          zoneName || '', s.delivery_address || '', dtName || '',
          s.total_amount.toFixed(2), s.currency || currency, emp?.name || ''
        ];
      })
    );
  };

  const handleExportInvoicesCSV = () => {
    downloadCSV(
      `invoices-${new Date().toISOString().split('T')[0]}.csv`,
      ['Invoice #', 'Date', 'Time', 'Order Type', 'Status', 'Amount', 'Currency', 'Employee'],
      filteredSales.map(s => {
        const emp = employees.find(e => e.id === s.employee_id);
        return [
          String(s.id), s.date || '', s.time || '', s.order_type || '', s.status || '',
          s.total_amount.toFixed(2), s.currency || currency, emp?.name || ''
        ];
      })
    );
  };

  const handleExportTransactionsCSV = () => {
    downloadCSV(
      `transactions-${new Date().toISOString().split('T')[0]}.csv`,
      ['Date', 'Time', 'Items', 'Total'],
      transactions.map(tx => [
        tx.date || '', tx.time || '',
        tx.items.map(i => i.name).join('; '),
        `${tx.currency} ${tx.total_amount.toFixed(2)}`
      ])
    );
  };

  const handleExportEmployeesCSV = () => {
    downloadCSV(
      `employees-${new Date().toISOString().split('T')[0]}.csv`,
      ['Employee', 'Orders', 'Revenue', 'Avg. Order Value'],
      employeePerformance.map(emp => [
        emp.employeeName, String(emp.orderCount),
        emp.revenue.toFixed(2), emp.averageOrderValue.toFixed(2)
      ])
    );
  };

  // ---- Excel Export ----
  const handleExportExcel = async () => {
    setExporting(true);
    try {
      const date = new Date().toISOString().split('T')[0];
      const columns = [
        { header: 'Date', key: 'date' },
        { header: 'Time', key: 'time' },
        { header: 'Order Type', key: 'order_type' },
        { header: 'Status', key: 'status' },
        { header: 'Total Amount', key: 'total_amount' },
        { header: 'Currency', key: 'currency' },
        { header: 'Table', key: 'table_number' },
      ];
      await downloadExcel(
        `sales-report-${date}.xlsx`,
        'Sales',
        columns,
        filteredSales.map(s => ({
          date: s.date || '',
          time: s.time || '',
          order_type: s.order_type || '',
          status: s.status || '',
          total_amount: s.total_amount.toFixed(2),
          currency: s.currency || currency,
          table_number: s.table_number ?? '',
        }))
      );
    } catch (error) {
      console.error('Error exporting Excel:', error);
    } finally {
      setExporting(false);
    }
  };


  if (loading) {
    return (
      <PageLayout title={t('reports.title')}>
        <div className="space-y-6">
          <SkeletonCard count={4} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SkeletonTable rows={5} columns={4} />
            <SkeletonTable rows={5} columns={3} />
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title={t('reports.title')}
      background="bg-linear-to-br from-base-200 via-primary/10 to-base-200"
      padding="py-10"
    >
      {/* Export Buttons — FlyonUI btn variants */}
      <div className="flex justify-end gap-2 mb-4">
        <button
          onClick={handleExportExcel}
          disabled={exporting}
          className="btn btn-success gap-1.5"
        >
          {exporting ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            <span className="ri-download-line ri-16px" />
          )}
          {exporting ? t('reports.exporting') : t('reports.exportExcel')}
        </button>
        <button
          onClick={exportPDF}
          disabled={exporting}
          className="btn btn-error gap-1.5"
        >
          {exporting ? (
            <span className="loading loading-spinner loading-sm" />
          ) : (
            <span className="ri-file-pdf-line ri-16px" />
          )}
          {exporting ? t('reports.exporting') : t('reports.exportPDF')}
        </button>
      </div>

        {/* Active Date Range Indicator */}
        {(dateRange.start || dateRange.end) && (
          <div className="text-center mb-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium
              bg-info/10 text-info">
              <span className="ri-calendar-line ri-14px" />
              {t('reports.showingDataFrom', { start: dateRange.start || t('reports.dateEarliest'), end: dateRange.end || t('reports.dateLatest') })}
            </span>
          </div>
        )}

        {/* Filter Row: Order Type + Delivery Zone */}
        <Card className="mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {/* Order Type Filter */}
            <div className="flex items-center gap-2 shrink-0">
              <span className="ri-store-2-line ri-20px text-info" />
              <span className="text-sm font-semibold text-base-content">{t('reports.orderType', 'Order Type')}</span>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={orderTypeFilter}
                onChange={e => setOrderTypeFilter(e.target.value)}
                className="select text-xs w-36"
              >
                <option value="">{t('reports.allTypes', 'All Types')}</option>
                <option value="dine-in">{t('reports.dineIn', 'Dine-in')}</option>
                <option value="takeaway">{t('reports.takeaway', 'Takeaway')}</option>
                <option value="delivery">{t('reports.delivery', 'Delivery')}</option>
              </select>
              {orderTypeFilter && (
                <button onClick={() => setOrderTypeFilter('')}
                  className="text-xs text-error hover:text-error/70 transition-colors shrink-0">
                  {t('reports.dateClear', 'Clear')}
                </button>
              )}
            </div>

            <div className="hidden sm:block w-px h-6 bg-base-300/50" />

            {/* Delivery Zone Filter */}
            <div className="flex items-center gap-2 shrink-0">
              <span className="ri-map-pin-2-line ri-20px text-warning" />
              <span className="text-sm font-semibold text-base-content">{t('reports.zone', 'Delivery Zone')}</span>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={zoneFilterId ?? ''}
                onChange={e => setZoneFilterId(e.target.value ? Number(e.target.value) : null)}
                className="select text-xs w-40"
              >
                <option value="">{t('reports.allZones', 'All Zones')}</option>
                {deliveryZones.filter(z => z.is_active).map(z => (
                  <option key={z.id} value={z.id}>{z.name}</option>
                ))}
              </select>
              {zoneFilterId != null && (
                <button onClick={() => setZoneFilterId(null)}
                  className="text-xs text-error hover:text-error/70 transition-colors shrink-0">
                  {t('reports.dateClear', 'Clear')}
                </button>
              )}
            </div>
          </div>
        </Card>

        {/* Global Date Range Filter */}
        <Card className="mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="flex items-center gap-2 shrink-0">
              <span className="ri-calendar-line ri-20px text-info" />
              <span className="text-sm font-semibold text-base-content">{t('common.period')}</span>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <button onClick={() => applyDatePreset('today')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === 'today'
                    ? 'bg-info text-info-content' : 'bg-base-100/50 text-base-content/70 hover:bg-info/10 dark:hover:bg-info/30'
                }`}>{t('reports.dateToday')}</button>
              <button onClick={() => applyDatePreset('7d')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === '7d'
                    ? 'bg-info text-info-content' : 'bg-base-100/50 text-base-content/70 hover:bg-info/10 dark:hover:bg-info/30'
                }`}>{t('reports.date7Days')}</button>
              <button onClick={() => applyDatePreset('30d')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === '30d'
                    ? 'bg-info text-info-content' : 'bg-base-100/50 text-base-content/70 hover:bg-info/10 dark:hover:bg-info/30'
                }`}>{t('reports.date30Days')}</button>
              <button onClick={() => applyDatePreset('month')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === 'month'
                    ? 'bg-info text-info-content' : 'bg-base-100/50 text-base-content/70 hover:bg-info/10 dark:hover:bg-info/30'
                }`}>{t('reports.dateThisMonth')}</button>
            </div>
            <div className="flex items-center gap-2 flex-1 sm:justify-end">
              <input type="date" value={dateRange.start}
                onChange={e => setDateRange(prev => ({ ...prev, start: e.target.value }))}className="select text-base-content text-xs w-36" />
              <span className="text-base-content/40 text-xs">{t('reports.dateTo')}</span>
              <input type="date" value={dateRange.end}
                onChange={e => setDateRange(prev => ({ ...prev, end: e.target.value }))}className="select text-base-content text-xs w-36" />
              {(dateRange.start || dateRange.end) && (
                <button onClick={() => applyDatePreset('clear')}
                  className="text-xs text-error hover:text-error/70 transition-colors shrink-0">
                  {t('reports.dateClear')}
                </button>
              )}
            </div>
          </div>
        </Card>

        {/* Tab Navigation */}
        <nav className="tabs tabs-boxed gap-1 mb-8 overflow-x-auto" aria-label={t('reports.tabsLabel') || 'Report tabs'} role="tablist" data-tab-prefix="reports-tab" onKeyDown={onReportsTabKeyDown}>
          {tabs.map(tab => (
            <button
              key={tab.key}
              type="button"
              role="tab"
              id={`reports-tab-${tab.key}`}
              aria-controls={`reports-panel-${tab.key}`}
              aria-selected={activeTab === tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`tab ${activeTab === tab.key ? 'tab-active' : ''}`}
            >
              {tab.icon}
              <span className="text-sm sm:text-base">{t('reports.' + tab.key)}</span>
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <div
          key={activeTab}
          role="tabpanel"
          id={`reports-panel-${activeTab}`}
          aria-labelledby={`reports-tab-${activeTab}`}
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Cross-section KPI Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.totalOrders')}
                  value={filteredSales.length.toString()}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                 compact/><StatCard 
                  title={t('reports.stockValueLabel')}
                  value={`${formatPrice(stockValue)}`}
                  icon={<span className="ri-archive-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.activeRecipes')}
                  value={recipes.filter(r => r.is_active).length.toString()}
                  icon={<span className="ri-menu-2-line ri-24px" />}
                  color="warning"
                 compact/><StatCard 
                  title={t('reports.activeEmployees')}
                  value={employees.filter(e => e.is_active).length.toString()}
                  icon={<span className="ri-group-line ri-24px" />}
                  color="secondary"
                compact
                />
              </div>

              {/* Revenue Trend Chart */}
              {analytics?.daily_revenue && analytics.daily_revenue.length > 0 && (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.revenueTrend')}</h3>
                  <div className="w-full h-64" dir="ltr">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analytics.daily_revenue.slice(-30)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.15)" />
                        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <Tooltip
                          contentStyle={{
                            background: 'rgba(15,23,42,0.9)',
                            border: 'none',
                            borderRadius: '8px',
                            color: '#fff',
                          }}
                        />
                        <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2}
                          dot={{ r: 3, fill: '#6366f1' }} activeDot={{ r: 5 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              )}

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4">
                <StatCard title={t('reports.lowStockItems')}
                  value={lowStockItems.length}
                  desc={t('reports.needReordering')}
                  color="error" border animated={false} compact />
                <StatCard title={t('reports.orderTypes')}
                  value={orderTypeBreakdown.length}
                  desc={orderTypeBreakdown.map(o => o.type).join(', ') || t('reports.none')}
                  color="info" border animated={false} compact />
                <StatCard title={t('reports.products')}
                  value={products.length}
                  desc={t('reports.haveRecipes', { count: products.filter(p => recipes.some(r => r.product_id === p.id && r.is_active)).length })}
                  color="success" border animated={false} compact />
                <StatCard title={t('reports.monthlySalary')}
                  value={`${formatPrice(employees.filter(e => e.is_active).reduce((s, e) => s + e.salary, 0))}`}
                  desc={t('reports.activeEmployeesCount', { count: employees.filter(e => e.is_active).length })}
                  color="warning" border animated={false} compact />
              </div>
            </div>
          )}

          {activeTab === 'sales' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4">                <StatCard 
                  title={t('reports.totalRevenue')}
                  value={formatPrice(analytics?.summary?.total_revenue || 0)}
                  desc={`${salesRevDelta.direction === 'up' ? '▲' : salesRevDelta.direction === 'down' ? '▼' : '→'} ${salesRevDelta.pct} vs prev 30 days`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                  onDescClick={() => setComparisonFilter({ label: 'Last 30 Days vs Previous 30', periodALabel: 'Last 30 Days', periodBLabel: 'Previous 30', startA: last30Start, endA: last30End, startB: prior30Start, endB: prior30End })}
                 compact/><StatCard 
                  title={t('reports.totalOrders')}
                  value={(filteredSales.length).toString()}
                  desc={`${salesOrderDelta.direction === 'up' ? '▲' : salesOrderDelta.direction === 'down' ? '▼' : '→'} ${salesOrderDelta.pct} vs prev 30 days`}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="info"
                  onDescClick={() => setComparisonFilter({ label: 'Last 30 Days vs Previous 30', periodALabel: 'Last 30 Days', periodBLabel: 'Previous 30', startA: last30Start, endA: last30End, startB: prior30Start, endB: prior30End })}
                 compact/><StatCard 
                  title={t('reports.avgOrderValue')}
                  value={`${formatPrice(analytics?.summary.average_order_value || 0)}`}
                  desc={`${salesAvgDelta.direction === 'up' ? '▲' : salesAvgDelta.direction === 'down' ? '▼' : '→'} Avg ${salesAvgDelta.pct} vs prev 30 days`}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                  onDescClick={() => setComparisonFilter({ label: 'Last 30 Days vs Previous 30', periodALabel: 'Last 30 Days', periodBLabel: 'Previous 30', startA: last30Start, endA: last30End, startB: prior30Start, endB: prior30End })}
                 compact/><StatCard 
                  title={t('reports.orderTypes')}
                  value={orderTypeBreakdown.length.toString()}
                  icon={<span className="ri-store-2-line ri-24px" />}
                  color="warning"
                compact
                />
              </div>

              {comparisonFilter && (
                <ComparisonTable
                  sales={sales}
                  filter={comparisonFilter}
                  currency={currency}
                  onDismiss={() => setComparisonFilter(null)}
                />
              )}

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportSalesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Order Type Breakdown — Cards + Pie Chart */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Cards */}
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.ordersByType')}</h3>
                  {orderTypeBreakdown.length > 0 ? (
                    <div className="space-y-3">
                      {orderTypeBreakdown.map(ot => {
                        const colors: Record<string, string> = {
                          'Dine-in': 'bg-success/20 text-success border-success/30',
                          'Takeaway': 'bg-info/20 text-info border-info/30',
                        };
                        const fallbackColor = 'bg-warning/10 text-warning border-warning/30';
                        const colorClass = colors[ot.type] || fallbackColor;
                        return (
                          <div key={ot.type} className={`flex items-center gap-4 p-4 rounded-lg border ${colorClass}`}>
                            <div className={`p-3 rounded-lg ${colorClass}`}>
                              <span className="ri-store-2-line ri-20px" />
                            </div>
                            <div className="flex-1">
                              <p className="text-sm text-base-content/50">{ot.type}</p>
                              <p className="text-lg font-bold text-base-content">{t('reports.ordersCount', { count: ot.count })}</p>
                              <p className="text-sm text-base-content/70">{formatPrice(ot.revenue)}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-base-content/50">{t('reports.noOrderData')}</p>
                  )}
                </Card>

                {/* Pie Chart */}
                {orderTypeBreakdown.length > 0 && (
                  <Card padding="xl">
                    <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.orderDistribution')}</h3>
                    <div className="w-full h-72" dir="ltr">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={orderTypeBreakdown}
                            dataKey="count"
                            nameKey="type"
                            cx="50%"
                            cy="45%"
                            outerRadius={90}
                            innerRadius={50}
                            paddingAngle={4}
                            label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                          >
                            {orderTypeBreakdown.map((_, i) => (
                              <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                            formatter={(value: number, name: string) => [`${value} orders`, name]}
                          />
                          <Legend verticalAlign="bottom" />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </Card>
                )}
              </div>

              {/* Revenue by Payment Method — breakdown of totals by how customers paid */}
              {paymentRevenue.length > 0 && (
                <Card padding="xl">
                  {(() => {
                    const paymentTotal = paymentRevenue.reduce((s, p) => s + p.revenue, 0);
                    return (
                      <>
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-bold text-base-content flex items-center gap-2">
                            <span className="ri-bank-card-line ri-20px text-primary" />
                            {t('reports.revenueByPayment')}
                          </h3>
                          <span className="tag tag--sm tag--ghost">
                            {t('reports.totalRevenue')}: {formatPrice(paymentTotal)}
                          </span>
                        </div>
                        <div className="space-y-4">
                          {paymentRevenue.map(pr => {
                            const method = (PAYMENT_METHODS as string[]).includes(pr.payment_method)
                              ? (pr.payment_method as PaymentMethod)
                              : 'other';
                            const pct = paymentTotal > 0 ? (pr.revenue / paymentTotal) * 100 : 0;
                            return (
                              <div key={pr.payment_method} className="flex items-center gap-4">
                                <div className="w-9 h-9 shrink-0 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80 flex items-center justify-center">
                                  <span className={`${PAYMENT_ICONS[method]} ri-18px`} />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center justify-between gap-2 mb-1">
                                    <p className="text-sm font-medium text-base-content truncate">
                                      {t(`payments.${pr.payment_method}`, PAYMENT_METHOD_LABELS[method] || pr.payment_method)}
                                    </p>
                                    <p className="text-sm font-semibold text-base-content tabular-nums shrink-0">
                                      {formatPrice(pr.revenue)}
                                    </p>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <div className="flex-1 h-1.5 rounded-full bg-base-200 dark:bg-base-300/40 overflow-hidden">
                                      <div
                                        className="h-full rounded-full bg-primary/70 dark:bg-primary/60 transition-all duration-500"
                                        style={{ width: `${pct}%` }}
                                      />
                                    </div>
                                    <span className="text-[11px] text-base-content/50 tabular-nums shrink-0 w-16 text-right">
                                      {pct.toFixed(0)}% · {pr.orders} {t('reports.ordersShort')}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </>
                    );
                  })()}
                </Card>
              )}

              {/* Top Products */}
              {analytics?.top_products && analytics.top_products.length > 0 && (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.topProducts')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">#</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableSold')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.top_products.map((p, i) => (
                          <tr key={i} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 text-base-content/50">{i + 1}</td>
                            <td className="py-3 px-4">
                              <span className="flex items-center gap-2 min-w-0">
                                <span className="font-medium text-base-content truncate">{p.name}</span>
                                <CategoryPill productName={p.name} productCategoryMap={productCategoryMap} />
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right text-base-content">{p.sales}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(p.revenue)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              )}

              {/* Revenue Trend Chart */}
              {analytics?.daily_revenue && analytics.daily_revenue.length > 0 && (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">Revenue Trend</h3>
                  <div className="w-full h-72" dir="ltr">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analytics.daily_revenue.slice(-30)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.15)" />
                        <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <Tooltip
                          contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2}
                          dot={{ r: 3, fill: '#6366f1' }} activeDot={{ r: 5 }} name="Revenue" />
                        <Line type="monotone" dataKey="orders" stroke="#10b981" strokeWidth={2}
                          dot={{ r: 3, fill: '#10b981' }} activeDot={{ r: 5 }} name="Orders" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'productsSales' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.totalProductsSold')}
                  value={analytics?.summary?.total_orders?.toString() || '0'}
                  icon={<span className="ri-bar-chart-2-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.productRevenue')}
                  value={formatPrice(analytics?.summary?.total_revenue || 0)}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                 compact/><StatCard 
                  title={t('reports.bestSellingCategory')}
                  value={bestSellingCategory}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="warning"
                 compact/><StatCard 
                  title={t('reports.avgItemsPerOrder')}
                  value={avgItemsPerOrder}
                  icon={<span className="ri-store-2-line ri-24px" />}
                  color="secondary"
                compact
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportProductsSalesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Product Performance Table */}
              {analytics?.top_products && analytics.top_products.length > 0 ? (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.productsSalesBreakdown')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">#</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableSold')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableShare')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.top_products.map((p, i) => {
                          const maxRevenue = Math.max(...analytics.top_products.map(x => x.revenue));
                          const share = maxRevenue > 0 ? (p.revenue / maxRevenue) * 100 : 0;
                          return (
                            <tr key={i} className="border-b border-base-300/50 hover:bg-base-100/50">
                              <td className="py-3 px-4 text-base-content/50">{i + 1}</td>
                              <td className="py-3 px-4">
                                <span className="flex items-center gap-2 min-w-0">
                                  <span className="font-medium text-base-content truncate">{p.name}</span>
                                  <CategoryPill productName={p.name} productCategoryMap={productCategoryMap} />
                                </span>
                              </td>
                              <td className="py-3 px-4 text-right text-base-content">{p.sales}</td>
                              <td className="py-3 px-4 text-right text-base-content">{formatPrice(p.revenue)}</td>
                              <td className="py-3 px-4">
                                <div className="flex items-center gap-2">
                                  <div className="w-20 bg-base-300 rounded-full h-2 overflow-hidden">
                                    <div
                                      className="h-full rounded-full bg-linear-to-r from-primary to-secondary"
                                      style={{ width: `${Math.min(share, 100)}%` }}
                                    />
                                  </div>
                                  <span className="text-xs text-base-content/50">{p.revenue > 0 ? `${((p.revenue / (analytics?.summary?.total_revenue || 1)) * 100).toFixed(1)}%` : '0%'}</span>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </Card>
              ) : (
                <Card padding="xl" center>
                  <span className="ri-bar-chart-2-line ri-48px mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 text-lg mb-2">{t('reports.noProductSales')}</p>
                  <p className="text-base-content/50">{t('reports.noProductSalesHint')}</p>
                </Card>
              )}

              {/* Revenue Distribution Bar Chart */}
              {analytics?.product_distribution && analytics.product_distribution.length > 0 && (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.productDistribution')}</h3>
                  <div className="w-full h-72" dir="ltr">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analytics.product_distribution} margin={{ left: 20, right: 20, top: 10, bottom: 60 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" vertical={false} />
                        <XAxis dataKey="name" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" angle={-30} textAnchor="end" height={70} interval={0} />
                        <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <Tooltip
                          contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                          formatter={(value: number) => [`${value}`, 'Sold']}
                        />
                        <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={40} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'invoices' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.totalInvoices')}
                  value={filteredSales.length.toString()}
                  icon={<span className="ri-receipt-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.totalRevenue')}
                  value={formatPrice(filteredSales.reduce((s, s2) => s + s2.total_amount, 0))}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                 compact/><StatCard 
                  title={t('reports.avgOrderValue')}
                  value={filteredSales.length > 0 ? formatPrice(filteredSales.reduce((s, s2) => s + s2.total_amount, 0) / filteredSales.length) : formatPrice(0)}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                 compact/><StatCard 
                  title={t('reports.completedOrders')}
                  value={filteredSales.filter(s => s.status === 'completed').length.toString()}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="success"
                compact
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportInvoicesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Invoices Table */}
              {filteredSales.length > 0 ? (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.invoiceList')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableInvoice')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableDate')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableTime')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableOrderType')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableStatus')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableAmount')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableEmployee')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredSales.map(sale => {
                          const emp = employees.find(e => e.id === sale.employee_id);
                          return (
                            <tr key={sale.id} className="border-b border-base-300/50 hover:bg-base-100/50">
                              <td className="py-3 px-4 font-medium text-base-content">#{sale.id}</td>
                              <td className="py-3 px-4 text-base-content/70">{sale.date}</td>
                              <td className="py-3 px-4 text-base-content/70">{sale.time}</td>
                              <td className="py-3 px-4">
                                <Badge className="bg-info/10 text-info capitalize">
                                  {sale.order_type || '-'}
                                </Badge>
                              </td>
                              <td className="py-3 px-4">
                                <Badge className={`${sale.status === 'completed' ? 'bg-success/20 text-success' : sale.status === 'cancelled' ? 'bg-error/20 text-error' : 'bg-warning/20 text-warning'}`}>
                                  {sale.status}
                                </Badge>
                              </td>
                              <td className="py-3 px-4 text-right font-bold text-base-content">{formatPrice(sale.total_amount)}</td>
                              <td className="py-3 px-4 text-base-content/70">{emp?.name || '-'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </Card>
              ) : (
                <Card padding="xl" center>
                  <span className="ri-receipt-line ri-48px mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 text-lg mb-2">{t('reports.noInvoices')}</p>
                  <p className="text-base-content/50">{t('reports.noInvoicesHint')}</p>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'dailyComparison' && (
            <div className="space-y-6">
              {/* Today's Overview Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.todayRevenue')}
                  value={`${formatPrice(todayStats.revenue)}`}
                  desc={`${revDelta.direction === 'up' ? '▲' : revDelta.direction === 'down' ? '▼' : '→'} ${revDelta.pct} vs yesterday`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                  onDescClick={() => setComparisonFilter({ label: 'Today vs Yesterday', periodALabel: 'Today', periodBLabel: 'Yesterday', startA: todayStr, endA: todayStr, startB: yesterdayStr, endB: yesterdayStr })}
                 compact/><StatCard 
                  title={t('reports.todayOrders')}
                  value={todayStats.orders.toString()}
                  desc={`${orderDelta.direction === 'up' ? '▲' : orderDelta.direction === 'down' ? '▼' : '→'} ${orderDelta.pct} vs yesterday`}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="info"
                  onDescClick={() => setComparisonFilter({ label: 'Today vs Yesterday', periodALabel: 'Today', periodBLabel: 'Yesterday', startA: todayStr, endA: todayStr, startB: yesterdayStr, endB: yesterdayStr })}
                 compact/><StatCard 
                  title={t('reports.todayAvgOrder')}
                  value={`${formatPrice(todayStats.avgOrder)}`}
                  desc={`${revDelta.direction === 'up' ? '▲' : revDelta.direction === 'down' ? '▼' : '→'} Avg ${revDelta.pct} vs yesterday`}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                  onDescClick={() => setComparisonFilter({ label: 'Today vs Yesterday', periodALabel: 'Today', periodBLabel: 'Yesterday', startA: todayStr, endA: todayStr, startB: yesterdayStr, endB: yesterdayStr })}
                 compact/><StatCard 
                  title={t('reports.todayItemsSold')}
                  value={todayStats.orders > 0 ? (todayStats.orders * (parseFloat(avgItemsPerOrder) || 1)).toFixed(0) : '0'}
                  desc={`${orderDelta.direction === 'up' ? '▲' : orderDelta.direction === 'down' ? '▼' : '→'} ${orderDelta.pct} vs yesterday`}
                  icon={<span className="ri-store-2-line ri-24px" />}
                  color="warning"
                  onDescClick={() => setComparisonFilter({ label: 'Today vs Yesterday', periodALabel: 'Today', periodBLabel: 'Yesterday', startA: todayStr, endA: todayStr, startB: yesterdayStr, endB: yesterdayStr })}
                />
              </div>

              {comparisonFilter && (
                <ComparisonTable
                  sales={sales}
                  filter={comparisonFilter}
                  currency={currency}
                  onDismiss={() => setComparisonFilter(null)}
                />
              )}

              {/* Comparison Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* vs Yesterday */}
                <Card padding="lg">
                  <h3 className="text-sm font-semibold text-base-content/70 mb-4 flex items-center gap-1.5">
                    <span className="ri-time-line ri-14px text-primary/60" />
                    {t('reports.vsYesterday')}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <StatCard
                      title={t('reports.todayRevenue')}
                      value={`${formatPrice(todayStats.revenue)}`}
                      desc={`${revDelta.direction === 'up' ? '▲' : revDelta.direction === 'down' ? '▼' : '→'} ${revDelta.pct} vs ${formatPrice(yesterdayStats.revenue)}`}
                      color={revDelta.direction === 'up' ? 'green-500' : revDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                    <StatCard
                      title={t('reports.todayOrders')}
                      value={todayStats.orders}
                      desc={`${orderDelta.direction === 'up' ? '▲' : orderDelta.direction === 'down' ? '▼' : '→'} ${orderDelta.pct} vs ${yesterdayStats.orders}`}
                      color={orderDelta.direction === 'up' ? 'green-500' : orderDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                  </div>
                </Card>

                {/* vs Same Day Last Week */}
                <Card padding="lg">
                  <h3 className="text-sm font-semibold text-base-content/70 mb-4 flex items-center gap-1.5">
                    <span className="ri-calendar-line ri-14px text-primary/60" />
                    {t('reports.vsLastWeek')}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <StatCard
                      title={t('reports.todayRevenue')}
                      value={`${formatPrice(todayStats.revenue)}`}
                      desc={`${wkRevDelta.direction === 'up' ? '▲' : wkRevDelta.direction === 'down' ? '▼' : '→'} ${wkRevDelta.pct} vs ${formatPrice(lastWeekStats.revenue)}`}
                      color={wkRevDelta.direction === 'up' ? 'green-500' : wkRevDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                    <StatCard
                      title={t('reports.todayOrders')}
                      value={todayStats.orders}
                      desc={`${wkOrderDelta.direction === 'up' ? '▲' : wkOrderDelta.direction === 'down' ? '▼' : '→'} ${wkOrderDelta.pct} vs ${lastWeekStats.orders}`}
                      color={wkOrderDelta.direction === 'up' ? 'green-500' : wkOrderDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                  </div>
                </Card>
              </div>

              {/* Comparison Bar Chart */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.dailyTrend14Days')}</h3>
                <div className="w-full h-72" dir="ltr">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dailyTrend} margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" angle={-30} textAnchor="end" height={60} />
                      <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                      <Tooltip
                        contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                      />
                      <Legend />
                      <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={30} name={t('reports.tableRevenue')} />
                      <Bar dataKey="orders" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={30} name={t('reports.totalOrders')} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>

              {/* Daily Comparison Table */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.dailyBreakdown')}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-base-300/30">
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableDate')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableOrders')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableAvgOrder')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableDayLabel')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dailyTrend.map(day => {
                        const dateObj = new Date(day.date + 'T00:00:00');
                        const dayName = dateObj.toLocaleDateString(undefined, { weekday: 'short' });
                        const isToday = day.date === todayStr;
                        return (
                          <tr key={day.date} className={`border-b border-base-300/50 hover:bg-base-100/50 ${isToday ? 'bg-primary/10' : ''}`}>
                            <td className={`py-3 px-4 font-medium ${isToday ? 'text-info dark:text-info/80' : 'text-base-content'}`}>
                              {day.date} {isToday && <span className="text-xs text-info ml-1">({t('reports.today')})</span>}
                            </td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(day.revenue)}</td>
                            <td className="py-3 px-4 text-right text-base-content">{day.orders}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(day.orders > 0 ? day.revenue / day.orders : 0)}</td>
                            <td className="py-3 px-4 text-base-content/50 text-sm">{dayName}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Employee Daily Breakdown */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4 flex items-center gap-2">
                  <span className="ri-group-line ri-20px text-info" />
                  {t('reports.employeeDailyBreakdown')}
                </h3>
                {employeeDailyStats.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableEmployee')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.todayOrders')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.todayRevenue')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.yesterdayOrders')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.yesterdayRevenue')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.revenueChange')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.orderChange')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employeeDailyStats.map(emp => (
                          <tr key={emp.id} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 font-medium text-base-content">{emp.name}</td>
                            <td className="py-3 px-4 text-right text-base-content font-semibold">{emp.todayOrders}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(emp.todayRevenue)}</td>
                            <td className="py-3 px-4 text-right text-base-content/70">{emp.yesterdayOrders}</td>
                            <td className="py-3 px-4 text-right text-base-content/70">{formatPrice(emp.yesterdayRevenue)}</td>
                            <td className={`py-3 px-4 text-right font-semibold ${emp.revColor}`}>
                              {emp.revDirection === 'up' && <span className="ri-stock-line inline w-3.5 h-3.5 mr-0.5" />}
                              {emp.revDirection === 'down' && <span className="ri-stock-line inline w-3.5 h-3.5 mr-0.5 rotate-180" />}
                              {emp.revChange}
                            </td>
                            <td className={`py-3 px-4 text-right font-semibold ${emp.orderColor}`}>
                              {emp.orderDirection === 'up' && <span className="ri-stock-line inline w-3.5 h-3.5 mr-0.5" />}
                              {emp.orderDirection === 'down' && <span className="ri-stock-line inline w-3.5 h-3.5 mr-0.5 rotate-180" />}
                              {emp.orderChange}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 text-base-content/50">
                    <span className="ri-group-line ri-20px" />
                    <span>{t('reports.noEmployeeDailyData')}</span>
                  </div>
                )}
              </Card>
            </div>
          )}

          {activeTab === 'periodComparison' && (
            <div className="space-y-6">
              {/* Period Toggle */}
              <div className="flex items-center gap-2 mb-2">
                <div className="inline-flex bg-base-100/50 rounded-lg p-1">
                  <button
                    onClick={() => setPeriodView('week')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                      periodView === 'week'
                        ? 'bg-info text-info-content shadow-md'
                        : 'text-base-content/60 hover:bg-base-100/50'
                    }`}
                  >{t('reports.periodWeek')}</button>
                  <button
                    onClick={() => setPeriodView('month')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                      periodView === 'month'
                        ? 'bg-info text-info-content shadow-md'
                        : 'text-base-content/60 hover:bg-base-100/50'
                    }`}
                  >{t('reports.periodMonth')}</button>
                </div>
                <span className="text-xs text-base-content/50 ml-2">
                  {periodView === 'week'
                    ? `${thisWeekStart} · ${todayStr}`
                    : `${currentMonthStart} · ${todayStr}`
                  }
                </span>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.currentPeriodRevenue')}
                  value={`${formatPrice(currentStats.revenue)}`}
                  desc={`${periodRevDelta.direction === 'up' ? '▲' : periodRevDelta.direction === 'down' ? '▼' : '→'} ${periodRevDelta.pct} vs previous`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                  onDescClick={() => setComparisonFilter(periodView === 'week'
                    ? { label: 'This Week vs Last Week', periodALabel: 'This Week', periodBLabel: 'Last Week', startA: thisWeekStart, endA: todayStr, startB: prevWeekStart, endB: prevWeekEnd }
                    : { label: 'This Month vs Last Month', periodALabel: 'This Month', periodBLabel: 'Last Month', startA: currentMonthStart, endA: todayStr, startB: prevMonthStart, endB: prevMonthEnd }
                  )}
                 compact/><StatCard 
                  title={t('reports.currentPeriodOrders')}
                  value={currentStats.orders.toString()}
                  desc={`${periodOrderDelta.direction === 'up' ? '▲' : periodOrderDelta.direction === 'down' ? '▼' : '→'} ${periodOrderDelta.pct} vs previous`}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="info"
                  onDescClick={() => setComparisonFilter(periodView === 'week'
                    ? { label: 'This Week vs Last Week', periodALabel: 'This Week', periodBLabel: 'Last Week', startA: thisWeekStart, endA: todayStr, startB: prevWeekStart, endB: prevWeekEnd }
                    : { label: 'This Month vs Last Month', periodALabel: 'This Month', periodBLabel: 'Last Month', startA: currentMonthStart, endA: todayStr, startB: prevMonthStart, endB: prevMonthEnd }
                  )}
                 compact/><StatCard 
                  title={t('reports.currentPeriodAvg')}
                  value={`${formatPrice(currentStats.avgOrder)}`}
                  desc={`${periodRevDelta.direction === 'up' ? '▲' : periodRevDelta.direction === 'down' ? '▼' : '→'} Avg ${periodRevDelta.pct} vs previous`}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                  onDescClick={() => setComparisonFilter(periodView === 'week'
                    ? { label: 'This Week vs Last Week', periodALabel: 'This Week', periodBLabel: 'Last Week', startA: thisWeekStart, endA: todayStr, startB: prevWeekStart, endB: prevWeekEnd }
                    : { label: 'This Month vs Last Month', periodALabel: 'This Month', periodBLabel: 'Last Month', startA: currentMonthStart, endA: todayStr, startB: prevMonthStart, endB: prevMonthEnd }
                  )}
                 compact/><StatCard 
                  title={t('reports.previousPeriod')}
                  value={`${formatPrice(previousStats.revenue)}`}
                  desc={`${currentStats.revenue > previousStats.revenue ? '▲ Up' : currentStats.revenue < previousStats.revenue ? '▼ Down' : '→ Flat'} from current`}
                  icon={<span className="ri-calendar-line ri-24px" />}
                  color="neutral"
                compact
                />
              </div>

              {comparisonFilter && (
                <ComparisonTable
                  sales={sales}
                  filter={comparisonFilter}
                  currency={currency}
                  onDismiss={() => setComparisonFilter(null)}
                />
              )}

              {/* Comparison Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Card padding="lg">
                  <h3 className="text-sm font-semibold text-base-content/70 mb-4 flex items-center gap-1.5">
                    <span className="ri-bar-chart-2-line ri-14px text-primary/60" />
                    {t('reports.revenueComparison')}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <StatCard
                      title={t('reports.currentPeriodShort')}
                      value={`${formatPrice(currentStats.revenue)}`}
                      desc={`${periodRevDelta.direction === 'up' ? '▲' : periodRevDelta.direction === 'down' ? '▼' : '→'} ${periodRevDelta.pct} vs ${formatPrice(previousStats.revenue)}`}
                      color={periodRevDelta.direction === 'up' ? 'green-500' : periodRevDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                    <StatCard
                      title={t('reports.previousPeriodShort')}
                      value={`${formatPrice(previousStats.revenue)}`}
                      desc={`${periodRevDelta.direction === 'up' ? '▲' : periodRevDelta.direction === 'down' ? '▼' : '→'} ${periodRevDelta.pct} vs current`}
                      color={periodRevDelta.direction === 'up' ? 'green-500' : periodRevDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                  </div>
                </Card>
                <Card padding="lg">
                  <h3 className="text-sm font-semibold text-base-content/70 mb-4 flex items-center gap-1.5">
                    <span className="ri-shopping-bag-line ri-14px text-primary/60" />
                    {t('reports.ordersComparison')}
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <StatCard
                      title={t('reports.currentPeriodShort')}
                      value={currentStats.orders}
                      desc={`${periodOrderDelta.direction === 'up' ? '▲' : periodOrderDelta.direction === 'down' ? '▼' : '→'} ${periodOrderDelta.pct} vs ${previousStats.orders}`}
                      color={periodOrderDelta.direction === 'up' ? 'green-500' : periodOrderDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                    <StatCard
                      title={t('reports.previousPeriodShort')}
                      value={previousStats.orders}
                      desc={`${periodOrderDelta.direction === 'up' ? '▲' : periodOrderDelta.direction === 'down' ? '▼' : '→'} ${periodOrderDelta.pct} vs current`}
                      color={periodOrderDelta.direction === 'up' ? 'green-500' : periodOrderDelta.direction === 'down' ? 'red-500' : 'slate-400'}
                      animated={false}
                    compact
                    />
                  </div>
                </Card>
              </div>

              {/* Trend Chart */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.periodTrend')}</h3>
                <div className="w-full h-72" dir="ltr">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={periodTrend} margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" vertical={false} />
                      <XAxis dataKey="label" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" angle={-25} textAnchor="end" height={50} />
                      <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                      <Tooltip
                        contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                      />
                      <Legend />
                      <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={30} name={t('reports.tableRevenue')} />
                      <Bar dataKey="orders" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={30} name={t('reports.totalOrders')} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>

              {/* Period Breakdown Table */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.periodBreakdown')}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-base-300/30">
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{periodView === 'week' ? t('reports.tableWeek') : t('reports.tableMonth')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableOrders')}</th>
                        <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableAvgOrder')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {periodTrend.map((p, i) => (
                        <tr key={i} className="border-b border-base-300/50 hover:bg-base-100/50">
                          <td className="py-3 px-4 font-medium text-base-content">{p.label}</td>
                          <td className="py-3 px-4 text-right text-base-content">{formatPrice(p.revenue)}</td>
                          <td className="py-3 px-4 text-right text-base-content">{p.orders}</td>
                          <td className="py-3 px-4 text-right text-base-content">{formatPrice(p.orders > 0 ? p.revenue / p.orders : 0)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'deliveryTracking' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.deliveryOrders')}
                  value={deliveryStats.totalOrders.toString()}
                  icon={<span className="ri-store-2-line ri-24px" />}
                  color="primary"
                 compact/><StatCard 
                  title={t('reports.totalRevenue')}
                  value={`${formatPrice(deliveryStats.totalRevenue)}`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.avgOrderValue')}
                  value={`${formatPrice(deliveryStats.avgOrderValue)}`}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                 compact/><StatCard 
                  title={t('reports.deliveryCompleted')}
                  value={`${deliveryStats.completedOrders} / ${deliveryStats.pendingOrders}`}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="warning"
                compact
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportDeliveryCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Delivery Orders List */}
              {filteredDeliverySales.length > 0 ? (
                <div className="space-y-3">
                  {filteredDeliverySales.map(sale => {
                    const dtName = sale.delivery_type_id ? deliveryTypeMap.get(sale.delivery_type_id) : null;
                    const zoneName = sale.delivery_zone_id ? deliveryZoneMap.get(sale.delivery_zone_id) : null;
                    const emp = employees.find(e => e.id === sale.employee_id);
                    return (
                      <Card padding="lg" hover transitional className="border-l-4 border-warning" key={sale.id}>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            {zoneName && (
                              <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold bg-warning/10 text-warning mb-1.5">
                                {zoneName}
                              </span>
                            )}
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <span className="text-sm font-bold text-base-content">{t('reports.tableInvoice')} #{sale.id}</span>
                              <span className="text-xs text-base-content/50">{sale.date} {sale.time}</span>
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                                sale.status === 'completed' ? 'bg-success/20 text-success'
                                : sale.status === 'cancelled' ? 'bg-error/20 text-error'
                                : 'bg-warning/20 text-warning'
                              }`}>{sale.status}</span>
                            </div>
                            {/* Delivery Address — map-style card */}
                            <div className="flex items-start gap-2 bg-base-100/40 rounded-lg p-3 mb-2 border border-base-300/50">
                              <span className="ri-store-2-line ri-16px text-warning mt-0.5 shrink-0" />
                              <div>
                                <p className="text-xs font-medium text-base-content/50 uppercase tracking-wider">{t('reports.deliveryAddress')}</p>
                                <p className="text-sm text-base-content font-medium">{sale.delivery_address || t('reports.noAddress')}</p>
                              </div>
                            </div>
                            {/* Extra info row */}
                            <div className="flex items-center gap-3 text-xs text-base-content/50">
                              {dtName && <span>{dtName}</span>}
                              {emp && <span>{emp.name}</span>}
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <p className="text-lg font-bold text-primary">{formatPrice(sale.total_amount)}</p>
                          </div>
                        </div>
                      </Card>
                    );
                  })}
                </div>
              ) : (
                <Card padding="xl" center>
                  <span className="ri-store-2-line ri-48px mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 text-lg mb-2">{t('reports.noDeliveries')}</p>
                  <p className="text-base-content/50">{t('reports.noDeliveriesHint')}</p>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'inventory' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.stockValueLabel')}
                  value={`${formatPrice(stockValue)}`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="success"
                 compact/><StatCard 
                  title={t('reports.activeIngredients')}
                  value={ingredients.filter(i => i.is_active).length.toString()}
                  icon={<span className="ri-archive-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.lowStockItems')}
                  value={lowStockItems.length.toString()}
                  icon={<span className="ri-alert-line ri-24px" />}
                  color="error"
                 compact/><StatCard 
                  title={t('transactions.title')}
                  value={inventoryTxns.length.toString()}
                  icon={<span className="ri-calendar-line ri-24px" />}
                  color="secondary"
                compact
                />
              </div>

              {/* CSV Export Bar */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportInventoryCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Low Stock Alerts */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4 flex items-center gap-2">
                  <span className="ri-alert-line ri-20px text-error" />
                  {t('reports.lowStockAlerts')}
                </h3>
                {lowStockItems.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableIngredient')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableCurrent')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableMin')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableShortage')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableUnit')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {lowStockItems.map((item, i) => (
                          <tr key={i} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 font-medium text-base-content">{item.name}</td>
                            <td className="py-3 px-4 text-right text-error font-semibold">{item.currentQuantity}</td>
                            <td className="py-3 px-4 text-right text-base-content/70">{item.reorderLevel}</td>
                            <td className="py-3 px-4 text-right text-warning">{item.shortage}</td>
                            <td className="py-3 px-4 text-base-content/70">{item.unit}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 text-success">
                    <span className="ri-alert-line ri-20px" />
                    <span>{t('reports.allWellStocked')}</span>
                  </div>
                )}
              </Card>

              {/* Active Ingredients Stock */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.ingredientStockLevels')}</h3>
                {ingredients.filter(i => i.is_active).length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableIngredient')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableQuantity')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableUnit')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableCostPerUnit')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableValue')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableStatus')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ingredients.filter(i => i.is_active).map(ing => (
                          <tr key={ing.id} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 font-medium text-base-content">{ing.name}</td>
                            <td className="py-3 px-4 text-right text-base-content">{ing.current_quantity}</td>
                            <td className="py-3 px-4 text-base-content/70">{ing.unit}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(ing.cost_per_unit)}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice((ing.current_quantity * ing.cost_per_unit))}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                ing.current_quantity <= ing.reorder_level
                                  ? 'bg-error/20 text-error'
                                  : 'bg-success/20 text-success'
                              }`}>
                                {ing.current_quantity <= ing.reorder_level ? t('inventory.lowStock') : t('inventory.inStock')}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-base-content/50">{t('reports.noIngredients')}</p>
                )}
              </Card>

              {/* Recent Transactions */}
              {recentInventoryTxns.length > 0 && (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.recentTransactions')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableDate')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableIngredient')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableChange')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableType')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableNote')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentInventoryTxns.map(tx => {
                          const ing = ingredientMap.get(tx.ingredient_id);
                          return (
                            <tr key={tx.id} className="border-b border-base-300/50 hover:bg-base-100/50">
                              <td className="py-3 px-4 text-base-content/70 text-sm">
                                {tx.created_at ? new Date(tx.created_at).toLocaleDateString() : '-'}
                              </td>
                              <td className="py-3 px-4 font-medium text-base-content">
                                {ing?.name || `#${tx.ingredient_id}`}
                              </td>
                              <td className={`py-3 px-4 text-right font-semibold ${
                                tx.quantity_change > 0
                                  ? 'text-success'
                                  : 'text-error'
                              }`}>
                                {tx.quantity_change > 0 ? '+' : ''}{tx.quantity_change}
                              </td>
                              <td className="py-3 px-4">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-base-200/50 text-base-content/70 capitalize">
                                  {tx.transaction_type.replace('_', ' ')}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-base-content/50 text-sm">{tx.note || '-'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'recipes' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.totalRecipes')}
                  value={recipePerformance.length.toString()}
                  icon={<span className="ri-menu-2-line ri-24px" />}
                  color="warning"
                 compact/><StatCard 
                  title={t('reports.activeProducts')}
                  value={products.length.toString()}
                  icon={<span className="ri-store-2-line ri-24px" />}
                  color="success"
                 compact/><StatCard 
                  title={t('reports.avgProductPrice')}
                  value={`${formatPrice(products.length > 0 ? products.reduce((s, p) => s + p.price, 0) / products.length : 0)}`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.activeRecipes')}
                  value={recipes.filter(r => r.is_active).length.toString()}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                compact
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportRecipesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Recipe Performance Table */}
              {recipePerformance.length > 0 ? (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.recipePerformance')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tablePrice')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableYield')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-center">{t('reports.tableStatus')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recipePerformance.map(rp => (
                          <tr key={rp.recipeId} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 font-medium text-base-content">{rp.productName}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(rp.productPrice)}</td>
                            <td className="py-3 px-4 text-right text-base-content">{rp.yieldQuantity}</td>
                            <td className="py-3 px-4 text-center">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                rp.isActive
                                  ? 'bg-success/20 text-success'
                                  : 'bg-base-200/50 text-base-content/50'
                              }`}>
                                {rp.isActive ? t('common.active') : t('common.inactive')}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              ) : (
                <Card padding="xl" center>
                  <span className="ri-menu-2-line ri-48px mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 text-lg mb-2">{t('reports.noRecipes')}</p>
                  <p className="text-base-content/50">{t('reports.noRecipesHint')}</p>
                </Card>
              )}

              {/* Products List */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.productCatalog')}</h3>
                {products.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tablePrice')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableUnit')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.hasRecipe')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {products.map(p => {
                          const hasRecipe = recipes.some(r => r.product_id === p.id && r.is_active);
                          return (
                            <tr key={p.id} className="border-b border-base-300/50 hover:bg-base-100/50">
                              <td className="py-3 px-4 font-medium text-base-content">{p.name}</td>
                              <td className="py-3 px-4 text-right text-base-content">{formatPrice(p.price)}</td>
                              <td className="py-3 px-4 text-base-content/70">{p.unit}</td>
                              <td className="py-3 px-4">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  hasRecipe
                                    ? 'bg-success/20 text-success'
                                    : 'bg-base-200/50 text-base-content/50'
                                }`}>                                  {hasRecipe ? t('common.yes') : t('common.no')}
                              </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-base-content/50">{t('reports.noProducts')}</p>
                )}
              </Card>
            </div>
          )}

          {activeTab === 'transactions' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.totalRevenue')}
                  value={`${formatPrice(transactions.reduce((s, t) => s + t.total_amount, 0))}`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="primary"
                 compact/><StatCard 
                  title={t('reports.totalOrders')}
                  value={transactions.length.toString()}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.avgOrderValue')}
                  value={`${formatPrice(transactions.length > 0 ? transactions.reduce((s, t) => s + t.total_amount, 0) / transactions.length : 0)}`}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="secondary"
                 compact/><StatCard 
                  title={t('reports.transactionItems')}
                  value={transactions.reduce((s, t) => s + t.items.length, 0).toString()}
                  icon={<span className="ri-calendar-line ri-24px" />}
                  color="warning"
                compact
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportTransactionsCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Transaction List */}
              {transactions.length > 0 ? (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.transactionHistory')}</h3>
                  <div className="space-y-3">
                    {transactions.slice(0, 20).map(tx => (
                      <div key={tx.id} className="flex items-center justify-between bg-base-100/50 rounded-lg p-4 border border-base-300/50">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-base-content/50">{tx.date}</span>
                            <span className="text-xs text-base-content/50">{tx.time}</span>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {tx.items.slice(0, 3).map((item, idx) => (
                              <span key={idx} className="text-xs bg-base-300 px-2 py-0.5 rounded-full text-base-content/80">
                                {item.name} ×{item.quantity}
                              </span>
                            ))}
                            {tx.items.length > 3 && (
                              <span className="text-xs text-base-content/40">+{tx.items.length - 3} more</span>
                            )}
                          </div>
                        </div>
                        <div className="text-right shrink-0 ml-4">
                          <span className="text-lg font-bold text-primary">
                            {tx.currency} {tx.total_amount.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ) : (
                <Card padding="xl" center>
                  <span className="ri-calendar-line ri-48px mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 text-lg mb-2">{t('transactions.noTransactions')}</p>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'employees' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-3 md:gap-4"><StatCard 
                  title={t('reports.activeEmployees')}
                  value={employees.filter(e => e.is_active).length.toString()}
                  icon={<span className="ri-group-line ri-24px" />}
                  color="secondary"
                 compact/><StatCard 
                  title={t('reports.employeesWithSales')}
                  value={employeePerformance.length.toString()}
                  icon={<span className="ri-stock-line ri-24px" />}
                  color="info"
                 compact/><StatCard 
                  title={t('reports.totalOrders')}
                  value={employeePerformance.reduce((s, e) => s + e.orderCount, 0).toString()}
                  icon={<span className="ri-shopping-cart-line ri-24px" />}
                  color="success"
                 compact/><StatCard 
                  title={t('reports.totalRevenue')}
                  value={`${formatPrice(employeePerformance.reduce((s, e) => s + e.revenue, 0))}`}
                  icon={<span className="ri-money-dollar-box-line ri-24px" />}
                  color="warning"
                compact
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportEmployeesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
                >
                  <span className="ri-download-line ri-14px" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Employee Performance Charts */}
              {employeePerformance.length > 0 && (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.revenueByEmployee')}</h3>
                  <div className="w-full h-72" dir="ltr">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={employeePerformance.slice(0, 10)} margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" vertical={false} />
                        <XAxis dataKey="employeeName" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" angle={-20} textAnchor="end" height={50} />
                        <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <Tooltip
                          contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                          formatter={(value: number) => [`${formatPrice(value)}`, 'Revenue']}
                        />
                        <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={40} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              )}

              {/* Employee Performance Table */}
              {employeePerformance.length > 0 ? (
                <Card padding="xl">
                  <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.employeePerformance')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableEmployee')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableOrders')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableAvgOrder')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tablePerformance')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employeePerformance.map(emp => (
                          <tr key={emp.employeeId} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 font-medium text-base-content">{emp.employeeName}</td>
                            <td className="py-3 px-4 text-right text-base-content">{emp.orderCount}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(emp.revenue)}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(emp.averageOrderValue)}</td>
                            <td className="py-3 px-4">
                              {/* Mini performance bar */}
                              <div className="w-24 bg-base-300 rounded-full h-2.5 overflow-hidden">
                                <div
                                  className="h-full rounded-full bg-linear-to-r from-primary to-secondary"
                                  style={{
                                    width: `${Math.min(
                                      (emp.revenue / Math.max(...employeePerformance.map(e => e.revenue))) * 100,
                                      100
                                    )}%`,
                                  }}
                                />
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>
              ) : (
                <Card padding="xl" center>
                  <span className="ri-group-line ri-48px mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 text-lg mb-2">{t('reports.noEmployeeSales')}</p>
                  <p className="text-base-content/50">{t('reports.noEmployeeSalesHint')}</p>
                </Card>
              )}

              {/* Employee Directory Summary */}
              <Card padding="xl">
                <h3 className="text-lg font-bold text-base-content mb-4">{t('reports.employeeDirectory')}</h3>
                {employees.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-base-300/30">
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm">{t('reports.tableName')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-right">{t('reports.tableSalary')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableStatus')}</th>
                          <th className="py-3 px-4 text-base-content/50 font-medium text-sm text-left">{t('reports.tableJoined')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employees.map(emp => (
                          <tr key={emp.id} className="border-b border-base-300/50 hover:bg-base-100/50">
                            <td className="py-3 px-4 font-medium text-base-content">{emp.name}</td>
                            <td className="py-3 px-4 text-right text-base-content">{formatPrice(emp.salary)}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                emp.is_active
                                  ? 'bg-success/20 text-success'
                                  : 'bg-error/20 text-error'
                              }`}>
                                {emp.is_active ? t('common.active') : t('common.inactive')}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-base-content/70">{emp.joined_at || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-base-content/50">{t('reports.noEmployees')}</p>
                )}
              </Card>
            </div>
          )}

          {activeTab === 'taxReports' && (
            <TaxReportsPanel />
          )}
        </div>

      <KeyboardShortcutsModal isOpen={showShortcutHelp} onClose={() => setShowShortcutHelp(false)} />
    </PageLayout>
  );
}

// ---- Chart Colors ----
const PIE_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

// ---- Subcomponents ----

// ── Subcomponents (StatCard now imported from ../components/ui/StatCard) ──


