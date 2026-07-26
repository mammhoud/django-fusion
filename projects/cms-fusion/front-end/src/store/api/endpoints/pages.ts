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

/** Response from the unified ``/apis/pages/<slug>/data/`` endpoint (data mode). */
export interface PageDataResponse {
  /** Page slug. */
  slug: string;
  /** Page title. */
  title: string;
  /** FusionCodec-encoded page data — decode with ``FusionDecoder``. */
  encoded: string;
  /** Active language code used for the response. */
  language?: string;
}

/** Query arguments for page data / fragment endpoints. */
export interface PageQueryArgs {
  slug: string;
  /** Language code (e.g. 'en', 'fr'). Appended as ?lang= query param. */
  lang?: string;
}

/** Fragment pointer returned by ``/apis/pages/<slug>/fragment/``. */
export interface FragmentPointer {
  /** Human-readable component identifier. */
  component: string;
  /** Registered django-fusion fragment name. */
  fragment_name: string;
  /** Absolute or relative URL that returns the server-rendered HTML fragment. */
  fragment_url: string;
  /** When true, the frontend should render the server fragment first. */
  fusion_render_first: boolean;
  /** Extra metadata returned by the backend (mirrors the page slug). */
  page_slug: string;
  /** Page title from the CMS. */
  title: string;
}

export const pagesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getPage: builder.query<CmsPage, string>({
      query: (slug) => `/apis/pages/${slug}/`,
      providesTags: (_result, _error, slug) => [{ type: 'Page' as const, id: slug }],
    }),

    getPageFragment: builder.query<FragmentPointer, string>({
      query: (slug) => `/apis/pages/${slug}/fragment/`,
      transformResponse: (raw: { status: number; message: string; data: FragmentPointer }) =>
        raw.data,
      providesTags: (_result, _error, slug) => [{ type: 'Page' as const, id: slug }],
    }),

    /**
     * Fetch page data via the unified ``/apis/pages/<slug>/data/`` endpoint.
     *
     * Accepts an optional ``lang`` parameter that is appended as a query
     * param so the backend returns language-aware content.
     *
     * Usage::
     *
     *     const { data } = useGetPageDataQuery({ slug: 'home', lang: 'fr' });
     *     const page = fusionDecoder.decodeAs<CmsPage>(data?.encoded ?? '');
     */
    getPageData: builder.query<PageDataResponse, PageQueryArgs>({
      query: ({ slug, lang }) => ({
        url: `/apis/pages/${slug}/data/`,
        params: lang ? { lang } : undefined,
      }),
      transformResponse: (raw: { status: number; message: string; data: PageDataResponse }) =>
        raw.data,
      providesTags: (_result, _error, { slug }) => [{ type: 'Page' as const, id: slug }],
    }),

    /**
     * Fetch server-rendered HTML via the unified endpoint with
     * ``?fusion_render_first=true``. Returns the raw HTML string.
     *
     * Usage::
     *
     *     const { data, isLoading, error } = useGetPageHtmlQuery('home');
     *     if (data) injectHtml(data);
     */
    getPageHtml: builder.query<string, string>({
      query: (slug) => ({
        url: `/apis/pages/${slug}/data/`,
        params: { fusion_render_first: 'true' },
        responseHandler: 'text' as const,
      }),
      providesTags: (_result, _error, slug) => [
        { type: 'Page' as const, id: `${slug}-html` },
      ],
    }),
  }),
});

export const {
  useGetPageQuery,
  useGetPageFragmentQuery,
  useGetPageDataQuery,
  useGetPageHtmlQuery,
} = pagesApi;
