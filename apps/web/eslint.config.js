import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
export default [eslint.configs.recommended,...tseslint.configs.recommended,...svelte.configs['flat/recommended'],{rules:{'@typescript-eslint/no-explicit-any':'error'}}];
