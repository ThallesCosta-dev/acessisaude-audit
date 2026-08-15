import { defineConfig, devices } from '@playwright/test';

/**
 * Configuração da suíte de acessibilidade do painel.
 *
 * Dois perfis de dispositivo, pelos mesmos motivos metodológicos do backend
 * (ver `config.py`, `DEFAULT_VIEWPORTS`): o celular estreito é onde o critério
 * 1.4.10 se define e onde está a maior parte dos usuários de serviço público
 * de saúde; o desktop é onde as interfaces costumam ser homologadas.
 *
 * O servidor de desenvolvimento é iniciado automaticamente. A API pode estar
 * fora do ar: as telas tratam erro de rede como estado de primeira classe, e o
 * axe-core precisa encontrar essa mensagem de erro acessível tanto quanto
 * encontraria os dados.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',

  use: {
    baseURL: 'http://127.0.0.1:5173',
    trace: 'on-first-retry',
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
  },

  projects: [
    {
      name: 'desktop-1366',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1366, height: 768 } },
    },
    {
      name: 'mobile-320',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 320, height: 640 },
        isMobile: false,
      },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://127.0.0.1:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
