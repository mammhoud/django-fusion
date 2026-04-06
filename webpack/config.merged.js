/**
 * @file webpack.config.merged.js
 * Merged webpack configuration for multi-project builds
 * Combines configurations from ctc-research and structa projects
 */

const path = require('path');
const { merge } = require('webpack-merge');

// Import project-specific configs
const ctcResearchConfig = require('./ctc-research/webpack/main.config.js');

/**
 * Merged configuration for both projects
 * This allows building both projects with a single webpack command
 */
module.exports = async (env, argv) => {
    const mode = argv.mode || (process.env.NODE_ENV === 'production' ? 'production' : 'development');

    console.log(`🚀 Building merged webpack configuration in ${mode} mode`);

    // Get CTC Research config
    const ctcConfig = await ctcResearchConfig(env, argv);

    // Create merged configuration
    const mergedConfig = {
        mode,

        // Multiple entry points for different projects
        entry: {
            'ctc-research': ctcConfig.entry,
        },

        output: {
            path: path.resolve(__dirname, 'dist'),
            publicPath: '/static/',
            filename: '[name]/[name].[contenthash:8].js',
            chunkFilename: '[name]/chunk/[name].[contenthash:8].chunk.js',
            clean: true,
        },

        resolve: {
            extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
            alias: {
                '@ctc': path.resolve(__dirname, 'ctc-research/assets/static/js'),
                '@structa': path.resolve(__dirname, 'structa/core/assets/static/js'),
                '@shared': path.resolve(__dirname, 'shared/assets/static/js'),
            },
        },

        module: {
            rules: [
                {
                    test: /\.jsx?$/,
                    exclude: /node_modules/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: [
                                ['@babel/preset-env', { targets: { browsers: ['last 2 versions'] } }],
                                '@babel/preset-react',
                            ],
                            plugins: [
                                '@babel/plugin-proposal-class-properties',
                                '@babel/plugin-proposal-optional-chaining',
                            ],
                        },
                    },
                },
                {
                    test: /\.css$/,
                    use: ['style-loader', 'css-loader', 'postcss-loader'],
                },
                {
                    test: /\.scss$/,
                    use: ['style-loader', 'css-loader', 'postcss-loader', 'sass-loader'],
                },
                {
                    test: /\.(png|jpg|jpeg|gif|svg)$/,
                    type: 'asset',
                    parser: {
                        dataUrlCondition: {
                            maxSize: 8 * 1024, // 8kb
                        },
                    },
                },
                {
                    test: /\.(woff|woff2|eot|ttf|otf)$/,
                    type: 'asset/resource',
                },
            ],
        },

        optimization: {
            minimize: mode === 'production',
            minimizer: ['...'],
            splitChunks: {
                chunks: 'all',
                minSize: 10000,
                maxSize: 50000,
                cacheGroups: {
                    vendors: {
                        test: /[\\/]node_modules[\\/]/,
                        name: 'vendors',
                        priority: 10,
                    },
                    common: {
                        minChunks: 2,
                        priority: 5,
                        reuseExistingChunk: true,
                    },
                },
            },
            runtimeChunk: 'single',
        },

        devtool: mode === 'production' ? 'source-map' : 'cheap-module-source-map',

        devServer: {
            port: 3000,
            host: 'localhost',
            hot: true,
            open: false,
            compress: true,
            historyApiFallback: true,
            client: {
                overlay: {
                    errors: true,
                    warnings: false,
                },
                progress: true,
            },
        },

        performance: {
            hints: mode === 'production' ? 'warning' : false,
            maxAssetSize: 512000,
            maxEntrypointSize: 512000,
        },

        stats: {
            colors: true,
            modules: false,
            chunks: false,
            assets: true,
            performance: mode === 'production',
            timings: true,
        },
    };

    // Merge with CTC Research config
    return merge(ctcConfig, mergedConfig);
};
