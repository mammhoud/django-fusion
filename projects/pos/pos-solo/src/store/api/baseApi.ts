/**
 * RTK Query base API — single source of truth for all REST endpoints.
 *
 * All entity endpoints inject into this base API. Tag-based cache invalidation
 * ensures that mutations (create/update/delete) automatically refetch affected lists.
 *
 * Pagination: endpoints return { data: T[], pagination: { page, per_page, total, total_pages } }
 */

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { SIDECAR_BASE } from '../../config/sidecar';

const API_BASE = SIDECAR_BASE;

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: API_BASE }),
  tagTypes: [
    'Product', 'Category', 'Customer', 'Sale', 'SaleItem',
    'Employee', 'Inventory', 'MenuItem', 'Menu',
    'Node', 'Heartbeat', 'SyncLog',
    'DeviceConfig', 'MasterDevice', 'CloudLink',
    'SyncApproval', 'Ingredient', 'Recipe', 'Supplier',
    'PurchaseOrder', 'KitchenTicket', 'SupportTicket',
    'DeliveryType', 'EmployeeType', 'ReceiptTemplate',
    'TaxReport', 'EmployeeSchedule', 'Payroll',
    'Transaction', 'Report', 'Settings', 'Analytics', 'Role', 'Note',
  ],
  endpoints: () => ({}),
  keepUnusedDataFor: 60, // 60s cache before garbage collection
});
