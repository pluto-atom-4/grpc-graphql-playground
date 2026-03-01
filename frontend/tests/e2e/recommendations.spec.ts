import { test, expect } from '@playwright/test';

test.describe('Travel Recommendations Page', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page
    await page.goto('/');
  });

  test('should display the page title and heading', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle('Travel Recommendations');

    // Check heading
    await expect(page.locator('h1')).toContainText('Travel Recommendations');
  });

  test('should have a form to input user ID', async ({ page }) => {
    // Check for input field
    const userInput = page.locator('input[placeholder*="user ID"]');
    await expect(userInput).toBeVisible();

    // Check for submit button
    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await expect(submitButton).toBeVisible();
  });

  test('should show error when submitting empty user ID', async ({ page }) => {
    // Try to submit without entering anything
    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await submitButton.click();

    // Should see error message
    await expect(page.locator('text=Please enter a user ID')).toBeVisible();
  });

  test('should accept and display user ID input', async ({ page }) => {
    // Enter a user ID
    const userInput = page.locator('input[placeholder*="user ID"]');
    await userInput.fill('test_user_123');

    // Verify input value
    await expect(userInput).toHaveValue('test_user_123');

    // Submit
    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await expect(submitButton).toBeEnabled();
  });

  test('should display loading state while fetching', async ({ page }) => {
    // Mock network to add delay
    await page.route('**/graphql', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.continue();
    });

    // Enter user ID and submit
    const userInput = page.locator('input[placeholder*="user ID"]');
    await userInput.fill('test_user_456');

    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await submitButton.click();

    // Check for loading state
    await expect(submitButton).toHaveText('Loading...');
    await expect(submitButton).toBeDisabled();
  });

  test('should handle GraphQL errors gracefully', async ({ page }) => {
    // Mock GraphQL to return an error
    await page.route('**/graphql', async (route) => {
      await route.abort('failed');
    });

    // Enter user ID and submit
    const userInput = page.locator('input[placeholder*="user ID"]');
    await userInput.fill('test_user_789');

    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await submitButton.click();

    // Should show an error message
    await expect(page.locator('.text-red')).toBeVisible();
  });

  test('should display empty state when no results', async ({ page }) => {
    // Mock GraphQL to return empty recommendations
    await page.route('**/graphql', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          data: {
            recommendations: [],
          },
        }),
      });
    });

    // Enter user ID and submit
    const userInput = page.locator('input[placeholder*="user ID"]');
    await userInput.fill('new_user');

    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await submitButton.click();

    // Should show empty state message
    await expect(
      page.locator('text=Enter your user ID to see personalized')
    ).toBeVisible();
  });

  test('should display recommendations as cards', async ({ page }) => {
    // Mock GraphQL to return sample recommendations
    await page.route('**/graphql', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          data: {
            recommendations: [
              {
                id: 'paris_001',
                name: 'Paris',
                region: 'Île-de-France',
                country: 'France',
                score: 0.95,
              },
              {
                id: 'tokyo_001',
                name: 'Tokyo',
                region: 'Kantō',
                country: 'Japan',
                score: 0.87,
              },
            ],
          },
        }),
      });
    });

    // Enter user ID and submit
    const userInput = page.locator('input[placeholder*="user ID"]');
    await userInput.fill('test_recommendations');

    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await submitButton.click();

    // Wait for results and check cards are displayed
    await expect(page.locator('text=Recommended Destinations')).toBeVisible();

    // Check Paris card
    await expect(page.locator('text=Paris')).toBeVisible();
    await expect(page.locator('text=France')).toBeVisible();
    await expect(page.locator('text=95%')).toBeVisible();

    // Check Tokyo card
    await expect(page.locator('text=Tokyo')).toBeVisible();
    await expect(page.locator('text=Japan')).toBeVisible();
    await expect(page.locator('text=87%')).toBeVisible();
  });

  test('should display correct score percentage for recommendations', async ({
    page,
  }) => {
    // Mock GraphQL with specific scores
    await page.route('**/graphql', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          data: {
            recommendations: [
              {
                id: 'dest_1',
                name: 'Destination 1',
                region: 'Region 1',
                country: 'Country 1',
                score: 0.5,
              },
              {
                id: 'dest_2',
                name: 'Destination 2',
                region: 'Region 2',
                country: 'Country 2',
                score: 0.25,
              },
            ],
          },
        }),
      });
    });

    // Submit
    const userInput = page.locator('input[placeholder*="user ID"]');
    await userInput.fill('score_test');

    const submitButton = page.locator('button:has-text("Get Recommendations")');
    await submitButton.click();

    // Verify scores are displayed correctly
    await expect(page.locator('text=50%')).toBeVisible();
    await expect(page.locator('text=25%')).toBeVisible();
  });
});
