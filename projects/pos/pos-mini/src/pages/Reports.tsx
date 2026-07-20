import { motion } from 'framer-motion';
import { useState, useEffect, useMemo, useCallback } from 'react';
import { 
  MdAttachMoney, MdShoppingCart, 
  MdPeople, MdInventory, MdMenuBook, MdWarning,
  MdTrendingUp, MdDateRange, MdStore, MdDashboard,
  MdReceipt, MdBarChart
} from 'react-icons/md';
import { FaFilePdf, FaDownload } from 'react-icons/fa';
import PageLayout from '../components/PageLayout';
import { SkeletonTable, SkeletonCard } from '../components/Skeleton';
import { useTranslation } from 'react-i18next';
import KeyboardShortcutsModal from '../components/KeyboardShortcutsModal';
import { invoke } from '@tauri-apps/api/core';
import { 
  Sale, Settings, AnalyticsData, Ingredient, InventoryTransaction, 
  Recipe, Employee, Product, Transaction, DeliveryType
} from '../types';
import jsPDF from 'jspdf';
import { downloadExcel } from '../utils/export';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

type Tab = 'overview' | 'sales' | 'inventory' | 'recipes' | 'employees' | 'transactions' | 'productsSales' | 'invoices' | 'dailyComparison' | 'deliveryTracking' | 'periodComparison';

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

export default function Reports() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('sales');
  const [currency, setCurrency] = useState('USD');
  const [restaurantName, setRestaurantName] = useState('POS');
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  // Date range filter for sales
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: '',
  });
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [periodView, setPeriodView] = useState<'week' | 'month'>('week');

  // Raw data
  const [sales, setSales] = useState<Sale[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [inventoryTxns, setInventoryTxns] = useState<InventoryTransaction[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [deliveryTypes, setDeliveryTypes] = useState<DeliveryType[]>([]);

  useEffect(() => {
    const loadAll = async () => {
      try {
        const [
          settingsRes, analyticsRes, salesRes,
          ingredientsRes, invTxnsRes, recipesRes,
          productsRes,          employeesRes,
          transactionsRes,
          deliveryTypesRes
        ] = await Promise.all([
          invoke<Settings>('get_settings'),
          invoke<AnalyticsData>('get_analytics').catch(() => null),
          invoke<Sale[]>('get_sales'),
          invoke<Ingredient[]>('get_ingredients', { includeInactive: true }),
          invoke<InventoryTransaction[]>('get_inventory_transactions', { ingredientId: null }),
          invoke<Recipe[]>('get_recipes', { includeInactive: true }),
          invoke<Product[]>('get_products'),
          invoke<Employee[]>('get_employees', { includeInactive: true }),
          invoke<Transaction[]>('get_transactions'),
          invoke<DeliveryType[]>('get_delivery_types', { includeInactive: true }),
        ]);

        setCurrency(settingsRes?.currency || 'USD');
        setRestaurantName(settingsRes?.restaurant_name || 'POS');
        setAnalytics(analyticsRes);
        setSales(Array.isArray(salesRes) ? salesRes : []);
        setIngredients(Array.isArray(ingredientsRes) ? ingredientsRes : []);
        setInventoryTxns(Array.isArray(invTxnsRes) ? invTxnsRes : []);
        setRecipes(Array.isArray(recipesRes) ? recipesRes : []);
        setProducts(Array.isArray(productsRes) ? productsRes : []);
        setEmployees(Array.isArray(employeesRes) ? employeesRes : []);
        setTransactions(Array.isArray(transactionsRes) ? transactionsRes : []);
        setDeliveryTypes(Array.isArray(deliveryTypesRes) ? deliveryTypesRes : []);
      } catch (error) {
        console.error('Error loading report data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAll();
  }, []);

  // ---- Help Modal State ----
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);


  // ---- Derived Data ----

  // Filtered sales for date range
  const filteredSales = useMemo(() => {
    if (!dateRange.start && !dateRange.end) return sales;
    return sales.filter(sale => {
      if (dateRange.start && sale.date < dateRange.start) return false;
      if (dateRange.end && sale.date > dateRange.end) return false;
      return true;
    });
  }, [sales, dateRange]);

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
      const tabKeys: Tab[] = ['overview', 'sales', 'productsSales', 'invoices', 'dailyComparison', 'periodComparison', 'deliveryTracking', 'inventory', 'recipes', 'employees', 'transactions'];
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
  const fmt = (d: Date) => d.toISOString().split('T')[0];
  const todayStr = fmt(new Date());
  const yesterdayStr = fmt(new Date(Date.now() - 86400000));
  const lastWeekStr = fmt(new Date(Date.now() - 7 * 86400000));

  // Aggregate sales by date
  const salesByDate = useMemo(() => {
    const map = new Map<string, Sale[]>();
    for (const sale of sales) {
      const date = sale.date;
      if (!map.has(date)) map.set(date, []);
      map.get(date)!.push(sale);
    }
    return map;
  }, [sales]);

  // Today's stats
  const todayStats = useMemo(() => {
    const daySales = salesByDate.get(todayStr) || [];
    const revenue = daySales.reduce((s, sale) => s + sale.total_amount, 0);
    const orders = daySales.length;
    const avgOrder = orders > 0 ? revenue / orders : 0;
    return { revenue, orders, avgOrder };
  }, [salesByDate]);

  // Yesterday's stats
  const yesterdayStats = useMemo(() => {
    const daySales = salesByDate.get(yesterdayStr) || [];
    const revenue = daySales.reduce((s, sale) => s + sale.total_amount, 0);
    const orders = daySales.length;
    const avgOrder = orders > 0 ? revenue / orders : 0;
    return { revenue, orders, avgOrder };
  }, [salesByDate]);

  // Same day last week's stats
  const lastWeekStats = useMemo(() => {
    const daySales = salesByDate.get(lastWeekStr) || [];
    const revenue = daySales.reduce((s, sale) => s + sale.total_amount, 0);
    const orders = daySales.length;
    const avgOrder = orders > 0 ? revenue / orders : 0;
    return { revenue, orders, avgOrder };
  }, [salesByDate]);

  // Daily trend data for last 14 days (for chart)
  const dailyTrend = useMemo(() => {
    const days: { date: string; revenue: number; orders: number }[] = [];
    for (let i = 13; i >= 0; i--) {
      const d = fmt(new Date(Date.now() - i * 86400000));
      const daySales = salesByDate.get(d) || [];
      const revenue = daySales.reduce((s, sale) => s + sale.total_amount, 0);
      const orders = daySales.length;
      days.push({ date: d, revenue, orders });
    }
    return days;
  }, [salesByDate]);

  // Delta helper: returns formatted percentage change and direction indicator
  const delta = (current: number, previous: number): { pct: string; direction: 'up' | 'down' | 'flat'; color: string } => {
    if (previous === 0 && current === 0) return { pct: '0%', direction: 'flat', color: 'text-slate-400' };
    if (previous === 0) return { pct: '+100%', direction: 'up', color: 'text-green-500' };
    const pct = ((current - previous) / previous) * 100;
    const formatted = `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`;
    if (pct > 0) return { pct: formatted, direction: 'up', color: 'text-green-500' };
    if (pct < 0) return { pct: formatted, direction: 'down', color: 'text-red-500' };
    return { pct: '0%', direction: 'flat', color: 'text-slate-400' };
  };

  const revDelta = delta(todayStats.revenue, yesterdayStats.revenue);
  const orderDelta = delta(todayStats.orders, yesterdayStats.orders);
  const wkRevDelta = delta(todayStats.revenue, lastWeekStats.revenue);
  const wkOrderDelta = delta(todayStats.orders, lastWeekStats.orders);

  // ---- Period Comparison (Week/Month) ----
  const now = new Date();
  const currentMonthStart = fmt(new Date(now.getFullYear(), now.getMonth(), 1));
  const prevMonthStart = fmt(new Date(now.getFullYear(), now.getMonth() - 1, 1));
  const prevMonthEnd = fmt(new Date(now.getFullYear(), now.getMonth(), 0)); // last day of prev month

  // Compute stats for a date range
  const periodStats = (start: string, end: string) => {
    const periodSales = sales.filter(s => s.date >= start && s.date <= end);
    const revenue = periodSales.reduce((sum, s) => sum + s.total_amount, 0);
    const orders = periodSales.length;
    const avgOrder = orders > 0 ? revenue / orders : 0;
    return { revenue, orders, avgOrder };
  };

  // Week periods
  const thisWeekStart = fmt(new Date(Date.now() - 6 * 86400000));
  const prevWeekStart = fmt(new Date(Date.now() - 13 * 86400000));
  const prevWeekEnd = fmt(new Date(Date.now() - 7 * 86400000));

  const thisWeekStats = useMemo(() => periodStats(thisWeekStart, todayStr), [sales, thisWeekStart, todayStr]);
  const prevWeekStats = useMemo(() => periodStats(prevWeekStart, prevWeekEnd), [sales, prevWeekStart, prevWeekEnd]);
  const thisMonthStats = useMemo(() => periodStats(currentMonthStart, todayStr), [sales, currentMonthStart, todayStr]);
  const prevMonthStats = useMemo(() => periodStats(prevMonthStart, prevMonthEnd), [sales, prevMonthStart, prevMonthEnd]);

  const currentStats = periodView === 'week' ? thisWeekStats : thisMonthStats;
  const previousStats = periodView === 'week' ? prevWeekStats : prevMonthStats;

  const periodRevDelta = delta(currentStats.revenue, previousStats.revenue);
  const periodOrderDelta = delta(currentStats.orders, previousStats.orders);

  // Weekly/monthly trend (last 8 periods)
  const periodTrend = useMemo(() => {
    const result: { label: string; revenue: number; orders: number }[] = [];
    if (periodView === 'week') {
      // Last 8 weeks
      for (let i = 7; i >= 0; i--) {
        const end = fmt(new Date(Date.now() - (i * 7) * 86400000));
        const start = fmt(new Date(Date.now() - (i * 7 + 6) * 86400000));
        const stats = periodStats(start, end);
        result.push({
          label: `${start.slice(5)}-${end.slice(5)}`,
          revenue: stats.revenue,
          orders: stats.orders,
        });
      }
    } else {
      // Last 8 months
      for (let i = 7; i >= 0; i--) {
        const m = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const label = m.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
        const mStart = fmt(m);
        const mEnd = fmt(new Date(now.getFullYear(), now.getMonth() - i + 1, 0));
        const stats = periodStats(mStart, mEnd);
        result.push({ label, revenue: stats.revenue, orders: stats.orders });
      }
    }
    return result;
  }, [sales, periodView]);

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
        addText('Total Revenue', `${currency} ${analytics.summary.total_revenue.toFixed(2)}`);
        addText('Total Orders', analytics.summary.total_orders.toString());
        addText('Average Order Value', `${currency} ${analytics.summary.average_order_value.toFixed(2)}`);
        y += 5;
      }

      // Order Type Breakdown
      addSection('Orders by Type');
      orderTypeBreakdown.forEach(ot => {
        addText(ot.type, `${ot.count} orders — ${currency} ${ot.revenue.toFixed(2)}`);
      });
      y += 5;

      // Top Products
      if (analytics?.top_products && analytics.top_products.length > 0) {
        addSection('Top Products');
        const topSlice = analytics.top_products.slice(0, 5);
        topSlice.forEach((p, i) => {
          addText(`#${i + 1} ${p.name}`, `${p.sales} sold — ${currency} ${p.revenue.toFixed(2)}`);
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
      addText('Total Stock Value', `${currency} ${stockValue.toFixed(2)}`);
      addText('Active Ingredients', ingredients.filter(i => i.is_active).length.toString());
      addText('Low Stock Items', lowStockItems.length.toString());
      y += 5;

      // Employee Performance
      if (employeePerformance.length > 0) {
        addSection('Employee Performance');
        employeePerformance.slice(0, 5).forEach((emp, i) => {
          addText(
            `#${i + 1} ${emp.employeeName}`,
            `${emp.orderCount} orders — ${currency} ${emp.revenue.toFixed(2)}`
          );
        });
        y += 5;
      }

      // Footer
      const dateStr = new Date().toLocaleDateString();
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.text(
        `Report generated on ${dateStr} — ${restaurantName}`,
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
      ['Invoice #', 'Date', 'Time', 'Status', 'Delivery Address', 'Delivery Type', 'Amount', 'Currency', 'Employee'],
      filteredDeliverySales.map(s => {
        const dtName = s.delivery_type_id ? deliveryTypeMap.get(s.delivery_type_id) : null;
        const emp = employees.find(e => e.id === s.employee_id);
        return [
          String(s.id), s.date || '', s.time || '', s.status || '',
          s.delivery_address || '', dtName || '',
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



  // ---- Tab Navigation ----
  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'overview' as Tab, label: 'Overview', icon: <MdDashboard className="w-5 h-5" /> },
    { key: 'sales' as Tab, label: 'Sales', icon: <MdAttachMoney className="w-5 h-5" /> },
    { key: 'productsSales' as Tab, label: 'Products Sales', icon: <MdBarChart className="w-5 h-5" /> },
    { key: 'invoices' as Tab, label: 'Invoices', icon: <MdReceipt className="w-5 h-5" /> },
    { key: 'dailyComparison' as Tab, label: 'Daily Comparison', icon: <MdTrendingUp className="w-5 h-5" /> },
    { key: 'periodComparison' as Tab, label: 'Period Comparison', icon: <MdDateRange className="w-5 h-5" /> },
    { key: 'deliveryTracking' as Tab, label: 'Delivery Tracking', icon: <MdStore className="w-5 h-5" /> },
    { key: 'inventory' as Tab, label: 'Inventory', icon: <MdInventory className="w-5 h-5" /> },
    { key: 'recipes' as Tab, label: 'Recipes', icon: <MdMenuBook className="w-5 h-5" /> },
    { key: 'employees' as Tab, label: 'Employees', icon: <MdPeople className="w-5 h-5" /> },
    { key: 'transactions' as Tab, label: 'Transactions', icon: <MdDateRange className="w-5 h-5" /> },
  ];

  if (loading) {
    return (
      <PageLayout title={t('reports.title')} background="bg-slate-100 dark:bg-slate-900">
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
      background="bg-linear-to-br from-slate-100 via-indigo-50 to-slate-100 dark:from-slate-900 dark:via-indigo-950 dark:to-slate-900"
      padding="py-10"
    >
      {/* Export Buttons */}
      <div className="flex justify-end gap-3 mb-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleExportExcel}
          disabled={exporting}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400
            text-white px-4 py-2 rounded-lg transition-colors duration-300"
        >
          {exporting ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
              />
              <span>{t('reports.exporting')}</span>
            </>
          ) : (
            <>
              <FaDownload className="w-5 h-5" />
              <span>{t('reports.exportExcel')}</span>
            </>
          )}
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={exportPDF}
          disabled={exporting}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:bg-red-400 
            text-white px-4 py-2 rounded-lg transition-colors duration-300"
        >
          {exporting ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
              />
              <span>{t('reports.exporting')}</span>
            </>
          ) : (
            <>
              <FaFilePdf className="w-5 h-5" />
              <span>{t('reports.exportPDF')}</span>
            </>
          )}
        </motion.button>
      </div>

        {/* Active Date Range Indicator */}
        {(dateRange.start || dateRange.end) && (
          <div className="text-center mb-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium
              bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300">
              <MdDateRange className="w-3.5 h-3.5" />
              {t('reports.showingDataFrom', { start: dateRange.start || t('reports.dateEarliest'), end: dateRange.end || t('reports.dateLatest') })}
            </span>
          </div>
        )}

        {/* Global Date Range Filter */}
        <div className="card--glass rounded-xl p-4 mb-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="flex items-center gap-2 shrink-0">
              <MdDateRange className="w-5 h-5 text-indigo-500" />
              <span className="text-sm font-semibold text-slate-900 dark:text-white">{t('common.period')}</span>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <button onClick={() => applyDatePreset('today')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === 'today'
                    ? 'bg-indigo-500 text-white' : 'bg-white/50 dark:bg-white/5 text-slate-600 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-800/30'
                }`}>{t('reports.dateToday')}</button>
              <button onClick={() => applyDatePreset('7d')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === '7d'
                    ? 'bg-indigo-500 text-white' : 'bg-white/50 dark:bg-white/5 text-slate-600 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-800/30'
                }`}>{t('reports.date7Days')}</button>
              <button onClick={() => applyDatePreset('30d')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === '30d'
                    ? 'bg-indigo-500 text-white' : 'bg-white/50 dark:bg-white/5 text-slate-600 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-800/30'
                }`}>{t('reports.date30Days')}</button>
              <button onClick={() => applyDatePreset('month')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  activePreset === 'month'
                    ? 'bg-indigo-500 text-white' : 'bg-white/50 dark:bg-white/5 text-slate-600 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-800/30'
                }`}>{t('reports.dateThisMonth')}</button>
            </div>
            <div className="flex items-center gap-2 flex-1 sm:justify-end">
              <input type="date" value={dateRange.start}
                onChange={e => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                className="px-2.5 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 
                  dark:border-gray-600 text-slate-900 dark:text-white text-xs w-36" />
              <span className="text-slate-400 text-xs">{t('reports.dateTo')}</span>
              <input type="date" value={dateRange.end}
                onChange={e => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                className="px-2.5 py-1.5 rounded-lg bg-white/50 dark:bg-white/5 border border-slate-300 
                  dark:border-gray-600 text-slate-900 dark:text-white text-xs w-36" />
              {(dateRange.start || dateRange.end) && (
                <button onClick={() => applyDatePreset('clear')}
                  className="text-xs text-red-500 hover:text-red-400 transition-colors shrink-0">
                  {t('reports.dateClear')}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-1 sm:gap-2 mb-8 bg-white/50 dark:bg-white/5 backdrop-blur-sm rounded-xl p-1.5 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg transition-all duration-300 whitespace-nowrap shrink-0 justify-center ${
                activeTab === tab.key
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-white/10'
              }`}
            >
              {tab.icon}
              <span className="font-medium text-sm sm:text-base">{t('reports.' + tab.key)}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Cross-section KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.totalOrders')}
                  value={filteredSales.length.toString()}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.stockValueLabel')}
                  value={`${currency} ${stockValue.toFixed(2)}`}
                  icon={<MdInventory className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.activeRecipes')}
                  value={recipes.filter(r => r.is_active).length.toString()}
                  icon={<MdMenuBook className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
                <SummaryCard
                  title={t('reports.activeEmployees')}
                  value={employees.filter(e => e.is_active).length.toString()}
                  icon={<MdPeople className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
              </div>

              {/* Revenue Trend Chart */}
              {analytics?.daily_revenue && analytics.daily_revenue.length > 0 && (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.revenueTrend')}</h3>
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
                </div>
              )}

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                {/* Low Stock Alert */}
                <div className="card--glass card--hover rounded-xl p-5 border-l-4 border-red-500">
                  <p className="text-xs text-slate-500 dark:text-white/50 uppercase tracking-wider">{t('reports.lowStockItems')}</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{lowStockItems.length}</p>
                  <p className="text-xs text-slate-400 mt-1">{t('reports.needReordering')}</p>
                </div>
                {/* Order Types */}
                <div className="card--glass card--hover rounded-xl p-5 border-l-4 border-blue-500">
                  <p className="text-xs text-slate-500 dark:text-white/50 uppercase tracking-wider">{t('reports.orderTypes')}</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{orderTypeBreakdown.length}</p>
                  <p className="text-xs text-slate-400 mt-1">{orderTypeBreakdown.map(o => o.type).join(', ') || t('reports.none')}</p>
                </div>
                {/* Total Products */}
                <div className="card--glass card--hover rounded-xl p-5 border-l-4 border-emerald-500">
                  <p className="text-xs text-slate-500 dark:text-white/50 uppercase tracking-wider">{t('reports.products')}</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{products.length}</p>
                  <p className="text-xs text-slate-400 mt-1">{t('reports.haveRecipes', { count: products.filter(p => recipes.some(r => r.product_id === p.id && r.is_active)).length })}</p>
                </div>
                {/* Total Salary */}
                <div className="card--glass card--hover rounded-xl p-5 border-l-4 border-amber-500">
                  <p className="text-xs text-slate-500 dark:text-white/50 uppercase tracking-wider">{t('reports.monthlySalary')}</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{currency} {employees.filter(e => e.is_active).reduce((s, e) => s + e.salary, 0).toFixed(0)}</p>
                  <p className="text-xs text-slate-400 mt-1">{t('reports.activeEmployeesCount', { count: employees.filter(e => e.is_active).length })}</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'sales' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.totalRevenue')}
                  value={`${currency} ${analytics?.summary?.total_revenue?.toFixed(2) || '0.00'}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.totalOrders')}
                  value={(filteredSales.length).toString()}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.avgOrderValue')}
                  value={`${currency} ${analytics?.summary.average_order_value.toFixed(2) || '0.00'}`}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
                <SummaryCard
                  title={t('reports.orderTypes')}
                  value={orderTypeBreakdown.length.toString()}
                  icon={<MdStore className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportSalesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Order Type Breakdown — Cards + Pie Chart */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                {/* Cards */}
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.ordersByType')}</h3>
                  {orderTypeBreakdown.length > 0 ? (
                    <div className="space-y-3">
                      {orderTypeBreakdown.map(ot => {
                        const colors: Record<string, string> = {
                          'Dine-in': 'bg-green-500/20 text-green-600 dark:text-green-400 border-green-300 dark:border-green-700',
                          'Takeaway': 'bg-blue-500/20 text-blue-600 dark:text-blue-400 border-blue-300 dark:border-blue-700',
                        };
                        const fallbackColor = 'bg-orange-500/20 text-orange-600 dark:text-orange-400 border-orange-300 dark:border-orange-700';
                        const colorClass = colors[ot.type] || fallbackColor;
                        return (
                          <div key={ot.type} className={`flex items-center gap-4 p-4 rounded-lg border ${colorClass}`}>
                            <div className={`p-3 rounded-lg ${colorClass}`}>
                              <MdStore className="w-5 h-5" />
                            </div>
                            <div className="flex-1">
                              <p className="text-sm text-slate-500 dark:text-white/50">{ot.type}</p>
                              <p className="text-lg font-bold text-slate-900 dark:text-white">{t('reports.ordersCount', { count: ot.count })}</p>
                              <p className="text-sm text-slate-600 dark:text-white/70">{currency} {ot.revenue.toFixed(2)}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-slate-500 dark:text-white/40">{t('reports.noOrderData')}</p>
                  )}
                </div>

                {/* Pie Chart */}
                {orderTypeBreakdown.length > 0 && (
                  <div className="card--glass rounded-xl p-6">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.orderDistribution')}</h3>
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
                  </div>
                )}
              </div>

              {/* Top Products */}
              {analytics?.top_products && analytics.top_products.length > 0 && (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.topProducts')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">#</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableSold')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.top_products.map((p, i) => (
                          <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 text-slate-500 dark:text-white/50">{i + 1}</td>
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{p.name}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{p.sales}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {p.revenue.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Revenue Trend Chart */}
              {analytics?.daily_revenue && analytics.daily_revenue.length > 0 && (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Revenue Trend</h3>
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
                </div>
              )}
            </div>
          )}

          {activeTab === 'productsSales' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.totalProductsSold')}
                  value={analytics?.summary?.total_orders?.toString() || '0'}
                  icon={<MdBarChart className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.productRevenue')}
                  value={`${currency} ${analytics?.summary?.total_revenue?.toFixed(2) || '0.00'}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.bestSellingCategory')}
                  value={bestSellingCategory}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
                <SummaryCard
                  title={t('reports.avgItemsPerOrder')}
                  value={avgItemsPerOrder}
                  icon={<MdStore className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportProductsSalesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Product Performance Table */}
              {analytics?.top_products && analytics.top_products.length > 0 ? (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.productsSalesBreakdown')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">#</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableSold')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableShare')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analytics.top_products.map((p, i) => {
                          const maxRevenue = Math.max(...analytics.top_products.map(x => x.revenue));
                          const share = maxRevenue > 0 ? (p.revenue / maxRevenue) * 100 : 0;
                          return (
                            <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                              <td className="py-3 px-4 text-slate-500 dark:text-white/50">{i + 1}</td>
                              <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{p.name}</td>
                              <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{p.sales}</td>
                              <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {p.revenue.toFixed(2)}</td>
                              <td className="py-3 px-4">
                                <div className="flex items-center gap-2">
                                  <div className="w-20 bg-slate-200 dark:bg-white/10 rounded-full h-2 overflow-hidden">
                                    <div
                                      className="h-full rounded-full bg-linear-to-r from-indigo-500 to-purple-500"
                                      style={{ width: `${Math.min(share, 100)}%` }}
                                    />
                                  </div>
                                  <span className="text-xs text-slate-500 dark:text-white/50">{p.revenue > 0 ? `${((p.revenue / (analytics?.summary?.total_revenue || 1)) * 100).toFixed(1)}%` : '0%'}</span>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="card--glass rounded-xl p-6 text-center">
                  <MdBarChart className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600 dark:text-white/70 text-lg mb-2">{t('reports.noProductSales')}</p>
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noProductSalesHint')}</p>
                </div>
              )}

              {/* Revenue Distribution Bar Chart */}
              {analytics?.product_distribution && analytics.product_distribution.length > 0 && (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.productDistribution')}</h3>
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
                </div>
              )}
            </div>
          )}

          {activeTab === 'invoices' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.totalInvoices')}
                  value={filteredSales.length.toString()}
                  icon={<MdReceipt className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.totalRevenue')}
                  value={`${currency} ${filteredSales.reduce((s, s2) => s + s2.total_amount, 0).toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.avgOrderValue')}
                  value={`${currency} ${filteredSales.length > 0 ? (filteredSales.reduce((s, s2) => s + s2.total_amount, 0) / filteredSales.length).toFixed(2) : '0.00'}`}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
                <SummaryCard
                  title={t('reports.completedOrders')}
                  value={filteredSales.filter(s => s.status === 'completed').length.toString()}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-emerald-500 to-teal-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportInvoicesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Invoices Table */}
              {filteredSales.length > 0 ? (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.invoiceList')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableInvoice')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableDate')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableTime')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableOrderType')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableStatus')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableAmount')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableEmployee')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredSales.map(sale => {
                          const emp = employees.find(e => e.id === sale.employee_id);
                          return (
                            <tr key={sale.id} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                              <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">#{sale.id}</td>
                              <td className="py-3 px-4 text-slate-600 dark:text-white/70">{sale.date}</td>
                              <td className="py-3 px-4 text-slate-600 dark:text-white/70">{sale.time}</td>
                              <td className="py-3 px-4">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400">
                                  {sale.order_type || '-'}
                                </span>
                              </td>
                              <td className="py-3 px-4">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${sale.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : sale.status === 'cancelled' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'}`}>
                                  {sale.status}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-right font-bold text-slate-900 dark:text-white">{sale.currency || currency} {sale.total_amount.toFixed(2)}</td>
                              <td className="py-3 px-4 text-slate-600 dark:text-white/70">{emp?.name || '-'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="card--glass rounded-xl p-6 text-center">
                  <MdReceipt className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600 dark:text-white/70 text-lg mb-2">{t('reports.noInvoices')}</p>
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noInvoicesHint')}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'dailyComparison' && (
            <div className="space-y-6">
              {/* Today's Overview Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.todayRevenue')}
                  value={`${currency} ${todayStats.revenue.toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.todayOrders')}
                  value={todayStats.orders.toString()}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.todayAvgOrder')}
                  value={`${currency} ${todayStats.avgOrder.toFixed(2)}`}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
                <SummaryCard
                  title={t('reports.todayItemsSold')}
                  value={todayStats.orders > 0 ? (todayStats.orders * (parseFloat(avgItemsPerOrder) || 1)).toFixed(0) : '0'}
                  icon={<MdStore className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
              </div>

              {/* Comparison Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* vs Yesterday */}
                <div className="card--glass rounded-xl p-5">
                  <h3 className="text-sm font-semibold text-slate-500 dark:text-white/50 uppercase tracking-wider mb-4">{t('reports.vsYesterday')}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.todayRevenue')}</p>
                      <p className="text-lg font-bold text-slate-900 dark:text-white">{currency} {todayStats.revenue.toFixed(2)}</p>
                      <p className={`text-sm font-semibold ${revDelta.color}`}>
                        {revDelta.direction === 'up' && <MdTrendingUp className="inline w-4 h-4 mr-0.5" />}
                        {revDelta.direction === 'down' && <MdTrendingUp className="inline w-4 h-4 mr-0.5 rotate-180" />}
                        {revDelta.pct}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">{t('reports.yesterday')}: {currency} {yesterdayStats.revenue.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.todayOrders')}</p>
                      <p className="text-lg font-bold text-slate-900 dark:text-white">{todayStats.orders}</p>
                      <p className={`text-sm font-semibold ${orderDelta.color}`}>
                        {orderDelta.direction === 'up' && <MdTrendingUp className="inline w-4 h-4 mr-0.5" />}
                        {orderDelta.direction === 'down' && <MdTrendingUp className="inline w-4 h-4 mr-0.5 rotate-180" />}
                        {orderDelta.pct}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">{t('reports.yesterday')}: {yesterdayStats.orders}</p>
                    </div>
                  </div>
                </div>

                {/* vs Same Day Last Week */}
                <div className="card--glass rounded-xl p-5">
                  <h3 className="text-sm font-semibold text-slate-500 dark:text-white/50 uppercase tracking-wider mb-4">{t('reports.vsLastWeek')}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.todayRevenue')}</p>
                      <p className="text-lg font-bold text-slate-900 dark:text-white">{currency} {todayStats.revenue.toFixed(2)}</p>
                      <p className={`text-sm font-semibold ${wkRevDelta.color}`}>
                        {wkRevDelta.direction === 'up' && <MdTrendingUp className="inline w-4 h-4 mr-0.5" />}
                        {wkRevDelta.direction === 'down' && <MdTrendingUp className="inline w-4 h-4 mr-0.5 rotate-180" />}
                        {wkRevDelta.pct}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">{lastWeekStr}: {currency} {lastWeekStats.revenue.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.todayOrders')}</p>
                      <p className="text-lg font-bold text-slate-900 dark:text-white">{todayStats.orders}</p>
                      <p className={`text-sm font-semibold ${wkOrderDelta.color}`}>
                        {wkOrderDelta.direction === 'up' && <MdTrendingUp className="inline w-4 h-4 mr-0.5" />}
                        {wkOrderDelta.direction === 'down' && <MdTrendingUp className="inline w-4 h-4 mr-0.5 rotate-180" />}
                        {wkOrderDelta.pct}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">{lastWeekStr}: {lastWeekStats.orders} {t('reports.orders')}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Comparison Bar Chart */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.dailyTrend14Days')}</h3>
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
              </div>

              {/* Daily Comparison Table */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.dailyBreakdown')}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10">
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableDate')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableOrders')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableAvgOrder')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableDayLabel')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dailyTrend.map(day => {
                        const dateObj = new Date(day.date + 'T00:00:00');
                        const dayName = dateObj.toLocaleDateString(undefined, { weekday: 'short' });
                        const isToday = day.date === todayStr;
                        return (
                          <tr key={day.date} className={`border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5 ${isToday ? 'bg-indigo-50 dark:bg-indigo-900/10' : ''}`}>
                            <td className={`py-3 px-4 font-medium ${isToday ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-900 dark:text-white'}`}>
                              {day.date} {isToday && <span className="text-xs text-indigo-500 ml-1">({t('reports.today')})</span>}
                            </td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {day.revenue.toFixed(2)}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{day.orders}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {day.orders > 0 ? (day.revenue / day.orders).toFixed(2) : '0.00'}</td>
                            <td className="py-3 px-4 text-slate-500 dark:text-white/50 text-sm">{dayName}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Employee Daily Breakdown */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <MdPeople className="w-5 h-5 text-indigo-500" />
                  {t('reports.employeeDailyBreakdown')}
                </h3>
                {employeeDailyStats.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableEmployee')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.todayOrders')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.todayRevenue')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.yesterdayOrders')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.yesterdayRevenue')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.revenueChange')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.orderChange')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employeeDailyStats.map(emp => (
                          <tr key={emp.id} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{emp.name}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white font-semibold">{emp.todayOrders}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {emp.todayRevenue.toFixed(2)}</td>
                            <td className="py-3 px-4 text-right text-slate-500 dark:text-white/70">{emp.yesterdayOrders}</td>
                            <td className="py-3 px-4 text-right text-slate-500 dark:text-white/70">{currency} {emp.yesterdayRevenue.toFixed(2)}</td>
                            <td className={`py-3 px-4 text-right font-semibold ${emp.revColor}`}>
                              {emp.revDirection === 'up' && <MdTrendingUp className="inline w-3.5 h-3.5 mr-0.5" />}
                              {emp.revDirection === 'down' && <MdTrendingUp className="inline w-3.5 h-3.5 mr-0.5 rotate-180" />}
                              {emp.revChange}
                            </td>
                            <td className={`py-3 px-4 text-right font-semibold ${emp.orderColor}`}>
                              {emp.orderDirection === 'up' && <MdTrendingUp className="inline w-3.5 h-3.5 mr-0.5" />}
                              {emp.orderDirection === 'down' && <MdTrendingUp className="inline w-3.5 h-3.5 mr-0.5 rotate-180" />}
                              {emp.orderChange}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 text-slate-500 dark:text-white/50">
                    <MdPeople className="w-5 h-5" />
                    <span>{t('reports.noEmployeeDailyData')}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'periodComparison' && (
            <div className="space-y-6">
              {/* Period Toggle */}
              <div className="flex items-center gap-2 mb-2">
                <div className="inline-flex bg-white/50 dark:bg-white/5 rounded-lg p-1">
                  <button
                    onClick={() => setPeriodView('week')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                      periodView === 'week'
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-white/10'
                    }`}
                  >{t('reports.periodWeek')}</button>
                  <button
                    onClick={() => setPeriodView('month')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 ${
                      periodView === 'month'
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-white/50 dark:hover:bg-white/10'
                    }`}
                  >{t('reports.periodMonth')}</button>
                </div>
                <span className="text-xs text-slate-500 dark:text-white/50 ml-2">
                  {periodView === 'week'
                    ? `${thisWeekStart} — ${todayStr}`
                    : `${currentMonthStart} — ${todayStr}`
                  }
                </span>
              </div>

              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.currentPeriodRevenue')}
                  value={`${currency} ${currentStats.revenue.toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.currentPeriodOrders')}
                  value={currentStats.orders.toString()}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.currentPeriodAvg')}
                  value={`${currency} ${currentStats.avgOrder.toFixed(2)}`}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
                <SummaryCard
                  title={t('reports.previousPeriod')}
                  value={`${currency} ${previousStats.revenue.toFixed(2)}`}
                  icon={<MdDateRange className="w-6 h-6" />}
                  color="from-slate-400 to-slate-500"
                />
              </div>

              {/* Comparison Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="card--glass rounded-xl p-5">
                  <h3 className="text-sm font-semibold text-slate-500 dark:text-white/50 uppercase tracking-wider mb-4">{t('reports.revenueComparison')}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.currentPeriodShort')}</p>
                      <p className="text-lg font-bold text-slate-900 dark:text-white">{currency} {currentStats.revenue.toFixed(2)}</p>
                      <p className={`text-sm font-semibold ${periodRevDelta.color}`}>
                        {periodRevDelta.direction === 'up' && <MdTrendingUp className="inline w-4 h-4 mr-0.5" />}
                        {periodRevDelta.direction === 'down' && <MdTrendingUp className="inline w-4 h-4 mr-0.5 rotate-180" />}
                        {periodRevDelta.pct}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.previousPeriodShort')}</p>
                      <p className="text-lg font-bold text-slate-500 dark:text-white/70">{currency} {previousStats.revenue.toFixed(2)}</p>
                    </div>
                  </div>
                </div>
                <div className="card--glass rounded-xl p-5">
                  <h3 className="text-sm font-semibold text-slate-500 dark:text-white/50 uppercase tracking-wider mb-4">{t('reports.ordersComparison')}</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.currentPeriodShort')}</p>
                      <p className="text-lg font-bold text-slate-900 dark:text-white">{currentStats.orders}</p>
                      <p className={`text-sm font-semibold ${periodOrderDelta.color}`}>
                        {periodOrderDelta.direction === 'up' && <MdTrendingUp className="inline w-4 h-4 mr-0.5" />}
                        {periodOrderDelta.direction === 'down' && <MdTrendingUp className="inline w-4 h-4 mr-0.5 rotate-180" />}
                        {periodOrderDelta.pct}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 dark:text-white/40">{t('reports.previousPeriodShort')}</p>
                      <p className="text-lg font-bold text-slate-500 dark:text-white/70">{previousStats.orders}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Trend Chart */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.periodTrend')}</h3>
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
              </div>

              {/* Period Breakdown Table */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.periodBreakdown')}</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10">
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{periodView === 'week' ? t('reports.tableWeek') : t('reports.tableMonth')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableOrders')}</th>
                        <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableAvgOrder')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {periodTrend.map((p, i) => (
                        <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                          <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{p.label}</td>
                          <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {p.revenue.toFixed(2)}</td>
                          <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{p.orders}</td>
                          <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {p.orders > 0 ? (p.revenue / p.orders).toFixed(2) : '0.00'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'deliveryTracking' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.deliveryOrders')}
                  value={deliveryStats.totalOrders.toString()}
                  icon={<MdStore className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.totalRevenue')}
                  value={`${currency} ${deliveryStats.totalRevenue.toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.avgOrderValue')}
                  value={`${currency} ${deliveryStats.avgOrderValue.toFixed(2)}`}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
                <SummaryCard
                  title={t('reports.deliveryCompleted')}
                  value={`${deliveryStats.completedOrders} / ${deliveryStats.pendingOrders}`}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportDeliveryCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Delivery Orders List */}
              {filteredDeliverySales.length > 0 ? (
                <div className="space-y-3">
                  {filteredDeliverySales.map(sale => {
                    const dtName = sale.delivery_type_id ? deliveryTypeMap.get(sale.delivery_type_id) : null;
                    const emp = employees.find(e => e.id === sale.employee_id);
                    return (
                      <div key={sale.id} className="card--glass rounded-xl p-5 border-l-4 border-orange-500 hover:shadow-lg transition-shadow duration-300">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <span className="text-sm font-bold text-slate-900 dark:text-white">{t('reports.tableInvoice')} #{sale.id}</span>
                              <span className="text-xs text-slate-500 dark:text-white/50">{sale.date} {sale.time}</span>
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                                sale.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                : sale.status === 'cancelled' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                              }`}>{sale.status}</span>
                            </div>
                            {/* Delivery Address — map-style card */}
                            <div className="flex items-start gap-2 bg-white/40 dark:bg-white/5 rounded-lg p-3 mb-2 border border-slate-200 dark:border-white/5">
                              <MdStore className="w-4 h-4 text-orange-500 mt-0.5 shrink-0" />
                              <div>
                                <p className="text-xs font-medium text-slate-500 dark:text-white/50 uppercase tracking-wider">{t('reports.deliveryAddress')}</p>
                                <p className="text-sm text-slate-900 dark:text-white font-medium">{sale.delivery_address || t('reports.noAddress')}</p>
                              </div>
                            </div>
                            {/* Extra info row */}
                            <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-white/50">
                              {dtName && <span>{dtName}</span>}
                              {emp && <span>{emp.name}</span>}
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <p className="text-lg font-bold text-teal-600 dark:text-teal-400">{sale.currency || currency} {sale.total_amount.toFixed(2)}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="card--glass rounded-xl p-6 text-center">
                  <MdStore className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600 dark:text-white/70 text-lg mb-2">{t('reports.noDeliveries')}</p>
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noDeliveriesHint')}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'inventory' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.stockValueLabel')}
                  value={`${currency} ${stockValue.toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-emerald-500 to-teal-600"
                />
                <SummaryCard
                  title={t('reports.activeIngredients')}
                  value={ingredients.filter(i => i.is_active).length.toString()}
                  icon={<MdInventory className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.lowStockItems')}
                  value={lowStockItems.length.toString()}
                  icon={<MdWarning className="w-6 h-6" />}
                  color="from-red-500 to-rose-600"
                />
                <SummaryCard
                  title={t('transactions.title')}
                  value={inventoryTxns.length.toString()}
                  icon={<MdDateRange className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
              </div>

              {/* CSV Export Bar */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportInventoryCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Low Stock Alerts */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                  <MdWarning className="w-5 h-5 text-red-500" />
                  {t('reports.lowStockAlerts')}
                </h3>
                {lowStockItems.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableIngredient')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableCurrent')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableMin')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableShortage')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableUnit')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {lowStockItems.map((item, i) => (
                          <tr key={i} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{item.name}</td>
                            <td className="py-3 px-4 text-right text-red-600 dark:text-red-400 font-semibold">{item.currentQuantity}</td>
                            <td className="py-3 px-4 text-right text-slate-600 dark:text-white/70">{item.reorderLevel}</td>
                            <td className="py-3 px-4 text-right text-orange-600 dark:text-orange-400">{item.shortage}</td>
                            <td className="py-3 px-4 text-slate-600 dark:text-white/70">{item.unit}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 text-green-600 dark:text-green-400">
                    <MdWarning className="w-5 h-5" />
                    <span>{t('reports.allWellStocked')}</span>
                  </div>
                )}
              </div>

              {/* Active Ingredients Stock */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.ingredientStockLevels')}</h3>
                {ingredients.filter(i => i.is_active).length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableIngredient')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableQuantity')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableUnit')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableCostPerUnit')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableValue')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableStatus')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {ingredients.filter(i => i.is_active).map(ing => (
                          <tr key={ing.id} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{ing.name}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{ing.current_quantity}</td>
                            <td className="py-3 px-4 text-slate-600 dark:text-white/70">{ing.unit}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {ing.cost_per_unit.toFixed(2)}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {(ing.current_quantity * ing.cost_per_unit).toFixed(2)}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                ing.current_quantity <= ing.reorder_level
                                  ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                  : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
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
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noIngredients')}</p>
                )}
              </div>

              {/* Recent Transactions */}
              {recentInventoryTxns.length > 0 && (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.recentTransactions')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableDate')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableIngredient')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableChange')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableType')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableNote')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentInventoryTxns.map(tx => {
                          const ing = ingredientMap.get(tx.ingredient_id);
                          return (
                            <tr key={tx.id} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                              <td className="py-3 px-4 text-slate-600 dark:text-white/70 text-sm">
                                {tx.created_at ? new Date(tx.created_at).toLocaleDateString() : '-'}
                              </td>
                              <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">
                                {ing?.name || `#${tx.ingredient_id}`}
                              </td>
                              <td className={`py-3 px-4 text-right font-semibold ${
                                tx.quantity_change > 0 
                                  ? 'text-green-600 dark:text-green-400' 
                                  : 'text-red-600 dark:text-red-400'
                              }`}>
                                {tx.quantity_change > 0 ? '+' : ''}{tx.quantity_change}
                              </td>
                              <td className="py-3 px-4">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-white/10 text-slate-700 dark:text-white/70 capitalize">
                                  {tx.transaction_type.replace('_', ' ')}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-slate-500 dark:text-white/50 text-sm">{tx.note || '-'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'recipes' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.totalRecipes')}
                  value={recipePerformance.length.toString()}
                  icon={<MdMenuBook className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
                <SummaryCard
                  title={t('reports.activeProducts')}
                  value={products.length.toString()}
                  icon={<MdStore className="w-6 h-6" />}
                  color="from-green-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.avgProductPrice')}
                  value={`${currency} ${products.length > 0 ? (products.reduce((s, p) => s + p.price, 0) / products.length).toFixed(2) : '0.00'}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.activeRecipes')}
                  value={recipes.filter(r => r.is_active).length.toString()}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportRecipesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Recipe Performance Table */}
              {recipePerformance.length > 0 ? (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.recipePerformance')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tablePrice')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableYield')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-center">{t('reports.tableStatus')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recipePerformance.map(rp => (
                          <tr key={rp.recipeId} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{rp.productName}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {rp.productPrice.toFixed(2)}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{rp.yieldQuantity}</td>
                            <td className="py-3 px-4 text-center">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                rp.isActive
                                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                  : 'bg-slate-100 text-slate-500 dark:bg-white/5 dark:text-white/40'
                              }`}>
                                {rp.isActive ? t('common.active') : t('common.inactive')}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="card--glass rounded-xl p-6 text-center">
                  <MdMenuBook className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600 dark:text-white/70 text-lg mb-2">{t('reports.noRecipes')}</p>
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noRecipesHint')}</p>
                </div>
              )}

              {/* Products List */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.productCatalog')}</h3>
                {products.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableProduct')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tablePrice')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableUnit')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.hasRecipe')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {products.map(p => {
                          const hasRecipe = recipes.some(r => r.product_id === p.id && r.is_active);
                          return (
                            <tr key={p.id} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                              <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{p.name}</td>
                              <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {p.price.toFixed(2)}</td>
                              <td className="py-3 px-4 text-slate-600 dark:text-white/70">{p.unit}</td>
                              <td className="py-3 px-4">
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                  hasRecipe
                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                    : 'bg-slate-100 text-slate-500 dark:bg-white/5 dark:text-white/40'
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
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noProducts')}</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'transactions' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.totalRevenue')}
                  value={`${currency} ${transactions.reduce((s, t) => s + t.total_amount, 0).toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-teal-500 to-emerald-600"
                />
                <SummaryCard
                  title={t('reports.totalOrders')}
                  value={transactions.length.toString()}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-blue-500 to-indigo-600"
                />
                <SummaryCard
                  title={t('reports.avgOrderValue')}
                  value={`${currency} ${transactions.length > 0 ? (transactions.reduce((s, t) => s + t.total_amount, 0) / transactions.length).toFixed(2) : '0.00'}`}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-purple-500 to-violet-600"
                />
                <SummaryCard
                  title={t('reports.transactionItems')}
                  value={transactions.reduce((s, t) => s + t.items.length, 0).toString()}
                  icon={<MdDateRange className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportTransactionsCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Transaction List */}
              {transactions.length > 0 ? (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.transactionHistory')}</h3>
                  <div className="space-y-3">
                    {transactions.slice(0, 20).map(tx => (
                      <div key={tx.id} className="flex items-center justify-between bg-white/50 dark:bg-white/5 rounded-lg p-4 border border-slate-200 dark:border-white/5">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-slate-500 dark:text-gray-400">{tx.date}</span>
                            <span className="text-xs text-slate-500 dark:text-gray-400">{tx.time}</span>
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {tx.items.slice(0, 3).map((item, idx) => (
                              <span key={idx} className="text-xs bg-slate-200 dark:bg-white/10 px-2 py-0.5 rounded-full text-slate-700 dark:text-gray-300">
                                {item.name} ×{item.quantity}
                              </span>
                            ))}
                            {tx.items.length > 3 && (
                              <span className="text-xs text-slate-400">+{tx.items.length - 3} more</span>
                            )}
                          </div>
                        </div>
                        <div className="text-right shrink-0 ml-4">
                          <span className="text-lg font-bold text-teal-600 dark:text-teal-400">
                            {tx.currency} {tx.total_amount.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="card--glass rounded-xl p-6 text-center">
                  <MdDateRange className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600 dark:text-white/70 text-lg mb-2">{t('transactions.noTransactions')}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'employees' && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 gap-4">
                <SummaryCard
                  title={t('reports.activeEmployees')}
                  value={employees.filter(e => e.is_active).length.toString()}
                  icon={<MdPeople className="w-6 h-6" />}
                  color="from-indigo-500 to-purple-600"
                />
                <SummaryCard
                  title={t('reports.employeesWithSales')}
                  value={employeePerformance.length.toString()}
                  icon={<MdTrendingUp className="w-6 h-6" />}
                  color="from-blue-500 to-cyan-600"
                />
                <SummaryCard
                  title={t('reports.totalOrders')}
                  value={employeePerformance.reduce((s, e) => s + e.orderCount, 0).toString()}
                  icon={<MdShoppingCart className="w-6 h-6" />}
                  color="from-emerald-500 to-teal-600"
                />
                <SummaryCard
                  title={t('reports.totalRevenue')}
                  value={`${currency} ${employeePerformance.reduce((s, e) => s + e.revenue, 0).toFixed(2)}`}
                  icon={<MdAttachMoney className="w-6 h-6" />}
                  color="from-orange-500 to-amber-600"
                />
              </div>

              {/* CSV Export */}
              <div className="flex justify-end">
                <button
                  onClick={handleExportEmployeesCSV}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    bg-teal-500/10 text-teal-600 dark:text-teal-400 hover:bg-teal-500/20 transition-colors"
                >
                  <FaDownload className="w-3.5 h-3.5" />
                  {t('reports.exportCSV')}
                </button>
              </div>

              {/* Employee Performance Charts */}
              {employeePerformance.length > 0 && (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.revenueByEmployee')}</h3>
                  <div className="w-full h-72" dir="ltr">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={employeePerformance.slice(0, 10)} margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,100,0.1)" vertical={false} />
                        <XAxis dataKey="employeeName" tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" angle={-20} textAnchor="end" height={50} />
                        <YAxis tick={{ fontSize: 10 }} stroke="rgba(100,100,100,0.4)" />
                        <Tooltip
                          contentStyle={{ background: 'rgba(15,23,42,0.9)', border: 'none', borderRadius: '8px', color: '#fff' }}
                          formatter={(value: number) => [`${currency} ${value.toFixed(2)}`, 'Revenue']}
                        />
                        <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={40} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Employee Performance Table */}
              {employeePerformance.length > 0 ? (
                <div className="card--glass rounded-xl p-6">
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.employeePerformance')}</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableEmployee')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableOrders')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableRevenue')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableAvgOrder')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tablePerformance')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employeePerformance.map(emp => (
                          <tr key={emp.employeeId} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{emp.employeeName}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{emp.orderCount}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {emp.revenue.toFixed(2)}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {emp.averageOrderValue.toFixed(2)}</td>
                            <td className="py-3 px-4">
                              {/* Mini performance bar */}
                              <div className="w-24 bg-slate-200 dark:bg-white/10 rounded-full h-2.5 overflow-hidden">
                                <div
                                  className="h-full rounded-full bg-linear-to-r from-indigo-500 to-purple-500"
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
                </div>
              ) : (
                <div className="card--glass rounded-xl p-6 text-center">
                  <MdPeople className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <p className="text-slate-600 dark:text-white/70 text-lg mb-2">{t('reports.noEmployeeSales')}</p>
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noEmployeeSalesHint')}</p>
                </div>
              )}

              {/* Employee Directory Summary */}
              <div className="card--glass rounded-xl p-6">
                <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">{t('reports.employeeDirectory')}</h3>
                {employees.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/10">
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm">{t('reports.tableName')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-right">{t('reports.tableSalary')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableStatus')}</th>
                          <th className="py-3 px-4 text-slate-500 dark:text-white/50 font-medium text-sm text-left">{t('reports.tableJoined')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {employees.map(emp => (
                          <tr key={emp.id} className="border-b border-slate-100 dark:border-white/5 hover:bg-white/50 dark:hover:bg-white/5">
                            <td className="py-3 px-4 font-medium text-slate-900 dark:text-white">{emp.name}</td>
                            <td className="py-3 px-4 text-right text-slate-900 dark:text-white">{currency} {emp.salary.toFixed(2)}</td>
                            <td className="py-3 px-4">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                emp.is_active
                                  ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                  : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                              }`}>
                                {emp.is_active ? t('common.active') : t('common.inactive')}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-slate-600 dark:text-white/70">{emp.joined_at || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-slate-500 dark:text-white/40">{t('reports.noEmployees')}</p>
                )}
              </div>
            </div>
          )}
        </motion.div>

      <KeyboardShortcutsModal isOpen={showShortcutHelp} onClose={() => setShowShortcutHelp(false)} />
    </PageLayout>
  );
}

// ---- Chart Colors ----
const PIE_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'];

// ---- Subcomponents ----

interface SummaryCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
}

function SummaryCard({ title, value, icon, color }: SummaryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card--glass card--hover rounded-xl p-5"
    >
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-lg bg-linear-to-br ${color} text-white shadow-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-slate-500 dark:text-white/60">{title}</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">{value}</p>
        </div>
      </div>
    </motion.div>
  );
}
