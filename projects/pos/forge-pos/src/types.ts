export interface Product {
  id: number;
  name: string;
  price: number;
  unit: string;
  category_id?: number | null;
  image?: string | null;
  product_type?: string;
  prepare_time_minutes?: number;
  barcode?: string | null;
  description?: string | null;
  /** Comma-separated order types this product is available for ('' = all). */
  available_order_types?: string;
}

export interface NewProduct {
  name: string;
  price: number;
  unit: string;
  category_id?: number | null;
  image?: string | null;
  product_type?: string;
  prepare_time_minutes?: number;
  barcode?: string | null;
  description?: string | null;
  available_order_types?: string;
}

export interface UpdateProductPayload {
  name?: string;
  price?: number;
  unit?: string;
  category_id?: number | null;
  image?: string | null;
  product_type?: string;
  prepare_time_minutes?: number;
  barcode?: string | null;
  description?: string | null;
  available_order_types?: string;
}

// ---- Category ----
export interface Category {
  id: number;
  name: string;
  color?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface NewCategory {
  name: string;
  color?: string | null;
}

export interface UpdateCategoryPayload {
  name?: string;
  color?: string | null;
}


export interface Settings {
  restaurant_name?: string;
  address?: string;
  phone?: string;
  email?: string;
  tax_rate?: string;
  tax_id?: string;
  currency?: string;
  opening_time?: string;
  closing_time?: string;
  receipt_footer?: string;
  logo?: string | null;
  invoice_logo?: string | null;
  dine_in_tables?: number;
  delivery_fee?: number;
  delivery_fee_per_km?: number;
  smtp_server?: string;
  smtp_port?: number;
  smtp_username?: string;
  smtp_password?: string;
  smtp_recipient?: string;
  smtp_from_name?: string;
  smtp_from_email?: string;
}

export interface DeliveryZone {
  id: number;
  name: string;
  base_fee: number;
  fee_per_km: number;
  max_distance: number;
  is_active: boolean;
}

export interface NewDeliveryZone {
  name: string;
  base_fee: number;
  fee_per_km: number;
  max_distance: number;
}

export interface DeliveryType {
  id: number;
  name: string;
  description?: string;
  fee_multiplier: number;
  is_active: boolean;
}

export interface EmployeeType {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface NewEmployeeType {
  name: string;
  description?: string | null;
}

export interface Employee {
  id: number;
  name: string;
  phone?: string;
  email?: string;
  employee_type_id: number;
  salary: number;
  is_active: boolean;
  joined_at?: string;
}

export interface NewEmployee {
  name: string;
  phone?: string | null;
  email?: string | null;
  employee_type_id: number;
  salary: number;
}

export interface SaleItem {
  name: string;
  price: number;
  quantity: number;
  unit: string;
}

export interface Sale {
  id: number;
  total_amount: number;
  currency: string;
  date: string;
  time: string;
  order_type: string;
  status: string;
  table_number: number | null;
  delivery_type_id: number | null;
  delivery_zone_id?: number | null;
  delivery_address: string | null;
  employee_id: number | null;
  customer_id?: number | null;
}

export interface NewSaleData {
  total_amount: number;
  currency: string;
  date?: string;
  time?: string;
  order_type: string;
  status: string;
  table_number?: number | null;
  delivery_type_id?: number | null;
  delivery_zone_id?: number | null;
  delivery_address?: string | null;
  employee_id?: number | null;
  customer_id?: number | null;
}

export interface NewSaleItemData {
  product_name: string;
  price: number;
  quantity: number;
  unit: string;
}

export interface TransactionItem {
  name: string;
  price: number;
  quantity: number;
  unit: string;
  subtotal: number;
}

export interface Transaction {
  id: number;
  items: TransactionItem[];
  total_amount: number;
  currency: string;
  date: string;
  time: string;
  order_type: string;
  status: string;
  table_number?: number | null;
  delivery_type_id?: number | null;
  delivery_address?: string | null;
}

export interface DailyRevenue {
  date: string;
  revenue: number;
  orders: number;
}

export interface TopProduct {
  name: string;
  sales: number;
  revenue: number;
}

export interface ProductDistribution {
  name: string;
  value: number;
}

export interface AnalyticsSummary {
  total_orders: number;
  total_revenue: number;
  average_order_value: number;
}

export interface AnalyticsData {
  daily_revenue: DailyRevenue[];
  top_products: TopProduct[];
  product_distribution: ProductDistribution[];
  summary: AnalyticsSummary;
}

export interface CartItem extends Product {
  quantity: number;
}

// ---- Recipe Types ----
export interface Recipe {
  id: number;
  product_id: number;
  recipe_type_id: number;
  yield_quantity: number;
  is_active: boolean;
}

export interface NewRecipe {
  product_id: number;
  recipe_type_id: number;
  yield_quantity: number;
}

export interface RecipeIngredient {
  id: number;
  recipe_id: number;
  ingredient_id: number;
  quantity: number;
  unit?: string | null;
  preparation_note?: string | null;
}

export interface NewRecipeIngredient {
  recipe_id: number;
  ingredient_id: number;
  quantity: number;
  unit?: string | null;
  preparation_note?: string | null;
}

// ---- Inventory Types ----
export interface Ingredient {
  id: number;
  name: string;
  unit: string;
  current_quantity: number;
  reorder_level: number;
  reorder_quantity: number;
  cost_per_unit: number;
  is_active: boolean;
}

export interface NewIngredient {
  name: string;
  unit: string;
  current_quantity: number;
  reorder_level: number;
  reorder_quantity: number;
  cost_per_unit: number;
}

export interface InventoryTransaction {
  id: number;
  ingredient_id: number;
  transaction_type: string;
  quantity_change: number;
  reference_id: number | null;
  note: string | null;
  created_at: string;
}

export interface NewInventoryTransaction {
  ingredient_id: number;
  transaction_type: string;
  quantity_change: number;
  reference_id?: number | null;
  note?: string | null;
}

export interface InventoryAdjustment {
  id: number;
  ingredient_id: number;
  previous_quantity: number;
  new_quantity: number;
  reason: string;
  created_by: string | null;
  created_at: string;
}

// ---- Enterprise Feature Types ----

export interface Role {
  id: number;
  name: string;
  permissions: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NewRole {
  name: string;
  permissions: string;
}

export interface ReportMetadata {
  id: number;
  report_type: string;
  format: string;
  file_path: string;
  parameters?: string | null;
  generated_by?: number | null;
  created_at: string;
}

export interface InventoryAlert {
  id: number;
  ingredient_id: number;
  alert_type: string;
  alert_message: string;
  is_resolved: boolean;
  created_at: string;
  resolved_at?: string | null;
}

export interface Supplier {
  id: number;
  name: string;
  contact_name?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  tax_id?: string | null;
  payment_terms?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NewSupplier {
  name: string;
  contact_name?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  tax_id?: string | null;
  payment_terms?: string | null;
}

export interface PurchaseOrder {
  id: number;
  supplier_id: number;
  reference_number?: string | null;
  status: string;
  total_amount: number;
  shipping_fee?: number;
  expected_date?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PurchaseOrderItem {
  id: number;
  purchase_order_id: number;
  ingredient_id: number;
  quantity: number;
  cost_per_unit: number;
  received_quantity: number;
}

export interface KitchenTicket {
  id: number;
  sale_id: number;
  status: string;
  priority: number;
  prepare_time_minutes: number;
  notes?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface Customer {
  id: number;
  name: string;
  phone?: string | null;
  email?: string | null;
  loyalty_points: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface NewCustomer {
  name: string;
  phone?: string | null;
  email?: string | null;
  notes?: string | null;
}

export interface LoyaltyTransaction {
  id: number;
  customer_id: number;
  sale_id?: number | null;
  points_change: number;
  reason: string;
  created_at: string;
}

export type InvoiceType = 'tax' | 'commercial' | 'proforma' | 'credit' | 'receipt' | 'selling' | 'goods_transfer';

export const INVOICE_TYPE_LABELS: Record<InvoiceType, string> = {
  tax: 'TAX INVOICE',
  commercial: 'COMMERCIAL INVOICE',
  proforma: 'PROFORMA INVOICE',
  credit: 'CREDIT NOTE',
  receipt: 'RECEIPT',
  selling: 'SELLING INVOICE',
  goods_transfer: 'GOODS TRANSFER',
};

// ---- Invoice Categories ----
export type InvoiceDirection = 'collection' | 'payment';

export interface InvoiceCategory {
  id: string;
  direction: InvoiceDirection;
  label: string;
  description?: string;
}

export const INVOICE_CATEGORIES: InvoiceCategory[] = [
  { id: 'get_goods', direction: 'collection', label: 'Get Goods', description: 'Inventory received from supplier' },
  { id: 'transfer_goods', direction: 'collection', label: 'Transfer Goods In', description: 'Goods transfer received' },
  { id: 'products', direction: 'collection', label: 'Products', description: 'Product sales invoice' },
  { id: 'production_creation', direction: 'collection', label: 'Production Creation', description: 'Created from production' },
  { id: 'all_transactions', direction: 'collection', label: 'All Transactions', description: 'Combined transaction record' },
  { id: 'employee_meal', direction: 'payment', label: 'Employee Meal', description: 'Staff meal deduction' },
  { id: 'pay_supplier', direction: 'payment', label: 'Pay Supplier', description: 'Payment to supplier' },
  { id: 'transfer_out', direction: 'payment', label: 'Transfer Goods Out', description: 'Goods transfer sent' },
];

export interface Note {
  id: number;
  name: string;
  template_body: string;
  category?: string | null;
  recipe_id?: number | null;
  is_default: boolean;
  use_as_template: boolean;
  selectable: boolean;
  steps?: string | null;
  created_at: string;
  updated_at: string;
}

export interface NoteStep {
  title: string;
  details?: string;
}

export interface TaxReport {
  id: number;
  period_start: string;
  period_end: string;
  total_sales: number;
  total_tax: number;
  transaction_count: number;
  generated_at: string;
}

export interface EmployeeSchedule {
  id: number;
  employee_id: number;
  shift_start: string;
  shift_end: string;
  status: string;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Payroll {
  id: number;
  employee_id: number;
  period_start: string;
  period_end: string;
  regular_hours: number;
  overtime_hours: number;
  total_pay: number;
  status: string;
  created_at: string;
  updated_at: string;
}

