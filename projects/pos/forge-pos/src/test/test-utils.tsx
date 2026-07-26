/**
 * Test utilities for rendering page components in vitest + React Testing Library.
 *
 * Wraps components in a MemoryRouter + ThemeProvider, and mocks heavy/animation
 * dependencies so tests can focus on functional behaviour.
 */
import { ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';
import { ThemeProvider } from '../contexts/ThemeContext';
import { LanguageProvider } from '../contexts/LanguageContext';
import { AuthProvider } from '../contexts/AuthContext';

// ---------------------------------------------------------------------------
// Framer Motion – silently render children without animation
// ---------------------------------------------------------------------------
vi.mock('framer-motion', async () => {
  const actual = await vi.importActual('framer-motion');
  return {
    ...actual,
    motion: {
      div: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        // Strip animation-only props so they don't generate console noise
        const { initial, animate, exit, whileHover, whileTap, variants, transition, layout, layoutId, ...rest } = props as Record<string, unknown>;
        return <div {...rest}>{children}</div>;
      },
      button: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, layout, layoutId, ...rest } = props as Record<string, unknown>;
        return <button {...rest}>{children}</button>;
      },
      span: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, ...rest } = props as Record<string, unknown>;
        return <span {...rest}>{children}</span>;
      },
      p: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, ...rest } = props as Record<string, unknown>;
        return <p {...rest}>{children}</p>;
      },
      h1: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, ...rest } = props as Record<string, unknown>;
        return <h1 {...rest}>{children}</h1>;
      },
      h2: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, ...rest } = props as Record<string, unknown>;
        return <h2 {...rest}>{children}</h2>;
      },
      h3: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, ...rest } = props as Record<string, unknown>;
        return <h3 {...rest}>{children}</h3>;
      },
      img: (props: Record<string, unknown>) => <img {...props} />,
      svg: ({ children, ...props }: { children?: ReactNode; [key: string]: unknown }) => {
        const { initial, animate, exit, whileHover, whileTap, variants, transition, layout, layoutId, ...rest } = props as Record<string, unknown>;
        return <svg {...rest}>{children}</svg>;
      },
    },
    AnimatePresence: ({ children }: { children?: ReactNode }) => <>{children}</>,
    useAnimation: () => ({}),
  };
});

// ---------------------------------------------------------------------------
// i18n – mock the whole module so components & contexts don't trigger
// react-i18next dependency resolution during tests
// ---------------------------------------------------------------------------
const { mockChangeLanguage, mockOn, mockOff, mockNavigate } = vi.hoisted(() => ({
  mockChangeLanguage: vi.fn(),
  mockOn: vi.fn(),
  mockOff: vi.fn(),
  mockNavigate: vi.fn(),
}));

vi.mock('../i18n', () => ({
  __esModule: true,
  default: {
    language: 'en',
    changeLanguage: mockChangeLanguage,
    on: mockOn,
    off: mockOff,
    dir: () => 'ltr',
    use: () => ({
      init: vi.fn(),
    }),
    t: (key: string) => key,
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      language: 'en',
      changeLanguage: mockChangeLanguage,
      on: mockOn,
      off: mockOff,
      dir: () => 'ltr',
    },
  }),
}));

// ---------------------------------------------------------------------------
// react-router-dom – stub useNavigate
// ---------------------------------------------------------------------------
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

export { mockNavigate };

// ---------------------------------------------------------------------------
// Tauri plugins – stub dialog & fs so components don't crash
// ---------------------------------------------------------------------------
vi.mock('@tauri-apps/plugin-dialog', () => ({
  open: vi.fn().mockResolvedValue(null),
  save: vi.fn().mockResolvedValue('/tmp/test-file.pdf'),
}));

vi.mock('@tauri-apps/plugin-fs', () => ({
  readFile: vi.fn().mockResolvedValue(new Uint8Array()),
  writeFile: vi.fn().mockResolvedValue(undefined),
}));

// ---------------------------------------------------------------------------
// jspdf – stub save so PDF generation doesn't throw
// ---------------------------------------------------------------------------
vi.mock('jspdf', () => {
  const MockJsPDF = vi.fn().mockImplementation(() => ({
    setFontSize: vi.fn().mockReturnThis(),
    setFont: vi.fn().mockReturnThis(),
    setDrawColor: vi.fn().mockReturnThis(),
    setLineWidth: vi.fn().mockReturnThis(),
    text: vi.fn().mockReturnThis(),
    line: vi.fn().mockReturnThis(),
    addPage: vi.fn().mockReturnThis(),
    splitTextToSize: vi.fn().mockReturnValue([]),
    output: vi.fn().mockReturnValue(new ArrayBuffer(0)),
    save: vi.fn(),
    internal: {
      pageSize: { getWidth: () => 80, getHeight: () => 297 },
    },
  }));
  return { default: MockJsPDF };
});

// ---------------------------------------------------------------------------
// recharts – stub ResponsiveContainer so it renders children
// ---------------------------------------------------------------------------
vi.mock('recharts', async () => {
  const actual = await vi.importActual('recharts');
  const MockResponsiveContainer = ({ children }: { children?: ReactNode; [key: string]: unknown }) =>
    <div>{children}</div>;
  return {
    ...actual,
    ResponsiveContainer: MockResponsiveContainer,
  };
});

// ---------------------------------------------------------------------------
// Custom render that wraps in MemoryRouter + ThemeProvider
// ---------------------------------------------------------------------------
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[];
}

export function renderWithRouter(
  ui: ReactNode,
  options?: CustomRenderOptions,
) {
  const { initialEntries = ['/'], ...renderOptions } = options ?? {};
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <MemoryRouter initialEntries={initialEntries}>
        <ThemeProvider>
          <LanguageProvider>
            <AuthProvider>{children}</AuthProvider>
          </LanguageProvider>
        </ThemeProvider>
      </MemoryRouter>
    );
  }
  return render(ui, { wrapper: Wrapper, ...renderOptions });
}

export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
