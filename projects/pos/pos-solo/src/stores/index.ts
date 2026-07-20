/**
 * POS-KO Zustand Stores — Barrel Export
 *
 * All 22 stores in one import:
 *   import { useProductStore, useCustomerStore } from '../stores';
 */

export { useAuthStore } from './auth';
export type { User } from './auth';

export { useProductStore } from './products';
export type { Product } from './products';

export { useCustomerStore } from './customers';
export type { Customer } from './customers';

export { useSaleStore } from './sales';
export type { Sale } from './sales';

export { useEmployeeStore } from './employees';
export type { Employee } from './employees';

export { useInventoryStore } from './inventory';
export type { Ingredient, InventoryTransaction, InventoryAdjustment } from './inventory';

export { useRecipeStore } from './recipes';
export type { Recipe, RecipeIngredient } from './recipes';

export { useCategoryStore } from './categories';
export type { Category } from './categories';

export { useDeliveryTypeStore } from './deliveryTypes';
export type { DeliveryType } from './deliveryTypes';

export { useEmployeeTypeStore } from './employeeTypes';
export type { EmployeeType } from './employeeTypes';

export { useSettingsStore } from './settings';
export type { Settings } from './settings';

export { useAnalyticsStore } from './analytics';
export type { AnalyticsData } from './analytics';

export { useRoleStore } from './roles';
export type { Role } from './roles';

export { useSupplierStore } from './suppliers';
export type { Supplier } from './suppliers';

export { usePurchaseOrderStore } from './purchaseOrders';
export type { PurchaseOrder, PurchaseOrderItem } from './purchaseOrders';

export { useKitchenTicketStore } from './kitchenTickets';
export type { KitchenTicket } from './kitchenTickets';

export { useReceiptTemplateStore } from './receiptTemplates';
export type { ReceiptTemplate } from './receiptTemplates';

export { useTaxReportStore } from './taxReports';
export type { TaxReport } from './taxReports';

export { useEmployeeScheduleStore } from './employeeSchedules';
export type { EmployeeSchedule } from './employeeSchedules';

export { usePayrollStore } from './payrolls';
export type { Payroll } from './payrolls';

export { useTransactionStore } from './transactions';
export type { Transaction } from './transactions';

export { useReportStore } from './reports';
export type { ReportMetadata } from './reports';

export { api } from './api';
export type { ApiResponse } from './api';
