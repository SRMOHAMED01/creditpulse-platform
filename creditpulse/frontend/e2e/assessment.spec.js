import { randomUUID } from 'node:crypto';
import { test, expect } from '@playwright/test';

test('genuine assessment survives sign-out and a fresh browser session', async ({ page, request, browser, baseURL }) => {
  const api = process.env.E2E_API_URL || 'http://localhost:8000';
  const ready = await request.get(`${api}/ready`);
  expect(ready.status(), 'Migrated database and real model must be ready').toBe(200);
  const email = `browser-${randomUUID()}@example.com`;
  const password = 'BrowserFlow123!';
  await page.goto('/signup');
  await page.getByLabel('Email Address').fill(email);
  await page.getByLabel('Password (min 8 chars)').fill(password);
  await page.getByRole('button', { name: 'Create Account' }).click();
  await expect(page).toHaveURL(/\/profile$/);
  await page.getByLabel('Monthly income').fill('12000');
  await page.getByLabel('Current debt').fill('1800');
  await page.getByLabel('Age', { exact: true }).fill('35');
  await page.getByLabel('Years in current job').fill('7');
  await page.getByLabel('Open credit accounts').fill('2');
  await page.getByLabel('Payment history (0 to 1)').fill('0.95');
  await page.getByRole('button', { name: 'Save profile' }).click();
  await expect(page.getByText('Profile saved.')).toBeVisible();
  await page.getByRole('link', { name: 'Assessment', exact: true }).click();
  await expect(page.getByLabel('Monthly Income ($)')).toHaveValue('12000');
  await expect(page.getByLabel('Current Debt ($)')).toHaveValue('1800');
  await page.getByLabel('Requested Amount ($)').fill('10000');
  await page.getByLabel('Duration (Months)').fill('24');
  const responsePromise = page.waitForResponse((response) => response.url().endsWith('/credit/apply') && response.request().method() === 'POST');
  await page.getByRole('button', { name: 'Run Risk Evaluation' }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const saved = await response.json();
  expect(saved.explanation).toHaveLength(7);
  expect(saved.model_version).toMatch(/^[a-f0-9]{64}$/);
  expect(saved.input_snapshot.revenu_mensuel).toBe(12000);
  expect(saved.requested_amount).toBe(10000);
  expect(saved.duration_months).toBe(24);
  await expect(page).toHaveURL(new RegExp(`/result/${saved.id}$`));
  await expect(page.getByRole('heading', { name: 'Credit Risk & SHAP Analysis' })).toBeVisible();
  await page.reload();
  await expect(page.getByText(`Assessment #${saved.id} ·`)).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login$/);

  const fresh = await browser.newContext({ baseURL });
  try {
    const returning = await fresh.newPage();
    await returning.goto('/login');
    await returning.getByLabel('Email Address').fill(email);
    await returning.getByLabel('Password', { exact: true }).fill(password);
    await returning.getByRole('button', { name: 'Sign In' }).click();
    await expect(returning).toHaveURL(/\/dashboard$/);
    await returning.getByRole('link').filter({ hasText: `Assessment #${saved.id}` }).click();
    await expect(returning).toHaveURL(new RegExp(`/result/${saved.id}$`));
    await expect(returning.getByRole('heading', { name: 'Credit Risk & SHAP Analysis' })).toBeVisible();
  } finally {
    await fresh.close();
  }

  const other = await request.post(`${api}/auth/register`, { data: { email: `other-${randomUUID()}@example.com`, password } });
  expect(other.status()).toBe(201);
  const token = (await other.json()).access_token;
  const hidden = await request.get(`${api}/credit/applications/${saved.id}`, { headers: { Authorization: `Bearer ${token}` } });
  expect(hidden.status()).toBe(404);
});
