import { test, expect } from '@playwright/test';

test.describe('Lucky Page', () => {
  test('loads lucky page with try your luck button', async ({ page }) => {
    await page.goto('/lucky');
    
    await expect(page.getByText("I'm Feeling Lucky")).toBeVisible();
    await expect(page.getByRole('button', { name: 'Try Your Luck' })).toBeVisible();
    await expect(page.getByText('Discover a random awesome repository')).toBeVisible();
  });

  test('shows initial state without results', async ({ page }) => {
    await page.goto('/lucky');
    
    await expect(page.getByText('Click "Try Your Luck" to discover')).toBeVisible();
  });

  test('fetches and displays random repository when button is clicked', async ({ page }) => {
    // Mock lucky API
    await page.route('**/api/v1/lucky**', async route => {
      const json = {
        timeline: [{
          date: '2024-01-15T00:00:00Z',
          items: [{
            name: 'lucky-repo',
            description: 'A randomly discovered repository',
            source: 'https://github.com/test/lucky-repo',
            list_name: 'awesome-lucky',
            list_source: 'https://github.com/test/awesome-lucky',
            time: '2024-01-15T10:00:00Z'
          }]
        }],
        page: 1,
        size: 1,
        total: 1,
        total_pages: 1
      };
      await route.fulfill({ json });
    });

    await page.goto('/lucky');
    
    // Click the lucky button
    await page.getByRole('button', { name: 'Try Your Luck' }).click();
    
    // Should show the random repository
    await expect(page.getByText('✨ Your lucky discovery ✨')).toBeVisible();
    await expect(page.getByText('lucky-repo')).toBeVisible();
    await expect(page.getByText('A randomly discovered repository')).toBeVisible();
  });

  test('shows loading state when fetching', async ({ page }) => {
    // Delay the API response to see loading state
    await page.route('**/api/v1/lucky**', route => {
      setTimeout(() => {
        const json = {
          timeline: [{
            date: '2024-01-15T00:00:00Z',
            items: [{
              name: 'test-repo',
              description: 'Test description',
              source: 'https://github.com/test/repo',
              list_name: 'test-list',
              list_source: 'https://github.com/test/list',
              time: '2024-01-15T10:00:00Z'
            }]
          }],
          page: 1,
          size: 1,
          total: 1,
          total_pages: 1
        };
        route.fulfill({ json });
      }, 1000);
    });

    await page.goto('/lucky');
    
    // Click button
    await page.getByRole('button', { name: 'Try Your Luck' }).click();
    
    // Should show loading state
    await expect(page.getByRole('button', { name: 'Rolling dice...' })).toBeVisible();
    await expect(page.getByText('Searching for luck')).toBeVisible();
  });

  test('can fetch multiple random repositories by clicking again', async ({ page }) => {
    let callCount = 0;
    
    // Mock API to return different responses
    await page.route('**/api/v1/lucky**', async route => {
      callCount++;
      const json = {
        timeline: [{
          date: '2024-01-15T00:00:00Z',
          items: [{
            name: `lucky-repo-${callCount}`,
            description: `Lucky repository number ${callCount}`,
            source: `https://github.com/test/lucky-repo-${callCount}`,
            list_name: 'awesome-lucky',
            list_source: 'https://github.com/test/awesome-lucky',
            time: '2024-01-15T10:00:00Z'
          }]
        }],
        page: 1,
        size: 1,
        total: 1,
        total_pages: 1
      };
      await route.fulfill({ json });
    });

    await page.goto('/lucky');
    
    // First click
    await page.getByRole('button', { name: 'Try Your Luck' }).click();
    await expect(page.getByText('lucky-repo-1')).toBeVisible();
    
    // Second click
    await page.getByRole('button', { name: 'Try Your Luck' }).click();
    await expect(page.getByText('lucky-repo-2')).toBeVisible();
    
    // Should not show the first result anymore
    await expect(page.getByText('lucky-repo-1')).not.toBeVisible();
  });

  test('handles API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/lucky**', route => {
      route.fulfill({ status: 500, body: 'Server Error' });
    });

    await page.goto('/lucky');
    
    // Click button
    await page.getByRole('button', { name: 'Try Your Luck' }).click();
    
    // Should show error message
    await expect(page.getByText('Connection Failed')).toBeVisible();
    await expect(page.getByText('Unable to connect to the backend API')).toBeVisible();
  });
});