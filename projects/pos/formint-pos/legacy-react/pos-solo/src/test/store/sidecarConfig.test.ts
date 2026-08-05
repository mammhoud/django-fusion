import { configureStore } from '@reduxjs/toolkit';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { SIDECAR_BASE, SIDECAR_WS_BASE } from '../../config/sidecar';
import { sidecar } from '../../api/sidecar';
import { api } from '../../store/api/baseApi';
import { productsApi } from '../../store/api/endpoints/products';
import { categoriesApi, settingsApi } from '../../store/api/endpoints/core';

const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

function makeStore() {
  return configureStore({
    reducer: { [api.reducerPath]: api.reducer },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(api.middleware),
  });
}

function jsonResponse(data: unknown) {
  return Promise.resolve(new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  }));
}

function requestUrl(call: unknown[]): string {
  const request = call[0];
  return request instanceof Request ? request.url : String(request);
}

describe('POS Solo sidecar connection config', () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it('keeps legacy HTTP, WebSocket, and RTK Query on the same sidecar origin', () => {
    expect(SIDECAR_BASE).toBe('http://127.0.0.1:8766');
    expect(SIDECAR_WS_BASE).toBe('ws://127.0.0.1:8766');
    expect(sidecar.base).toBe(SIDECAR_BASE);
    expect(sidecar.wsBase).toBe(SIDECAR_WS_BASE);
  });

  it('loads products from the configured sidecar URL', async () => {
    fetchMock.mockImplementationOnce(() => jsonResponse({
      data: [{ id: 1, name: 'Burger', price: 10, unit: 'piece', category_id: null, image: null, created_at: '', updated_at: '', uploaded: false }],
      pagination: { page: 1, per_page: 200, total: 1, total_pages: 1 },
    }));

    const store = makeStore();
    const result = await store.dispatch(
      productsApi.endpoints.getProducts.initiate({ page: 1, per_page: 200 }),
    );

    expect(result.data?.data[0].name).toBe('Burger');
    expect(requestUrl(fetchMock.mock.calls[0])).toBe(`${SIDECAR_BASE}/products?page=1&per_page=200`);
  });

  it('loads settings and categories from the configured sidecar URL', async () => {
    fetchMock
      .mockImplementationOnce(() => jsonResponse({ id: 1, restaurant_name: 'Structa POS', currency: 'USD' }))
      .mockImplementationOnce(() => jsonResponse([{ id: 7, name: 'Food', created_at: '', updated_at: '' }]));

    const store = makeStore();
    const settings = await store.dispatch(settingsApi.endpoints.getSettings.initiate());
    const categories = await store.dispatch(categoriesApi.endpoints.getCategories.initiate());

    expect(settings.data?.restaurant_name).toBe('Structa POS');
    expect(categories.data?.[0].name).toBe('Food');
    expect(requestUrl(fetchMock.mock.calls[0])).toBe(`${SIDECAR_BASE}/settings`);
    expect(requestUrl(fetchMock.mock.calls[1])).toBe(`${SIDECAR_BASE}/categories`);
  });
});
