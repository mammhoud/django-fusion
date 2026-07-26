/**
 * TypeScript API schema types for the Fusion CMS frontend.
 *
 * Mirror of the backend schema contracts used by bolt and REST APIs.
 */

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}

export interface PageData {
  slug: string;
  title: string;
  seo: {
    title: string;
    description: string;
  };
  blocks: PageBlock[];
}

export interface PageBlock {
  type: string;
  [key: string]: unknown;
}

export interface BlogPostResponse {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  published_at: string | null;
}

export interface LayoutInfo {
  available: string[];
  default: string;
}

export interface BrandingResponse {
  site_name: string;
  company_name: string;
  creator_name: string;
  primary_color: string;
  secondary_color?: string;
}
