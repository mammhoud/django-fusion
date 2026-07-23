/**
 * RTK Query endpoints — Legacy/old-model CRUD operations.
 *
 * These replace Tauri `invoke()` calls for models that don't have dedicated
 * endpoint files yet.  Each endpoint maps to the sidecar HTTP API.
 */
import { api } from '../baseApi';

// ── Ingredients ──
export interface Ingredient {
  id: number;
  name: string; unit: string;
  current_quantity: number; reorder_level: number;
  reorder_quantity: number; cost_per_unit: number;
  is_active: boolean;
}
export interface NewIngredient {
  name: string; unit: string;
  current_quantity: number; reorder_level: number;
  reorder_quantity: number; cost_per_unit: number;
}

// ── Inventory Adjustments ──
export interface InventoryAdjustment {
  id: number; ingredient_id: number;
  previous_quantity: number; new_quantity: number;
  reason: string; created_by: string | null;
  created_at: string;
}

// ── Employee Types ──
export interface EmployeeType {
  id: number; name: string;
  description?: string; is_active: boolean;
}

// ── Transactions ──
export interface Transaction {
  id: number; items: { name: string; price: number; quantity: number; unit: string; subtotal: number }[];
  total_amount: number; currency: string;
  date: string; time: string;
  order_type: string; status: string;
}

// ── Analytics Data ──
export interface AnalyticsData {
  daily_revenue: { date: string; revenue: number; orders: number }[];
  top_products: { name: string; sales: number; revenue: number }[];
  product_distribution: { name: string; value: number }[];
  summary: { total_orders: number; total_revenue: number; average_order_value: number };
}

export const legacyApi = api.injectEndpoints({
  endpoints: (build) => ({

    // ── Ingredients ──
    getIngredients: build.query<Ingredient[], { includeInactive?: boolean }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.includeInactive) p.set('include_inactive', 'true');
        return `/ingredients?${p.toString()}`;
      },
      providesTags: ['Ingredient'],
    }),

    addIngredient: build.mutation<Ingredient, { ingredient: NewIngredient }>({
      query: ({ ingredient }) => ({ url: '/ingredients', method: 'POST', body: ingredient }),
      invalidatesTags: ['Ingredient'],
    }),

    updateIngredient: build.mutation<Ingredient, { id: number; update: Partial<Ingredient> }>({
      query: ({ id, update }) => ({ url: `/ingredients/${id}`, method: 'PATCH', body: update }),
      invalidatesTags: ['Ingredient'],
    }),

    softDeleteIngredient: build.mutation<void, { id: number }>({
      query: ({ id }) => ({ url: `/ingredients/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Ingredient'],
    }),

    // ── Inventory Transactions (legacy Ingredient-based) ──
    getInventoryTransactions: build.query<any[], { ingredientId?: number | null }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.ingredientId) p.set('ingredient_id', String(params.ingredientId));
        return `/inventory?${p.toString()}`;
      },
      providesTags: ['Inventory'],
    }),

    // ── Inventory Adjustments ──
    getInventoryAdjustments: build.query<InventoryAdjustment[], { ingredientId?: number | null }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.ingredientId) p.set('ingredient_id', String(params.ingredientId));
        return `/inventory-adjustments?${p.toString()}`;
      },
      providesTags: ['Inventory'],
    }),

    // ── Employee Types ──
    getEmployeeTypes: build.query<EmployeeType[], { includeInactive?: boolean }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.includeInactive) p.set('include_inactive', 'true');
        return `/employee-types?${p.toString()}`;
      },
      providesTags: ['EmployeeType'],
    }),

    addEmployeeType: build.mutation<EmployeeType, { employeeType: { name: string; description?: string | null } }>({
      query: ({ employeeType }) => ({ url: '/employee-types', method: 'POST', body: employeeType }),
      invalidatesTags: ['EmployeeType'],
    }),

    updateEmployeeType: build.mutation<EmployeeType, { id: number; update: { name?: string; description?: string | null } }>({
      query: ({ id, update }) => ({ url: `/employee-types/${id}`, method: 'PATCH', body: update }),
      invalidatesTags: ['EmployeeType'],
    }),

    softDeleteEmployeeType: build.mutation<void, { id: number }>({
      query: ({ id }) => ({ url: `/employee-types/${id}`, method: 'DELETE' }),
      invalidatesTags: ['EmployeeType'],
    }),

    // ── Employee CRUD (missing mutations) ──
    addEmployee: build.mutation<any, { employee: any }>({
      query: ({ employee }) => ({ url: '/employees', method: 'POST', body: employee }),
      invalidatesTags: ['Employee'],
    }),

    updateEmployee: build.mutation<any, { id: number; update: any }>({
      query: ({ id, update }) => ({ url: `/employees/${id}`, method: 'PATCH', body: update }),
      invalidatesTags: ['Employee'],
    }),

    softDeleteEmployee: build.mutation<void, { id: number }>({
      query: ({ id }) => ({ url: `/employees/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Employee'],
    }),

    // ── Recipes ──
    getRecipes: build.query<any[], { includeInactive?: boolean }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.includeInactive) p.set('include_inactive', 'true');
        return `/recipes?${p.toString()}`;
      },
      providesTags: ['Recipe'],
    }),

    // ── Analytics ──
    getAnalytics: build.query<AnalyticsData, void>({
      query: () => '/analytics',
      providesTags: ['Analytics'],
    }),

    // ── Transactions ──
    getTransactions: build.query<Transaction[], void>({
      query: () => '/transactions',
      providesTags: ['Transaction'],
    }),

  }),
});

export const {
  useGetIngredientsQuery,
  useAddIngredientMutation,
  useUpdateIngredientMutation,
  useSoftDeleteIngredientMutation,
  useGetInventoryTransactionsQuery,
  useGetInventoryAdjustmentsQuery,
  useGetEmployeeTypesQuery,
  useAddEmployeeTypeMutation,
  useUpdateEmployeeTypeMutation,
  useSoftDeleteEmployeeTypeMutation,
  useAddEmployeeMutation,
  useUpdateEmployeeMutation,
  useSoftDeleteEmployeeMutation,
  useGetRecipesQuery,
  useGetAnalyticsQuery,
  useGetTransactionsQuery,
} = legacyApi;
