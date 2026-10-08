import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('creditpulse_token', 'browser-ui-test-token'));
});

test('saved financial values prefill without slider rounding or clipping', async ({ page }) => {
  await page.route('**/users/profile', (route) => route.fulfill({ json: {
    revenu_mensuel: 30000.25, dettes_actuelles: 18000.5, age: 40,
    anciennete_emploi: 7.5, nombre_credits_en_cours: 3, historique_paiement: 0.92,
  } }));
  await page.goto('/apply');
  await expect(page.getByLabel('Monthly Income ($)')).toHaveValue('30000.25');
  await expect(page.getByLabel('Current Debt ($)')).toHaveValue('18000.5');
  await expect(page.getByLabel('Employment Seniority (Years)')).toHaveValue('7.5');
  await expect(page.getByRole('button', { name: 'Run Risk Evaluation' })).toBeEnabled();
});

test('profile load failure blocks scoring and can be retried', async ({ page }) => {
  let recovered = false;
  await page.route('**/users/profile', (route) => {
    return route.fulfill(!recovered ? { status: 503, json: { detail: 'Unavailable' } } : { json: {
      revenu_mensuel: 12000, dettes_actuelles: 1800, age: 35,
      anciennete_emploi: 7, nombre_credits_en_cours: 2, historique_paiement: 0.95,
    } });
  });
  await page.goto('/apply');
  await expect(page.getByText('Could not load your saved profile.')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Run Risk Evaluation' })).toBeDisabled();
  recovered = true;
  await page.getByRole('button', { name: 'Retry', exact: true }).click();
  await expect(page.getByLabel('Monthly Income ($)')).toHaveValue('12000');
  await expect(page.getByRole('button', { name: 'Run Risk Evaluation' })).toBeEnabled();
});
