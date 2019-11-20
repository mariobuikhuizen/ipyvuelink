var path = require('path');
var version = require('./package.json').version;

// Custom webpack rules are generally the same for all webpack bundles, hence
// stored in a separate local variable.
var rules = [
    { test: /\.css$/, use: ['style-loader', 'css-loader']},
    {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        loader: 'file-loader',
    },
];

module.exports = [
    {
        entry: './lib/entryPoints/extension.js',
        output: {
            filename: 'extension.js',
            path: path.resolve(__dirname, '..', 'ipypL4C3h0ld3r', 'static'),
            libraryTarget: 'amd'
        },
        mode: 'production',
    },
    {
        entry: './lib/entryPoints/notebook.js',
        output: {
            filename: 'index.js',
            path: path.resolve(__dirname, '..', 'ipypL4C3h0ld3r', 'static'),
            libraryTarget: 'amd'
        },
        devtool: 'source-map',
        module: {
            rules: rules
        },
        externals: ['@jupyter-widgets/base', 'jupyter-vue'],
        mode: 'production',
        resolve: {
            alias: {
                vue$: path.resolve(__dirname, 'lib', 'vue_alias'),
            }
        },
        performance: {
            maxEntrypointSize: 1400000,
            maxAssetSize: 1400000
        },
    },
    {
        entry: './lib/entryPoints/embed.js',
        output: {
            filename: 'index.js',
            path: path.resolve(__dirname, 'dist'),
            libraryTarget: 'amd',
            publicPath: 'https://unpkg.com/jupyter-pL4C3h0ld3r@' + version + '/dist/'
        },
        devtool: 'source-map',
        module: {
            rules: rules
        },
        externals: ['@jupyter-widgets/base', 'jupyter-vue'],
        mode: 'production',
        resolve: {
            alias: {
                vue$: path.resolve(__dirname, 'lib', 'vue_alias'),
            }
        },
        performance: {
            maxEntrypointSize: 1400000,
            maxAssetSize: 1400000
        },
    },
];
