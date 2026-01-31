import { test, expect } from '@playwright/test';

function uniqueEmail(): string {
  const ts = Date.now();
  return `e2e_${ts}@example.com`;
}

test('register -> redirect to /books -> create book -> add & edit note -> logout', async ({ page }) => {
  const email = uniqueEmail();
  const password = 'Password1!';

  await page.goto('/');
  await page.getByRole('link', { name: 'Załóż konto' }).click();

  await expect(page.getByRole('heading', { name: 'Rejestracja' })).toBeVisible();

  await page.locator('input[name="email"]').fill(email);
  await page.locator('input[name="password"]').fill(password);
  await page.locator('input[name="password_confirm"]').fill(password);
  await page.getByRole('button', { name: 'Załóż konto' }).click();

  await expect(page).toHaveURL(/\/books/);

  await page.locator('textarea[name="title"]').fill('E2E Book');
  await page.locator('textarea[name="author"]').fill('E2E Author');
  await page.getByRole('button', { name: 'Dodaj książkę' }).click();

  await page.getByRole('link', { name: 'E2E Book' }).click();
  await expect(page.getByRole('heading', { name: 'E2E Book' })).toBeVisible();

  await page.locator('textarea[name="content"]').fill('first note');
  await page.getByRole('button', { name: 'Dodaj notatkę' }).click();
  await expect(page.getByText('first note')).toBeVisible();

  await page.getByRole('link', { name: 'Edytuj' }).first().click();
  await page.locator('textarea[name="content"]').fill('edited note');
  await page.getByRole('button', { name: 'Zapisz' }).click();

  await expect(page.getByText('edited note')).toBeVisible();

  await page.getByRole('button', { name: 'Wyloguj' }).click();
  await expect(page).toHaveURL(/(\/|\/login)/);
});
