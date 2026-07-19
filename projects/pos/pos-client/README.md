# Tauri Vue3 App Template

[中文文档](README_CN.md) | **English**

A modern cross-platform desktop application template built with Tauri v2 and Vue 3, featuring internationalization, theme switching, and a multi-page clean responsive UI.

## Features

- **Modern Stack**: Tauri v2 + Vue 3 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 + daisyUI components
- **Internationalization**: Built-in i18n support (English & Chinese)
- **State Management**: Pinia store with persistent settings without localStorage dependency
- **Theme System**: Dynamic theme switching with daisyUI themes
- **Responsive Design**: Mobile-first responsive layout
- **Developer Experience**: Hot reload, TypeScript, OxLint, Prettier
- **Custom Window**: Custom title bar with window controls
- **Cross-Platform**: Build for Windows, macOS, and Linux

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or higher)
- [pnpm](https://pnpm.io/) package manager
- [Rust](https://rustup.rs/) toolchain

### Installation

1. **Clone the repository**

    ```bash
    git clone https://github.com/KitsuneX07/tauri-vue-app.git
    cd tauri-vue-app
    ```

2. **Install dependencies**

    ```bash
    pnpm install
    ```

3. **Start development server**

    ```bash
    pnpm tauri dev
    ```

4. **Build for production**
    ```bash
    pnpm tauri build
    ```

## Development Commands

### Frontend Development

```bash
pnpm dev          # Start Vue development server (port 1420)
pnpm build        # Build Vue frontend for production
pnpm preview      # Preview production build
```

### Tauri Development

```bash
pnpm tauri dev    # Start Tauri development environment
pnpm tauri build  # Build Tauri application
pnpm tauri        # Access Tauri CLI commands
```

### Code Quality

```bash
pnpm lint         # Run oxlint for linting
pnpm lint:fix     # Run oxlint with auto-fix
pnpm format       # Format code with Prettier
vue-tsc --noEmit  # TypeScript type checking
```

## Project Structure

```
tauri-vue-app/
├── src/                    # Vue frontend source code
│   ├── components/         # Reusable Vue components
│   │   └── TitleBar.vue   # Custom title bar component
│   ├── layouts/           # Layout components
│   │   └── MainLayout.vue # Main application layout
│   ├── views/             # Page components
│   │   ├── HomeView.vue   # Home page
│   │   └── SettingsView.vue # Settings page
│   ├── utils/             # Utility functions
│   │   ├── i18n.ts        # Internationalization setup
│   │   ├── settings.ts    # Settings management
│   │   └── theme.ts       # Theme switching utilities
│   ├── locales/           # Translation files
│   │   ├── en-US.ts       # English translations
│   │   └── zh-CN.ts       # Chinese translations
│   ├── router/            # Vue Router configuration
│   │   └── index.ts       # Router setup
│   ├── assets/            # Static assets
│   │   └── main.css       # Global styles
│   ├── App.vue            # Root component
│   └── main.ts            # Vue app entry point
├── src-tauri/             # Rust backend source code
│   ├── src/
│   │   ├── main.rs        # Tauri app entry point
│   │   └── lib.rs         # Main Rust library
│   ├── icons/             # App icons
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri configuration
├── public/                # Public assets
├── package.json           # Node.js dependencies
├── vite.config.ts         # Vite configuration
├── tailwind.config.ts     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── README.md              # This file
```

## Technology Stack

### Frontend

- **Vue 3** - Progressive JavaScript framework with Composition API
- **TypeScript** - Type-safe JavaScript development
- **Vite** - Fast build tool and development server
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Vue i18n** - Internationalization
- **Tailwind CSS v4** - Utility-first CSS framework
- **daisyUI** - Tailwind CSS components
- **Heroicons** - Beautiful hand-crafted SVG icons

### Backend

- **Rust** - Systems programming language
- **Tauri v2** - Cross-platform desktop app framework
- **Tauri Plugins**:
    - `store` - Persistent key-value storage
    - `fs` - File system operations
    - `opener` - Open URLs and files
    - `log` - Logging functionality

### Development Tools

- **oxlint** - Fast JavaScript/TypeScript linter
- **Prettier** - Code formatter with Tailwind plugin
- **pnpm** - Fast, disk space efficient package manager

## Configuration

### Internationalization

The app supports multiple languages out of the box:

- English (en-US)
- Chinese (zh-CN)

Add new languages by creating translation files in `src/locales/` and updating the i18n configuration.

### Theme System

Built-in theme switching with daisyUI themes:

- Light themes: light, pastel, emerald
- Dark themes: dark, forest, luxury

Customize themes in `src/utils/theme.ts`.

### Settings Persistence

User settings are automatically saved using Tauri's store plugin:

- Language preference
- Theme selection
- Window state
- Custom configurations

## Building and Distribution

### Development Build

```bash
pnpm tauri dev
```

### Production Build

```bash
pnpm tauri build
```

Build outputs are generated in `src-tauri/target/release/bundle/`:

- **Windows**: `.msi` installer and `.exe` executable
- **macOS**: `.dmg` installer and `.app` bundle
- **Linux**: `.deb`, `.rpm`, and `.AppImage` packages

### Customization

1. **App Identity**: Update `src-tauri/tauri.conf.json`
2. **Icons**: Replace files in `src-tauri/icons/`
3. **Window Settings**: Modify window configuration in `tauri.conf.json`
4. **Branding**: Update app name, description, and metadata

## IDE Setup

### Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

### Type Support For `.vue` Imports in TS

Since TypeScript cannot handle type information for `.vue` imports, they are shimmed to be a generic Vue component type by default. In most cases this is fine if you don't really care about component prop types outside of templates. However, if you wish to get actual prop types in `.vue` imports (for example to get props validation when using manual `h(...)` calls), you can enable Volar's Take Over mode by following these steps:

1. Run `Extensions: Show Built-in Extensions` from VS Code's command palette, look for `TypeScript and JavaScript Language Features`, then right click and select `Disable (Workspace)`. By default, Take Over mode will enable itself if the default TypeScript extension is disabled.
2. Reload the VS Code window by running `Developer: Reload Window` from the command palette.

You can learn more about Take Over mode [here](https://github.com/johnsoncodehk/volar/discussions/471).

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tauri](https://tauri.app/) - For the amazing cross-platform framework
- [Vue.js](https://vuejs.org/) - For the reactive frontend framework
- [Tailwind CSS](https://tailwindcss.com/) - For the utility-first CSS framework
- [daisyUI](https://daisyui.com/) - For the beautiful component library

## Support

If you find this template helpful, please consider:

- Starring the repository
- Reporting issues
- Contributing improvements
- Sharing feedback
