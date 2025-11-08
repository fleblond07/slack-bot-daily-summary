import js from '@eslint/js'
import svelte from 'eslint-plugin-svelte'
import globals from 'globals'

export default [
  js.configs.recommended,
  ...svelte.configs['flat/recommended'],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node
      }
    }
  },
  {
    rules: {
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'svelte/no-at-html-tags': 'off'
    }
  },
  {
    ignores: [
      'dist/',
      'node_modules/',
      'build/',
      '.svelte-kit/',
      'coverage/'
    ]
  }
]
