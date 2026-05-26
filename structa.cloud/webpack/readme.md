# Webpack Configuration Documentation

## Overview

This documentation covers the webpack configuration with additional guidance for extending functionality, adding features, and helpful resources.

## Table of Contents
1. [Core Configuration](#core-configuration)
2. [Adding New Features](#adding-new-features)
3. [Performance Optimization](#performance-optimization)
4. [Troubleshooting](#troubleshooting)
5. [Useful Resources](#useful-resources)

---

## Core Configuration

1. `common.config.js` - Contains shared configuration for all environments
2. `main.config.js` - Contains environment-specific configuration and extends the common config

## Common Configuration (`common.config.js`)

### Base Settings
- **Target**: Web browser (`'web'`)
- **Context**: Base directory of the project (one level up from the config file)
- **Entry Points**:
  - `top`: `assets/static/top-assets`
  - `bottom`: `assets/static/bottom-assets`

### Path Definitions
- **BASE_DIR**: Project root directory
- **paths**:
  - `assets`: `assets/` directory
  - `static`: `assets/static/` directory
  - `dist`: `assets/bundles/` output directory

### Plugins
1. **CopyWebpackPlugin**: Copies files from:
   - `static/js/` to `dist/js/`
   - `static/libs/` to `dist/libs/`
2. **BundleTracker**: Generates `bundles.json` in the assets directory
3. **MiniCssExtractPlugin**: Extracts CSS into separate files in `css/` directory
4. **VueLoaderPlugin**: Handles Vue single-file components

### Module Rules
- **JavaScript/JSX**: Uses `babel-loader` (excludes `node_modules`)
- **Vue**: Uses `vue-loader` with reactivity transform
- **HTML**: Uses `html-loader`
- **CSS/SCSS**: Processing pipeline:
  - `MiniCssExtractPlugin.loader`
  - `css-loader`
  - `postcss-loader` with plugins:
    - `postcss-import`
    - `postcss-nested`
    - `autoprefixer`
  - `sass-loader`
- **Images**: Handled as assets, output to `images/`
- **Fonts**: Handled as assets, output to `fonts/`

### Resolve Configuration
- **Extensions**: `.js`, `.jsx`, `.json`, `.vue`, `.scss`, `.css`
- **Aliases**:
  - `@*`: Points to dist directory
  - `static`: Points to static directory

## Main Configuration (`main.config.js`)

### Environment Setup
- Determines mode (defaults to production)
- Sets up development server when in development mode

### Key Features
1. **Library Copying**:
   - Reads `package-copy.json` for packages to copy
   - Copies specified packages from `node_modules` to `assets/bundles/libs/`
   - Handles cleanup in production mode

2. **RTL CSS Generation**:
   - Processes specified CSS files to create RTL versions
   - Supported pairs:
     - `css/app.min.css` → `css/app-rtl.min.css`
     - `css/bootstrap.min.css` → `css/bootstrap-rtl.min.css`

3. **Output Configuration**:
   - Output path: `assets/bundles/`
   - Public path: `/static/bundles/`
   - JavaScript files output to `js/` directory

### Development Server
- **Port**: 3000
- **Proxy**: Routes all requests to `http://localhost:8000`
- **Static Files**: Serves from output directory
- **Hot Reloading**: Disabled (uses live reload instead)

### Optimization
- **Production**:
  - Minimization enabled
  - Source maps generated
  - Chunk splitting enabled
- **Development**:
  - Inline source maps
  - Performance hints disabled

## Usage

### Production Build
```bash
webpack --mode=production
```

### Development Build
```bash
webpack --mode=development
```

### Development Server
```bash
webpack serve --mode=development
```

## Notes
- The configuration supports Vue.js components with reactivity transform
- RTL CSS generation is automatic for specified files
- Library copying is configurable via `package-copy.json`
- Cache is configured to use filesystem for faster rebuilds
---

## Adding New Features

### 1. Adding TailwindCSS Support

**Installation:**
```bash
npm install -D tailwindcss postcss-import autoprefixer
npx tailwindcss init
```

**Modify `common.config.js`:**
```javascript
// In postcss-loader plugins:
plugins: [
  require('postcss-import'),
  require('tailwindcss')({
    config: path.join(BASE_DIR, 'tailwind.config.js')
  }),
  require('postcss-nested'),
  require('autoprefixer'),
]
```

**Create `tailwind.config.js`:**
```javascript
module.exports = {
  content: [
    './assets/static/**/*.{html,js,vue}',
    './templates/**/*.html'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 2. Adding TypeScript Support

**Installation:**
```bash
npm install -D typescript ts-loader @types/webpack-env
```

**Modify Configuration:**
```javascript
// In common.config.js
module.exports = {
  // ...
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      }
    ]
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx', '.vue']
  }
}
```

### 3. Adding React Support

**Installation:**
```bash
npm install react react-dom @babel/preset-react
```

**Add to `.babelrc`:**
```json
{
  "presets": ["@babel/preset-react"]
}
```

### 4. Adding SVG Optimization

**Installation:**
```bash
npm install -D svgo svgo-loader
```

**Add Rule:**
```javascript
{
  test: /\.svg$/,
  use: [
    {
      loader: 'svgo-loader',
      options: {
        plugins: [
          { removeTitle: true },
          { convertColors: { shorthex: false } },
          { convertPathData: false }
        ]
      }
    }
  ]
}
```

---

## Performance Optimization

### 1. Cache Configuration

**Improve caching in `main.config.js`:**
```javascript
cache: {
  type: "filesystem",
  buildDependencies: {
    config: [__filename],
  },
  cacheDirectory: path.resolve(__dirname, '.webpack_cache'),
  name: `${mode}-cache`
},
```

### 2. DLL Plugin for Vendor Files

**Create `webpack.dll.config.js`:**
```javascript
const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: {
    vendor: ['react', 'react-dom', 'vue', 'lodash'] // Add your heavy libraries
  },
  output: {
    path: path.join(__dirname, 'assets/bundles'),
    filename: '[name].dll.js',
    library: '[name]_[hash]'
  },
  plugins: [
    new webpack.DllPlugin({
      path: path.join(__dirname, 'assets', '[name]-manifest.json'),
      name: '[name]_[hash]'
    })
  ]
};
```

**Reference in main config:**
```javascript
new webpack.DllReferencePlugin({
  manifest: require('./assets/vendor-manifest.json')
})
```

### 3. Bundle Analysis

**Installation:**
```bash
npm install -D webpack-bundle-analyzer
```

**Add to `main.config.js`:**
```javascript
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

// In plugins:
new BundleAnalyzerPlugin({
  analyzerMode: 'static',
  reportFilename: 'bundle-report.html',
  openAnalyzer: false
})
```

---

## Troubleshooting

### Common Issues

1. **RTL CSS not generating**:
   - Ensure `rtlcss` is installed (`npm install rtlcss`)
   - Verify CSS file paths in `cssPairs` array

2. **Vue components not loading**:
   - Check Vue loader is installed (`npm install -D vue-loader vue-template-compiler`)
   - Ensure `.vue` extension is in resolve.extensions

3. **Development server not proxying**:
   - Verify backend server is running on port 8000
   - Check proxy configuration in `devServer` settings

---

## Useful Resources

### Official Documentation
- [Webpack Documentation](https://webpack.js.org/concepts/)
- [Vue Loader](https://vue-loader.vuejs.org/)
- [Babel](https://babeljs.io/docs/en/)
- [PostCSS](https://postcss.org/)

### Community Plugins
- [Webpack Plugins Directory](https://webpack.js.org/plugins/)
- [Awesome Webpack](https://github.com/webpack-contrib/awesome-webpack)

### Performance Tools
- [Webpack Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)
- [Speed Measure Plugin](https://github.com/stephencookdev/speed-measure-webpack-plugin)

### Sample Configurations
- [Webpack Config Examples](https://github.com/webpack/webpack/tree/main/examples)
- [React + Webpack](https://github.com/facebook/create-react-app/tree/main/packages/react-scripts/config)

---

## Migration Guide

### Upgrading to Webpack 5

1. Update dependencies:
```bash
npm install webpack@latest webpack-cli@latest
```

2. Key changes to implement:
- Replace `file-loader`/`url-loader` with asset modules
- Update cache configuration (new filesystem cache)
- Verify plugin compatibility

### Migrating from CommonJS to ESM

**Convert config files to ESM:**
```javascript
// Change requires to imports
import { merge } from 'webpack-merge';
import commonConfig from './common.config.js';

// Update module.exports to export default
export default async (env, argv) => {
  // config
};
```

**Add to package.json:**
```json
{
  "type": "module"
}
```

