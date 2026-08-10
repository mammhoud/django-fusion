// ============================================================================
// django-fusion — Webpack 5 Config with Workspace + Project Support
// ============================================================================
// Builds component SCSS/JS assets into versioned bundles consumed by
// django-webpack-loader via {% render_bundle 'fusion' %} tag.
//
// Workspaces:
//   Set FUSION_WEBPACK_WORKSPACE env var to switch workspace configs.
//   Default workspace: webpack/workspaces/default.js
//
// Project-level customization (env vars, set by manage.py webpack_build or Makefile):
//   FUSION_WEBPACK_WORKSPACE_PATH  — Absolute path to custom workspace .js file
//   FUSION_WEBPACK_ENTRIES         — JSON: { "entry_name": ["path/to/file.scss", ...] }
//   FUSION_WEBPACK_OUTPUT_PATH     — Override output directory
//   FUSION_WEBPACK_OUTPUT_PUBLIC   — Override publicPath (default: /static/bundles/)
//   FUSION_WEBPACK_STATS_FILE      — Override webpack-stats.json location
//   FUSION_WEBPACK_SCSS_INCLUDES   — JSON: ["path/to/scss/dir", ...]
//   FUSION_WEBPACK_ALIASES         — JSON: { "@alias": "path/to/dir" }
//
// Output:
//   static/bundles/fusion.<contenthash>.js
//   static/bundles/fusion.<contenthash>.css
//   webpack-stats.json        ← Read by django-webpack-loader
// ============================================================================

const path = require("path");
const fs = require("fs");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");
const { workspace } = require("./webpack/workspace.config");

const SRC_DIR = path.resolve(__dirname, "src");
const STATIC_DIR = path.resolve(__dirname, "static");
const PROJECT_ROOT = process.env.FUSION_PROJECT_ROOT
  ? path.resolve(process.env.FUSION_PROJECT_ROOT)
  : path.resolve(__dirname, "..", ".."); // fallback: monorepo root

// ── Project-level overrides (from env vars) ─────────────────────
const projectEntries = (() => {
  try { return JSON.parse(process.env.FUSION_WEBPACK_ENTRIES || "{}"); }
  catch { console.warn("[fusion-webpack] Invalid FUSION_WEBPACK_ENTRIES JSON — ignoring"); return {}; }
})();
const projectOutputPath = process.env.FUSION_WEBPACK_OUTPUT_PATH || null;
const projectOutputPublic = process.env.FUSION_WEBPACK_OUTPUT_PUBLIC || "/static/bundles/";
const projectStatsFile = process.env.FUSION_WEBPACK_STATS_FILE || null;
const projectScssIncludes = (() => {
  try { return JSON.parse(process.env.FUSION_WEBPACK_SCSS_INCLUDES || "[]"); }
  catch { console.warn("[fusion-webpack] Invalid FUSION_WEBPACK_SCSS_INCLUDES JSON"); return []; }
})();
const projectAliases = (() => {
  try { return JSON.parse(process.env.FUSION_WEBPACK_ALIASES || "{}"); }
  catch { console.warn("[fusion-webpack] Invalid FUSION_WEBPACK_ALIASES JSON"); return {}; }
})();

console.log(`[fusion-webpack] Project root: ${PROJECT_ROOT}`);
if (Object.keys(projectEntries).length) console.log(`[fusion-webpack] Project entries: ${Object.keys(projectEntries).join(", ")}`);
if (projectOutputPath) console.log(`[fusion-webpack] Output path: ${projectOutputPath}`);

module.exports = (env, argv) => {
  const isDev = argv.mode === "development";

  // Merge base entries → workspace entries → project entries
  const baseEntries = {
    fusion: [
      path.resolve(SRC_DIR, "django_fusion/assets/entry.js"),
    ],
  };
  const projectResolvedEntries = {};
  for (const [name, files] of Object.entries(projectEntries)) {
    projectResolvedEntries[name] = files.map(f => {
      const abs = path.isAbsolute(f) ? f : path.resolve(PROJECT_ROOT, f);
      if (!fs.existsSync(abs)) console.warn(`[fusion-webpack] Entry file not found: ${abs}`);
      return abs;
    });
  }
  const mergedEntries = {
    ...baseEntries,
    ...(workspace.entries || {}),
    ...projectResolvedEntries,
  };

  // Merge base output → workspace overrides → project overrides
  const baseOutput = {
    path: path.resolve(STATIC_DIR, "bundles"),
    filename: isDev ? "[name].js" : "[name].[contenthash:8].js",
    chunkFilename: isDev ? "[id].js" : "[id].[contenthash:8].js",
    publicPath: "/static/bundles/",
    clean: true,
  };
  const mergedOutput = {
    ...baseOutput,
    ...(workspace.output || {}),
    ...(projectOutputPath ? { path: path.resolve(projectOutputPath) } : {}),
    publicPath: projectOutputPublic,
  };

  return {
    entry: mergedEntries,
    output: mergedOutput,

    // Dev source-maps
    devtool: isDev ? "eval-source-map" : "source-map",

    module: {
      rules: [
        // JavaScript / JSX — webpack 5 handles modern ES modules natively.
        // No babel needed for ES2020+ syntax used in entry.js.
        // Add @babel/core + babel-loader if IE11 / older browser support is needed.

        // SCSS — compile to separate CSS file per entry
        {
          test: /\.s?css$/,
          use: [
            isDev ? "style-loader" : MiniCssExtractPlugin.loader,
            "css-loader",
            {
              loader: "sass-loader",
              options: {
                sassOptions: {
                  // Modern Dart Sass API
                  silenceDeprecations: ["import"],
                  // Base include paths + project SCSS directories
                  includePaths: [
                    path.resolve(SRC_DIR, "django_fusion/assets"),
                    ...projectScssIncludes.map(p =>
                      path.isAbsolute(p) ? p : path.resolve(PROJECT_ROOT, p)
                    ),
                  ],
                },
              },
            },
          ],
        },

        // CSS in node_modules (e.g. normalize.css)
        {
          test: /\.css$/,
          use: [
            isDev ? "style-loader" : MiniCssExtractPlugin.loader,
            "css-loader",
          ],
        },

        // Fonts — woff2/ttf/eot/svg as static assets
        {
          test: /\.(woff2?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
          type: "asset/resource",
          generator: {
            filename: "fonts/[name][ext]",
          },
        },

        // Images
        {
          test: /\.(png|jpe?g|gif|webp)$/,
          type: "asset/resource",
          generator: {
            filename: "images/[name][ext]",
          },
        },
      ],
    },

    plugins: [
      // Extract CSS to separate file instead of inline <style> tags
      ...(isDev
        ? []
        : [
            new MiniCssExtractPlugin({
              filename: "[name].[contenthash:8].css",
              chunkFilename: "[id].[contenthash:8].css",
            }),
          ]),

      // Generate webpack-stats.json consumed by django-webpack-loader.
      // Uses project override path when FUSION_WEBPACK_STATS_FILE is set.
      new BundleTracker({
        path: projectStatsFile
          ? path.dirname(path.resolve(projectStatsFile))
          : __dirname,
        filename: projectStatsFile
          ? path.basename(projectStatsFile)
          : "webpack-stats.json",
      }),

      // Workspace-specific plugins
      ...(workspace.plugins || []),
    ],

    resolve: {
      extensions: [".js", ".jsx", ".scss", ".css"],
      // Base aliases + workspace aliases + project aliases
      alias: {
        "@fusion": path.resolve(SRC_DIR, "django_fusion/assets"),
        "@fusion-components": path.resolve(SRC_DIR, "django_fusion/comp"),
        ...(workspace.aliases || {}),
        ...Object.fromEntries(
          Object.entries(projectAliases).map(([k, v]) => [k, path.resolve(PROJECT_ROOT, v)])
        ),
      },
    },

    // Optimisation for production
    optimization: {
      minimize: !isDev,
      splitChunks: {
        cacheGroups: {
          // Vendor chunk for node_modules dependencies
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendor",
            chunks: "all",
          },
        },
      },
    },
  };
};
