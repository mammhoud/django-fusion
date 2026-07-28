import { FusionDecoder } from './fusion-decoder';
import type {
  FusionEnvelope, FragmentPointer, PageDataResponse, HealthResponse,
  FusionBranding, FusionWagtailPage, PageListResponse,
} from './fusion-types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5075/api';
const decoder = new FusionDecoder();

class FusionApiClient {
  private baseUrl: string;
  constructor(baseUrl: string = API_BASE) { this.baseUrl = baseUrl; }

  async fetchJson<T>(path: string, options?: RequestInit): Promise<FusionEnvelope<T>> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers }, ...options,
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  }

  async checkHealth(): Promise<HealthResponse> {
    const envelope = await this.fetchJson<HealthResponse>('/fusion/health');
    const data = decoder.unwrap(envelope);
    if (typeof data.fusion_render_first === 'boolean') decoder.initSession(data.fusion_render_first);
    return data;
  }

  async fetchFragment(slug: string): Promise<FragmentPointer> {
    const envelope = await this.fetchJson<FragmentPointer>(`/pages/${encodeURIComponent(slug)}/fragment/`);
    return decoder.decodeFragmentPointer(envelope);
  }

  async fetchPageData(slug: string, renderFirst = false): Promise<PageDataResponse> {
    const params = renderFirst ? '?fusion_render_first=true' : '';
    const envelope = await this.fetchJson<PageDataResponse>(`/pages/${encodeURIComponent(slug)}/data/${params}`);
    return decoder.unwrap(envelope);
  }

  async fetchPageHtml(slug: string): Promise<string> {
    const res = await fetch(`${this.baseUrl}/pages/${encodeURIComponent(slug)}/data/?fusion_render_first=true`,
      { headers: { 'X-Fusion-Render-First': 'true' } });
    if (!res.ok) throw new Error(`HTML render failed: ${res.status}`);
    return res.text();
  }

  async fetchPageList(): Promise<PageListResponse> {
    const envelope = await this.fetchJson<PageListResponse>('/pages/');
    return decoder.unwrap(envelope);
  }

  async fetchWagtailPage(slug: string): Promise<FusionWagtailPage> {
    const envelope = await this.fetchJson<FusionWagtailPage>(`/pages/${encodeURIComponent(slug)}/`);
    return decoder.unwrap(envelope);
  }

  async fetchWagtailPageDecoded(slug: string): Promise<FusionWagtailPage> {
    const data = await this.fetchPageData(slug);
    return decoder.decodeAs<FusionWagtailPage>(data.encoded);
  }

  /** Decode page blocks from a FusionCodec encoded page data response. */
  async fetchPageBlocks(slug: string): Promise<Record<string, unknown>> {
    const data = await this.fetchPageData(slug);
    return decoder.decodeAs<Record<string, unknown>>(data.encoded);
  }

  async fetchBranding(): Promise<FusionBranding> {
    try {
      const envelope = await this.fetchJson<FusionBranding>('/fusion/branding');
      return decoder.unwrap(envelope);
    } catch {
      return {
        site_name: process.env.NEXT_PUBLIC_FUSION_SITE_NAME || 'Fusion CMS',
        company_name: 'Fusion Inc.',
        creator_name: 'Fusion Team',
        primary_color: '#7c3aed',
      };
    }
  }
}

export const fusionApi = new FusionApiClient();
export { FusionApiClient };
export default fusionApi;
