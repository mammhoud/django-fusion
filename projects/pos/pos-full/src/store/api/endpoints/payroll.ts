/** RTK Query endpoints — Payroll, Tax Reports, Employee Schedules. */
import { api } from '../baseApi';

export interface Payroll { id: number; employee_id: number; period_start: string; period_end: string; regular_hours: number; overtime_hours: number; total_pay: number; status: string; created_at: string; updated_at: string; }
export interface TaxReport { id: number; period_start: string; period_end: string; total_sales: number; total_tax: number; transaction_count: number; generated_at: string; }
export interface EmployeeSchedule { id: number; employee_id: number; shift_start: string; shift_end: string; status: string; notes?: string | null; created_at: string; updated_at: string; }

export const payrollApi = api.injectEndpoints({
  endpoints: (build) => ({
    getPayrollRecords: build.query<Payroll[], void>({
      query: () => '/payroll',
      providesTags: ['Payroll'],
    }),
    addPayroll: build.mutation<Payroll, Partial<Payroll>>({
      query: (body) => ({ url: '/payroll', method: 'POST', body }),
      invalidatesTags: ['Payroll'],
    }),
    deletePayroll: build.mutation<void, number>({
      query: (id) => ({ url: `/payroll/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Payroll'],
    }),
    getTaxReports: build.query<TaxReport[], void>({
      query: () => '/tax-reports',
      providesTags: ['TaxReport'],
    }),
    addTaxReport: build.mutation<TaxReport, Partial<TaxReport>>({
      query: (body) => ({ url: '/tax-reports', method: 'POST', body }),
      invalidatesTags: ['TaxReport'],
    }),
    deleteTaxReport: build.mutation<void, number>({
      query: (id) => ({ url: `/tax-reports/${id}`, method: 'DELETE' }),
      invalidatesTags: ['TaxReport'],
    }),
    getEmployeeSchedules: build.query<EmployeeSchedule[], { employee_id?: number }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.employee_id) p.set('employee_id', String(params.employee_id));
        return `/employee-schedules?${p.toString()}`;
      },
      providesTags: ['EmployeeSchedule'],
    }),
    addEmployeeSchedule: build.mutation<EmployeeSchedule, Partial<EmployeeSchedule>>({
      query: (body) => ({ url: '/employee-schedules', method: 'POST', body }),
      invalidatesTags: ['EmployeeSchedule'],
    }),
    deleteEmployeeSchedule: build.mutation<void, number>({
      query: (id) => ({ url: `/employee-schedules/${id}`, method: 'DELETE' }),
      invalidatesTags: ['EmployeeSchedule'],
    }),
  }),
});

export const { useGetPayrollRecordsQuery, useAddPayrollMutation, useDeletePayrollMutation, useGetTaxReportsQuery, useAddTaxReportMutation, useDeleteTaxReportMutation, useGetEmployeeSchedulesQuery, useAddEmployeeScheduleMutation, useDeleteEmployeeScheduleMutation } = payrollApi;
