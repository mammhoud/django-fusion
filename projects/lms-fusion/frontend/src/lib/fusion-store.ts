/**
 * Fusion Store — lightweight state management for fusion rendering mode.
 *
 * Tracks whether the frontend should render server HTML first (fusion mode)
 * or fetch JSON data and render client-side (data mode).
 */

import { fusionDecoder } from './fusion-decoder';
import type { FusionMode } from './fusion-types';

type Listener = () => void;

class FusionStore {
  private mode: FusionMode = 'loading';
  private renderFirst = false;
  private listeners = new Set<Listener>();

  getMode(): FusionMode {
    return this.mode;
  }

  getRenderFirst(): boolean {
    return this.renderFirst;
  }

  setMode(mode: FusionMode): void {
    this.mode = mode;
    this.notify();
  }

  setRenderFirst(value: boolean): void {
    this.renderFirst = value;
    fusionDecoder.initSession(value);
    this.notify();
  }

  /** Initialize from health check response. */
  initFromHealth(prefersFragment: boolean): void {
    this.renderFirst = prefersFragment;
    this.mode = prefersFragment ? 'fragment' : 'data';
    fusionDecoder.initSession(prefersFragment);
    this.notify();
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => { this.listeners.delete(listener); };
  }

  private notify(): void {
    this.listeners.forEach((fn) => fn());
  }
}

export const fusionStore = new FusionStore();
export default fusionStore;
