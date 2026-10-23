import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5055',
  },
  webServer: {
    command: 'rm -f instance/e2e.db && .venv/bin/python app.py',
    url: 'http://127.0.0.1:5055/contact',
    reuseExistingServer: false,
    env: {
      ADMIN_USERNAME: 'admin',
      ADMIN_PASSWORD: 'secret',
      PORT: '5055',
      CONTACT_DB_PATH: 'instance/e2e.db',
    },
    timeout: 20000,
  },
});
