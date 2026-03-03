module.exports = {
    parser: '@typescript-eslint/parser',
    extends: [
        'plugin:@typescript-eslint/recommended',
    ],
    parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module',
    },
    rules: {
        // Turn off some rules that may cause bulk modifications
        '@typescript-eslint/explicit-function-return-type': 'off',
        '@typescript-eslint/explicit-module-boundary-types': 'off',
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/no-unused-vars': ['warn', { 'argsIgnorePattern': '^_' }],
        // Disable no-empty-function to prevent getTokens crash when ESLint
        // and @typescript-eslint versions are mismatched (e.g. npx fallback)
        '@typescript-eslint/no-empty-function': 'off',
        'no-empty-function': 'off',
    },
};