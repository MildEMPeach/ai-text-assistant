module.exports = {
  root: true,
  env: {
    es2022: true,
    node: true,
    browser: true
  },
  parser: '@typescript-eslint/parser',
  parserOptions: {
    sourceType: 'module'
  },
  plugins: ['@typescript-eslint'],
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended', 'prettier'],
  ignorePatterns: ['dist', 'node_modules'],
  overrides: [
    {
      files: ['src/main/**/*.ts', 'src/preload/**/*.ts'],
      parserOptions: {
        project: ['./tsconfig.main.json']
      }
    },
    {
      files: ['src/renderer/**/*.ts'],
      parserOptions: {
        project: ['./tsconfig.renderer.json']
      }
    }
  ]
};
