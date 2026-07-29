// ============================================================================
// django-fusion — Webpack 5 Config with Workspace Support
// ============================================================================
// Builds component SCSS/JS assets into versioned bundles consumed by
// django-webpack-loader via {% render_bundle 'fusion' %} tag.
//
// Workspaces:
//   Set FUSION_WEBPACK_WORKSPACE env var to switch workspace configs.
//   Default workspace: webpack/workspaces/default.js
//
// Output:
//   static/bundles/fusion.<contenthash>.js
//   static/bundles/fusion.<contenthash>.css
//   webpack-stats.json        ← Read by django-webpack-loader
// ============================================================================

const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");
const { workspace } = require("./webpack/workspace.config");

const SRC_DIR = path.resolve(__dirname, "src");
const STATIC_DIR = path.resolve(__dirname, "static");

module.exports = (env, argv) => {
  const isDev = argv.mode === "development";

  // Merge base entries with workspace entries
  const baseEntries = {
    fusion: [
      path.resolve(SRC_DIR, "django_fusion/assets/entry.js"),
    ],
  };
  const mergedEntries = {
    ...baseEntries,
    ...(workspace.entries || {}),
  };

  // Merge base output with workspace output overrides
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

      // Generate webpack-stats.json consumed by django-webpack-loader
      new BundleTracker({
        path: __dirname,
        filename: "webpack-stats.json",
      }),

      // Workspace-specific plugins
      ...(workspace.plugins || []),
    ],

    resolve: {
      extensions: [".js", ".jsx", ".scss", ".css"],
      // Alias so component SCSS can import shared vars easily
      alias: {
        "@fusion": path.resolve(SRC_DIR, "django_fusion/assets"),
        "@fusion-components": path.resolve(SRC_DIR, "django_fusion/comp"),
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
