/**
 * RTK Query endpoints — Categories, Settings, Employees, DeliveryTypes.
 * Replaces: useCategoryStore, useSettingsStore, useEmployeeStore, useDeliveryTypeStore (Zustand)
 */

import { api, PaginatedResponse } from '../baseApi';

// ── Categories ──
export interface Category { id: number; name: string; created_at: string; updated_at: string; }

export const categoriesApi = api.injectEndpoints({
  endpoints: (build) => ({
    getCategories: build.query<Category[], void>({
      query: () => '/categories',
      providesTags: (result) =>
        result
          ? [...result.map(({ id }) => ({ type: 'Category' as const, id })), { type: 'Category', id: 'LIST' }]
          : [{ type: 'Category', id: 'LIST' }],
    }),
  }),
});

export const { useGetCategoriesQuery } = categoriesApi;

// ── Settings ──
export interface Settings {
  id: number; restaurant_name: string | null; address: string | null;
  phone: string | null; email: string | null; tax_rate: string | null;
  currency: string; receipt_footer: string | null; logo: string | null;
}

export const settingsApi = api.injectEndpoints({
  endpoints: (build) => ({
    getSettings: build.query<Settings | null, void>({
      query: () => '/settings',
      providesTags: ['Settings'],
    }),
    updateSettings: build.mutation<Settings, Partial<Settings>>({
      query: (body) => ({ url: '/settings', method: 'PATCH', body }),
      invalidatesTags: ['Settings'],
    }),
  }),
});

export const { useGetSettingsQuery, useUpdateSettingsMutation } = settingsApi;

// ── Employees ──
export interface Employee {
  id: number; name: string; phone: string | null; email: string | null;
  employee_type_id: number; salary: number; is_active: boolean;
}

export const employeesApi = api.injectEndpoints({
  endpoints: (build) => ({
    getEmployees: build.query<Employee[], void>({
      query: () => '/employees?include_inactive=false',
      providesTags: (result) =>
        result
          ? [...result.map(({ id }) => ({ type: 'Employee' as const, id })), { type: 'Employee', id: 'LIST' }]
          : [{ type: 'Employee', id: 'LIST' }],
    }),
  }),
});

export const { useGetEmployeesQuery } = employeesApi;

// ── Delivery Types ──
export interface DeliveryType {
  id: number; name: string; description: string | null;
  fee_multiplier: number; is_active: boolean;
}

export const deliveryTypesApi = api.injectEndpoints({
  endpoints: (build) => ({
    getDeliveryTypes: build.query<DeliveryType[], void>({
      query: () => '/delivery-types?include_inactive=false',
      providesTags: (result) =>
        result
          ? [...result.map(({ id }) => ({ type: 'DeliveryType' as const, id })), { type: 'DeliveryType', id: 'LIST' }]
          : [{ type: 'DeliveryType', id: 'LIST' }],
    }),
  }),
});

export const { useGetDeliveryTypesQuery } = deliveryTypesApi;
