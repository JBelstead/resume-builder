import pluginVue from 'eslint-plugin-vue'
import tsParser from '@typescript-eslint/parser'

export default [
  {
    ignores: ['dist/', 'node_modules/', 'coverage/'],
  },
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.ts'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tsParser,
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    rules: {
      'vue/multi-word-component-names': 'off',
    },
  },
]
