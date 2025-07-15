import { test, expect } from '@playwright/test';

test.describe('Academy AI Assistant E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page before each test
    await page.goto('http://localhost:3002');
  });

  test('should display dashboard page', async ({ page }) => {
    // Check if the page loads correctly
    await expect(page).toHaveTitle(/Academy AI Assistant/);
    
    // Check for main navigation elements
    await expect(page.locator('nav')).toBeVisible();
    
    // Check for dashboard content
    await expect(page.locator('h1')).toContainText(/Dashboard/);
  });

  test('should navigate to students page', async ({ page }) => {
    // Click on students navigation link
    await page.click('text=Students');
    
    // Verify we're on the students page
    await expect(page).toHaveURL(/.*students/);
    await expect(page.locator('h1')).toContainText(/Students/);
  });

  test('should navigate to teachers page', async ({ page }) => {
    // Click on teachers navigation link
    await page.click('text=Teachers');
    
    // Verify we're on the teachers page
    await expect(page).toHaveURL(/.*teachers/);
    await expect(page.locator('h1')).toContainText(/Teachers/);
  });

  test('should navigate to materials page', async ({ page }) => {
    // Click on materials navigation link
    await page.click('text=Materials');
    
    // Verify we're on the materials page
    await expect(page).toHaveURL(/.*materials/);
    await expect(page.locator('h1')).toContainText(/Materials/);
  });

  test('should navigate to AI chat page', async ({ page }) => {
    // Click on AI chat navigation link
    await page.click('text=AI Chat');
    
    // Verify we're on the AI chat page
    await expect(page).toHaveURL(/.*ai-chat/);
    await expect(page.locator('h1')).toContainText(/AI Chat/);
  });

  test('should have responsive design', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('nav')).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('nav')).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should handle theme toggle', async ({ page }) => {
    // Find and click theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    if (await themeToggle.isVisible()) {
      await themeToggle.click();
      
      // Verify theme change (this might need adjustment based on your theme implementation)
      await expect(page.locator('html')).toHaveAttribute('class', /dark/);
    }
  });
}); 