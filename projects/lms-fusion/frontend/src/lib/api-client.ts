/**
 * Fusion API Client — HTTP client for django-bolt + django-fusion endpoints.
 */

import { FusionDecoder } from './fusion-decoder';
import type {
  FusionEnvelope, FragmentPointer, PageDataResponse, HealthResponse,
  FusionBranding, FusionWagtailPage, PageListResponse,
} from './fusion-types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5074/api';
const decoder = new FusionDecoder();

class FusionApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  async fetchJson<T>(path: string, options?: RequestInit): Promise<FusionEnvelope<T>> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
    return res.json();
  }

  async checkHealth(): Promise<HealthResponse> {
    const envelope = await this.fetchJson<HealthResponse>('/health');
    const data = decoder.unwrap(envelope);
    if (typeof data.fusion_render_first === 'boolean') {
      decoder.initSession(data.fusion_render_first);
    }
    return data;
  }

  async fetchFragment(slug: string): Promise<FragmentPointer> {
    const envelope = await this.fetchJson<FragmentPointer>(
      `/pages/${encodeURIComponent(slug)}/fragment/`);
    return decoder.decodeFragmentPointer(envelope);
  }

  async fetchPageData(slug: string, renderFirst = false): Promise<PageDataResponse> {
    const params = renderFirst ? '?fusion_render_first=true' : '';
    const envelope = await this.fetchJson<PageDataResponse>(
      `/pages/${encodeURIComponent(slug)}/data/${params}`);
    return decoder.unwrap(envelope);
  }

  async fetchPageHtml(slug: string): Promise<string> {
    const res = await fetch(
      `${this.baseUrl}/pages/${encodeURIComponent(slug)}/data/?fusion_render_first=true`,
      { headers: { 'X-Fusion-Render-First': 'true' } });
    if (!res.ok) throw new Error(`HTML render failed for ${slug}: ${res.status}`);
    return res.text();
  }

  async fetchPageBlocks(slug: string): Promise<Record<string, unknown>> {
    const data = await this.fetchPageData(slug);
    return decoder.decodeAs<Record<string, unknown>>(data.encoded);
  }

  // ─── Wagtail page methods ──────────────────────────────────────────

  /** GET /api/pages/ — list all published Wagtail FusionPages. */
  async fetchPageList(): Promise<PageListResponse> {
    const envelope = await this.fetchJson<PageListResponse>('/pages/');
    return decoder.unwrap(envelope);
  }

  /** GET /api/pages/<slug>/ — get a single Wagtail FusionPage. */
  async fetchWagtailPage(slug: string): Promise<FusionWagtailPage> {
    const envelope = await this.fetchJson<FusionWagtailPage>(
      `/pages/${encodeURIComponent(slug)}/`);
    return decoder.unwrap(envelope);
  }

  /** Decode a Wagtail page from a FusionCodec encoded string. */
  async fetchWagtailPageDecoded(slug: string): Promise<FusionWagtailPage> {
    const data = await this.fetchPageData(slug);
    return decoder.decodeAs<FusionWagtailPage>(data.encoded);
  }

  async fetchBranding(): Promise<FusionBranding> {
    try {
      const envelope = await this.fetchJson<FusionBranding>('/branding');
      return decoder.unwrap(envelope);
    } catch {
      return {
        site_name: process.env.NEXT_PUBLIC_FUSION_SITE_NAME || 'Fusion LMS',
        company_name: 'Fusion Inc.', creator_name: 'Fusion Team',
        primary_color: '#00a1b3',
      };
    }
  }
}

export const fusionApi = new FusionApiClient();
export { FusionApiClient };
export default fusionApi;
