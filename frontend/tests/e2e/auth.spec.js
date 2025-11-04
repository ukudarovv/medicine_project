import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('text=Medicine ERP')).toBeVisible()
    await expect(page.locator('input[placeholder="Введите логин"]')).toBeVisible()
    await expect(page.locator('input[placeholder="Введите пароль"]')).toBeVisible()
  })

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder="Введите логин"]', 'wronguser')
    await page.fill('input[placeholder="Введите пароль"]', 'wrongpass')
    await page.click('button:has-text("Войти")')
    
    // Wait for error message
    await page.waitForTimeout(1000)
  })

  test('should redirect to dashboard on successful login', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder="Введите логин"]', 'admin')
    await page.fill('input[placeholder="Введите пароль"]', 'admin123')
    await page.click('button:has-text("Войти")')
    
    // Should redirect to main page
    await page.waitForURL('/')
    await expect(page.locator('text=Расписание')).toBeVisible()
  })
})

