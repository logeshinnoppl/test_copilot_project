import { test, expect } from '@playwright/test';

test('visitor submits the contact form and the submission appears for the admin', async ({ page, context }) => {
  const name = `Playwright User ${Date.now()}`;
  const email = 'playwright@example.com';
  const subject = 'E2E test subject';
  const message = 'This message was submitted by the Playwright e2e test.';

  await page.goto('/contact');
  await expect(page.locator('h1')).toHaveText('Contact Us');

  await page.fill('#name', name);
  await page.fill('#email', email);
  await page.fill('#subject', subject);
  await page.fill('#message', message);
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/\/thank-you$/);
  await expect(page.locator('h1')).toHaveText('Thank you!');

  await context.setHTTPCredentials({ username: 'admin', password: 'secret' });
  await page.goto('/admin/submissions');

  const firstRow = page.locator('tbody tr').first();
  await expect(firstRow).toContainText(name);
  await expect(firstRow).toContainText(email);
  await expect(firstRow).toContainText(subject);
});

test('contact form shows inline validation errors and does not submit', async ({ page }) => {
  await page.goto('/contact');

  await page.fill('#name', '');
  await page.fill('#email', 'not-an-email');
  await page.fill('#subject', 'Subject');
  await page.fill('#message', 'Message body');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/\/contact$|\/submit$/);
  await expect(page.locator('.error')).toContainText(['This field is required.', 'Enter a valid email address.']);
});

test('admin submissions page requires authentication', async ({ page }) => {
  const response = await page.goto('/admin/submissions');
  expect(response?.status()).toBe(401);
});
