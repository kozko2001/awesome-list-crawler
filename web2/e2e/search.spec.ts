import { test, expect } from '@playwright/test';

test.describe('Search Page', () => {
  test('loads search page with search input', async ({ page }) => {
    await page.goto('/search');
    
    await expect(page.getByText('Search')).toBeVisible();
    await expect(page.getByPlaceholder(/Search repositories/)).toBeVisible();
    await expect(page.getByText('Start your search')).toBeVisible();
  });

  test('shows search suggestions', async ({ page }) => {
    await page.goto('/search');
    
    // Check if suggestion buttons are present
    await expect(page.getByRole('button', { name: 'javascript' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'python' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'react' })).toBeVisible();
  });

  test('performs search when typing', async ({ page }) => {
    // Mock search API
    await page.route('**/api/v1/search**', async route => {
      const url = new URL(route.request().url());
      const query = url.searchParams.get('q');
      
      const json = {
        items: [{
          name: `result-for-${query}`,
          description: `Search result for ${query}`,
          source: 'https://github.com/test/result',
          list_name: 'awesome-search',
          list_source: 'https://github.com/test/awesome-search',
          time: '2024-01-15T10:00:00Z'
        }],
        page: 1,
        size: 20,
        total: 1,
        total_pages: 1
      };
      await route.fulfill({ json });
    });

    await page.goto('/search');
    
    const searchInput = page.getByPlaceholder(/Search repositories/);
    
    // Type in search input
    await searchInput.fill('javascript');
    
    // Should show search results
    await expect(page.getByText('result-for-javascript')).toBeVisible();
    await expect(page.getByText('Search result for javascript')).toBeVisible();
  });

  test('clicking suggestion buttons fills search input', async ({ page }) => {
    await page.goto('/search');
    
    // Click on a suggestion button
    await page.getByRole('button', { name: 'react' }).click();
    
    // Should fill the search input
    const searchInput = page.getByPlaceholder(/Search repositories/);
    await expect(searchInput).toHaveValue('react');
  });

  test('clear button works', async ({ page }) => {
    await page.goto('/search');
    
    const searchInput = page.getByPlaceholder(/Search repositories/);
    
    // Fill search input
    await searchInput.fill('test query');
    await expect(searchInput).toHaveValue('test query');
    
    // Click clear button
    await page.getByRole('button', { name: '', exact: false }).last().click(); // X button
    await expect(searchInput).toHaveValue('');
  });

  test('shows no results message when search returns empty', async ({ page }) => {
    // Mock empty search results
    await page.route('**/api/v1/search**', async route => {
      const json = {
        items: [],
        page: 1,
        size: 20,
        total: 0,
        total_pages: 0
      };
      await route.fulfill({ json });
    });

    await page.goto('/search');
    
    const searchInput = page.getByPlaceholder(/Search repositories/);
    await searchInput.fill('nonexistent');
    
    // Should show no results message
    await expect(page.getByText('No results found')).toBeVisible();
    await expect(page.getByText('Try different keywords')).toBeVisible();
  });

  test('handles search API errors', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/search**', route => {
      route.fulfill({ status: 500, body: 'Server Error' });
    });

    await page.goto('/search');
    
    const searchInput = page.getByPlaceholder(/Search repositories/);
    await searchInput.fill('test');
    
    // Should show error message
    await expect(page.getByText('Search Failed')).toBeVisible();
  });
});