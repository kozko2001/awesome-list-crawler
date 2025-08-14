import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('all navigation links are functional', async ({ page }) => {
    await page.goto('/');
    
    // Test Timeline link (should be active on home page)
    const timelineLink = page.getByRole('link', { name: 'Timeline' });
    await expect(timelineLink).toHaveClass(/text-terminal-green/);
    
    // Test Search link
    const searchLink = page.getByRole('link', { name: 'Search' });
    await searchLink.click();
    await expect(page).toHaveURL('/search');
    await expect(searchLink).toHaveClass(/text-terminal-green/);
    
    // Test Lucky link
    const luckyLink = page.getByRole('link', { name: 'Lucky' });
    await luckyLink.click();
    await expect(page).toHaveURL('/lucky');
    await expect(luckyLink).toHaveClass(/text-terminal-green/);
    
    // Go back to Timeline
    await timelineLink.click();
    await expect(page).toHaveURL('/');
    await expect(timelineLink).toHaveClass(/text-terminal-green/);
  });

  test('logo is visible and styled correctly', async ({ page }) => {
    await page.goto('/');
    
    const logo = page.getByText('$ awesome-crawler');
    await expect(logo).toBeVisible();
    await expect(logo).toHaveClass(/glow-text/);
  });

  test('navigation is consistent across all pages', async ({ page }) => {
    const pages = ['/', '/search', '/lucky'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      
      // Check that navigation bar is present
      await expect(page.getByText('$ awesome-crawler')).toBeVisible();
      await expect(page.getByRole('link', { name: 'Timeline' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Search' })).toBeVisible();
      await expect(page.getByRole('link', { name: 'Lucky' })).toBeVisible();
    }
  });

  test('navigation has proper terminal styling', async ({ page }) => {
    await page.goto('/');
    
    const nav = page.locator('nav');
    await expect(nav).toHaveClass(/border-b/);
    await expect(nav).toHaveClass(/border-terminal-border/);
    await expect(nav).toHaveClass(/bg-terminal-bg/);
  });

  test('responsive navigation works on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Navigation should still be visible
    await expect(page.getByText('$ awesome-crawler')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Timeline' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Search' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Lucky' })).toBeVisible();
  });
});