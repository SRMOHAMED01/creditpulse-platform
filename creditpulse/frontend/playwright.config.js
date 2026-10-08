import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.E2E_BASE_URL || 'http://localhost:5173';

export default defineConfig({
  testDir: './e2e',
  timeout: 60000,
  expect: { timeout: 15000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: { baseURL, channel: process.env.E2E_BROWSER_CHANNEL, trace: 'retain-on-failure', screenshot: 'only-on-failure' },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
  webServer: process.env.E2E_EXTERNAL_SERVER ? undefined : {
    command: `npm run dev -- --host 127.0.0.1 --port ${new URL(baseURL).port || '5173'} --strictPort`,
    url: baseURL,
    // Fail on occupied ports rather than accidentally testing another project.
    reuseExistingServer: false,
  },
});
