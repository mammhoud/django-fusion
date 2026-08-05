import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/test/**/*.test.{ts,tsx}', 'src/**/*.test.{ts,tsx}'],
    exclude: ['node_modules', 'src-tauri'],
    css: false,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // In jsdom tests, @tauri-apps/plugin-store is not available.
      // The code catches the dynamic import, but Vite's dependency
      // analysis still tries to resolve it. Alias to a mock.
      '@tauri-apps/plugin-store': path.resolve(__dirname, './src/test/mocks/tauri-plugin-store.ts'),
    },
  },
});
