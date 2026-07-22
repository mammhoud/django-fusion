import { api } from '../baseApi';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'instructor';
}

export interface AuthResponse {
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    avatar: string;
  };
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar: string;
  bio: string;
  role: 'student' | 'instructor' | 'admin';
  date_joined: string;
  last_login: string;
}

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/apis/auth/login/',
        method: 'POST',
        body: credentials,
      }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }],
    }),
    register: builder.mutation<AuthResponse, RegisterRequest>({
      query: (data) => ({
        url: '/apis/auth/register/',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }, { type: 'User', id: 'LIST' }],
    }),
    logout: builder.mutation<void, void>({
      query: () => ({ url: '/apis/auth/logout/', method: 'POST' }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }],
    }),
    getProfile: builder.query<UserProfile, void>({
      query: () => '/apis/auth/profile/',
      providesTags: [{ type: 'Auth', id: 'CURRENT' }],
    }),
    updateProfile: builder.mutation<UserProfile, Partial<UserProfile>>({
      query: (data) => ({ url: '/apis/auth/profile/', method: 'PATCH', body: data }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }, { type: 'User', id: 'LIST' }],
    }),
    resetPassword: builder.mutation<void, { email: string }>({
      query: (data) => ({ url: '/apis/auth/password-reset/', method: 'POST', body: data }),
    }),
    changePassword: builder.mutation<void, { old_password: string; new_password: string }>({
      query: (data) => ({ url: '/apis/auth/change-password/', method: 'POST', body: data }),
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useGetProfileQuery,
  useUpdateProfileMutation,
  useResetPasswordMutation,
  useChangePasswordMutation,
} = authApi;
