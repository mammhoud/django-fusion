import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    include: ['src/test/**/*.test.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@tauri-apps/plugin-store': path.resolve(__dirname, 'src/test/mocks/plugin-store.ts'),
    },
  },
});
