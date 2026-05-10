import pluginVue from 'eslint-plugin-vue'

export default [
  {
    ignores: ['dist/', 'node_modules/', 'coverage/'],
  },
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue', '**/*.ts', '**/*.js'],
    languageOptions: {
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    rules: {
      'vue/multi-word-component-names': 'off',
    },
  },
]
