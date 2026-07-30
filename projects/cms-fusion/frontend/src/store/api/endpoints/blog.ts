import { api, PaginatedResponse } from '../baseApi';

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  author: number;
  author_name: string;
  author_avatar: string;
  category: number;
  category_name: string;
  tags: string[];
  featured_image: string;
  is_published: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
}

export interface BlogCategory {
  id: number;
  name: string;
  slug: string;
  post_count: number;
}

export const blogApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getBlogPosts: builder.query<PaginatedResponse<BlogPost>, { page?: number; category?: string; search?: string }>({
      query: (params) => ({
        url: '/blog/',
        params: { page: params.page || 1, category: params.category, search: params.search },
      }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Blog' as const, id })), { type: 'Blog', id: 'LIST' }] : [{ type: 'Blog', id: 'LIST' }],
    }),
    getBlogPost: builder.query<BlogPost, number>({
      query: (id) => `/blog/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Blog', id }],
    }),
    getBlogCategories: builder.query<BlogCategory[], void>({
      query: () => '/blog/categories/',
      providesTags: [{ type: 'BlogCategory', id: 'LIST' }],
    }),
    getFeaturedPosts: builder.query<BlogPost[], void>({
      query: () => '/blog/featured/',
      providesTags: [{ type: 'Blog', id: 'LIST' }],
    }),
    getRelatedPosts: builder.query<BlogPost[], number>({
      query: (id) => `/blog/${id}/related/`,
      providesTags: [{ type: 'Blog', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetBlogPostsQuery,
  useGetBlogPostQuery,
  useGetBlogCategoriesQuery,
  useGetFeaturedPostsQuery,
  useGetRelatedPostsQuery,
} = blogApi;
