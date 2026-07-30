import { api } from '../baseApi';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface UserInfo {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
}

/**
 * JWT auth response — returned by login, register, and refresh endpoints.
 */
export interface AuthResponse {
  access: string;
  refresh: string;
  user: UserInfo;
  expires_in: number;
}

/**
 * Refresh request body.
 */
export interface RefreshRequest {
  refresh: string;
}

/**
 * User profile — returned by GET /apis/auth/me and /apis/auth/profile.
 */
export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'instructor' | 'admin';
  avatar: string;
  bio: string;
  date_joined: string;
  last_login: string;
}

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }],
    }),
    register: builder.mutation<AuthResponse, RegisterRequest>({
      query: (data) => ({
        url: '/auth/register',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }, { type: 'User', id: 'LIST' }],
    }),
    logout: builder.mutation<void, void>({
      query: () => ({ url: '/auth/logout', method: 'POST' }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }],
    }),
    refreshToken: builder.mutation<AuthResponse, RefreshRequest>({
      query: (data) => ({
        url: '/auth/refresh',
        method: 'POST',
        body: data,
      }),
    }),
    getProfile: builder.query<UserProfile, void>({
      query: () => '/auth/profile',
      providesTags: [{ type: 'Auth', id: 'CURRENT' }],
    }),
    updateProfile: builder.mutation<UserProfile, Partial<UserProfile>>({
      query: (data) => ({ url: '/auth/profile', method: 'PATCH', body: data }),
      invalidatesTags: [{ type: 'Auth', id: 'CURRENT' }, { type: 'User', id: 'LIST' }],
    }),
    resetPassword: builder.mutation<void, { email: string }>({
      query: (data) => ({ url: '/auth/password-reset', method: 'POST', body: data }),
    }),
    changePassword: builder.mutation<void, { old_password: string; new_password: string }>({
      query: (data) => ({ url: '/auth/change-password', method: 'POST', body: data }),
    }),
  }),
});

export const {
  useLoginMutation,
  useRegisterMutation,
  useLogoutMutation,
  useRefreshTokenMutation,
  useGetProfileQuery,
  useUpdateProfileMutation,
  useResetPasswordMutation,
  useChangePasswordMutation,
} = authApi;
