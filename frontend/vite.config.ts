import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Configuração do Vite.
 *
 * O proxy de `/api` evita CORS em desenvolvimento e, mais importante, mantém o
 * cliente sem nenhuma URL absoluta embutida: o mesmo build serve tanto o
 * desenvolvimento local quanto uma implantação atrás de proxy reverso.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    // Endereço explícito: a suíte de acessibilidade aguarda exatamente esta
    // origem, e o padrão do Vite varia entre versões e sistemas.
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Alvos modernos, mas não os mais recentes: parte do público institucional
    // acessa de estações com navegadores desatualizados, e um painel sobre
    // acessibilidade que não abre no computador do gestor é inútil.
    target: ['es2020', 'chrome90', 'firefox90', 'safari15'],
  },
});
