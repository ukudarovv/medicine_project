import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login')
    await page.fill('input[placeholder="Введите логин"]', 'admin')
    await page.fill('input[placeholder="Введите пароль"]', 'admin123')
    await page.click('button:has-text("Войти")')
    await page.waitForURL('/')
  })

  test('should navigate to patients page', async ({ page }) => {
    await page.click('a:has-text("Пациенты")')
    await expect(page).toHaveURL('/patients')
    await expect(page.locator('h1:has-text("Пациенты")')).toBeVisible()
  })

  test('should navigate to services page', async ({ page }) => {
    await page.click('a:has-text("Услуги")')
    await expect(page).toHaveURL('/services')
    await expect(page.locator('h1:has-text("Услуги")')).toBeVisible()
  })

  test('should navigate to staff page', async ({ page }) => {
    await page.click('a:has-text("Сотрудники")')
    await expect(page).toHaveURL('/staff')
    await expect(page.locator('h1:has-text("Сотрудники")')).toBeVisible()
  })

  test('should navigate to settings page', async ({ page }) => {
    await page.click('a:has-text("Настройки")')
    await expect(page).toHaveURL('/settings/clinic')
    await expect(page.locator('text=Информация о клинике')).toBeVisible()
  })
})

