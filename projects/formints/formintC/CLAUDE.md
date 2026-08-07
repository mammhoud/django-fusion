# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development

- `pnpm dev` - Start development server for Vue frontend (runs on port 1420)
- `pnpm build` - Build Vue frontend for production (includes TypeScript compilation)
- `pnpm preview` - Preview production build

### Tauri Development

- `pnpm tauri dev` - Start Tauri development environment (frontend + backend)
- `pnpm tauri build` - Build Tauri application for production
- `pnpm tauri` - Access Tauri CLI commands

### Code Quality

- `pnpm lint` - Run oxlint for linting
- `pnpm lint:fix` - Run oxlint with auto-fix
- `pnpm format` - Format code with Prettier
- `vue-tsc --noEmit` - TypeScript type checking (part of build process)

### Testing

- No test framework is currently configured in this project

## Architecture Overview

This is a **Tauri v2 application** combining a Vue 3 frontend with a Rust backend, using modern web technologies.

### Frontend Stack

- **Vue 3** with TypeScript and Composition API (`<script setup>`)
- **Vue Router** for client-side routing
- **Vite** as build tool and development server
- **Tailwind CSS v4** + **daisyUI** for styling and components
- **Pinia** for state management
- **Vue i18n** for internationalization (supports zh-CN and en-US)
- **Heroicons** for icons
- **pnpm** for package management

### Backend Stack

- **Rust** with Tauri v2 framework
- **Cargo** for Rust package management
- **Tauri plugins**: store, fs, opener, log

### Project Structure

- `src/` - Vue frontend source code
    - `main.ts` - Vue app entry point with Pinia, i18n, and router setup
    - `App.vue` - Root component
    - `router/` - Vue Router configuration
    - `views/` - Page components (HomeView, SettingsView)
    - `components/` - Reusable Vue components (TitleBar)
    - `layouts/` - Layout components (MainLayout)
    - `assets/` - Static assets (CSS, images)
    - `utils/` - Utility functions (i18n, settings, theme)
    - `locales/` - Internationalization files (zh-CN, en-US)
- `src-tauri/` - Rust backend source code
    - `src/main.rs` - Tauri app entry point
    - `src/lib.rs` - Main Rust library with Tauri commands
    - `Cargo.toml` - Rust dependencies
    - `tauri.conf.json` - Tauri configuration
    - `icons/` - App icons for different platforms

### Key Configuration

- **Vite config** (`vite.config.ts`): Configured for Tauri development with fixed port (1420) and HMR
- **Tauri config** (`src-tauri/tauri.conf.json`): App metadata, window settings, build commands
- **TypeScript**: Strict mode enabled with modern ES2020 target
- **Tailwind**: v4 configuration with daisyUI components and prettier plugin
- **Package manager**: pnpm with proper lockfile management

### Frontend-Backend Communication

- Tauri commands defined in `src-tauri/src/lib.rs` (e.g., `greet` command)
- Frontend calls Rust functions using Tauri API
- Available Tauri plugins: store (persistent data), fs (file system), opener (URLs/files), log (logging)

### Development Workflow

1. Use `pnpm tauri dev` for full-stack development
2. Frontend runs on localhost:1420 with hot reload
3. Rust backend compiles and runs automatically
4. Changes to either frontend or backend trigger appropriate rebuilds
5. Use `pnpm lint` and `pnpm format` for code quality

### Key Features

- **Internationalization**: Built-in support for Chinese (zh-CN) and English (en-US)
- **State Management**: Pinia store with settings persistence via Tauri store plugin
- **Theme System**: Dynamic theme switching utility with daisyUI themes
- **Routing**: Vue Router with Home and Settings views
- **Code Quality**: Configured with oxlint and Prettier with Tailwind plugin
- **Icons**: Heroicons integration for consistent iconography
- **Window Management**: Custom title bar component with window controls

## Important Notes

- The application uses **pnpm** (not npm) - ensure pnpm is installed
- Tauri requires Rust toolchain to be installed
- Development server runs on fixed port 1420 (configured in Vite)
- Default language is Chinese (zh-CN) with English fallback
- Settings are persisted using Tauri's store plugin
- No test framework is currently configured - add testing setup if needed
- Window size is set to 800x600 by default in tauri.conf.json
