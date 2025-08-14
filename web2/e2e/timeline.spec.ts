import { test, expect } from '@playwright/test';

test.describe('Timeline Page', () => {
  test('loads timeline page successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check if navigation is present
    await expect(page.getByText('$ awesome-crawler')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Timeline' })).toBeVisible();
    
    // Check page title
    await expect(page.getByText('Timeline')).toBeVisible();
    await expect(page.getByText('Chronological feed of awesome repositories')).toBeVisible();
  });

  test('shows loading state initially', async ({ page }) => {
    // Slow down the network to see loading state
    await page.route('**/api/v1/**', route => {
      setTimeout(() => route.continue(), 1000);
    });

    await page.goto('/');
    
    // Should show loading indicator
    await expect(page.getByText('Initializing timeline')).toBeVisible();
  });

  test('navigation works correctly', async ({ page }) => {
    await page.goto('/');
    
    // Click on Search navigation
    await page.getByRole('link', { name: 'Search' }).click();
    await expect(page).toHaveURL('/search');
    
    // Click on Lucky navigation
    await page.getByRole('link', { name: 'Lucky' }).click();
    await expect(page).toHaveURL('/lucky');
    
    // Go back to Timeline
    await page.getByRole('link', { name: 'Timeline' }).click();
    await expect(page).toHaveURL('/');
  });

  test('displays repository items when data is available', async ({ page }) => {
    // Mock API response with test data
    await page.route('**/api/v1/timeline**', async route => {
      const json = {
        timeline: [{
          date: '2024-01-15T00:00:00Z',
          items: [{
            name: 'test-repo',
            description: 'A test repository',
            source: 'https://github.com/test/test-repo',
            list_name: 'awesome-test',
            list_source: 'https://github.com/test/awesome-test',
            time: '2024-01-15T10:00:00Z'
          }]
        }],
        page: 1,
        size: 10,
        total: 1,
        total_pages: 1
      };
      await route.fulfill({ json });
    });

    await page.goto('/');
    
    // Should display the repository item
    await expect(page.getByText('test-repo')).toBeVisible();
    await expect(page.getByText('A test repository')).toBeVisible();
    await expect(page.getByText('from awesome-test')).toBeVisible();
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API to return error
    await page.route('**/api/v1/timeline**', route => {
      route.fulfill({ status: 500, body: 'Server Error' });
    });

    await page.goto('/');
    
    // Should show error message
    await expect(page.getByText('Connection Failed')).toBeVisible();
    await expect(page.getByText('Unable to connect to the backend API')).toBeVisible();
  });
});