/** RTK Query endpoints — Roles, Permissions. */
import { api } from '../baseApi';

export interface Role {
  id: number; name: string; permissions: string[];
  is_active: boolean; created_at: string; updated_at: string;
}

export const rolesApi = api.injectEndpoints({
  endpoints: (build) => ({
    getRoles: build.query<Role[], void>({
      query: () => '/roles',
      providesTags: (result) =>
        result
          ? [...result.map(({ id }) => ({ type: 'Role' as const, id })), { type: 'Role', id: 'LIST' }]
          : [{ type: 'Role', id: 'LIST' }],
    }),

    addRole: build.mutation<Role, Partial<Role>>({
      query: (body) => ({ url: '/roles', method: 'POST', body }),
      invalidatesTags: [{ type: 'Role', id: 'LIST' }],
    }),

    updateRole: build.mutation<Role, { id: number; data: Partial<Role> }>({
      query: ({ id, data }) => ({ url: `/roles/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: [{ type: 'Role', id: 'LIST' }],
    }),

    deleteRole: build.mutation<void, number>({
      query: (id) => ({ url: `/roles/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Role', id: 'LIST' }],
    }),
  }),
});

export const { useGetRolesQuery, useAddRoleMutation, useUpdateRoleMutation, useDeleteRoleMutation } = rolesApi;
