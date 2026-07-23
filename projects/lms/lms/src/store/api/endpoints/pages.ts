import { api } from '../baseApi';

export interface PageCta {
  label: string;
  href: string;
  variant?: 'primary' | 'secondary' | 'link';
}

export interface PageBlock {
  type: string;
  key?: string;
  heading?: string;
  title?: string;
  intro?: string;
  html?: string;
  cta?: PageCta;
  ctas?: PageCta[];
  items?: any[];
  groups?: { title: string; items: { question: string; answer: string }[] }[];
}

export interface CmsPage {
  slug: string;
  title: string;
  seo: {
    title: string;
    description: string;
  };
  last_updated?: string;
  blocks: PageBlock[];
}

export const pagesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getPage: builder.query<CmsPage, string>({
      query: (slug) => `/apis/pages/${slug}/`,
      providesTags: (_result, _error, slug) => [{ type: 'Page' as const, id: slug }],
    }),
  }),
});

export const { useGetPageQuery } = pagesApi;
