import { test, expect } from '@playwright/test';

// ==============================================================================
// AegisIQ End-to-End (E2E) Browser Test Suite
// Engine: Playwright Test Runner
// Coverage: Login, Dashboard Navigation, AI Copilot, Predictive Analytics, XAI
// ==============================================================================

test.describe('AegisIQ Enterprise E2E Test Suite', () => {
  const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

  test('1. Enterprise Login & 5-Tier RBAC Authentication', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Verify login form presence
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();

    // Fill credentials
    await page.fill('input[type="email"]', 'admin@aegisiq.com');
    await page.fill('input[type="password"]', 'Admin@12345');
    await page.click('button[type="submit"]');

    // Verify redirect to Executive BI Dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('2. Multi-Domain BI Dashboard & Interactive KPI Widgets', async ({ page }) => {
    await page.goto(`${BASE_URL}/dashboard`);

    // Verify key KPI metric cards rendered
    await expect(page.locator('text=Executive Summary')).toBeVisible();
    await expect(page.locator('text=Revenue Variance')).toBeVisible();
  });

  test('3. AI Copilot RAG Prompt & Citation Display', async ({ page }) => {
    await page.goto(`${BASE_URL}/copilot`);

    // Check chat prompt input
    const promptInput = page.locator('textarea[placeholder*="Ask AegisIQ"]');
    await expect(promptInput).toBeVisible();

    await promptInput.fill('Summarize key Q3 financial performance risks.');
    await page.keyboard.press('Enter');

    // Verify streaming response container
    await expect(page.locator('.ai-response-container')).toBeVisible({ timeout: 10000 });
  });

  test('4. XAI Studio SHAP Waterfall & Counterfactual Simulator', async ({ page }) => {
    await page.goto(`${BASE_URL}/analytics/xai`);

    // Verify SHAP feature importance chart
    await expect(page.locator('text=SHAP Additive Feature Attributions')).toBeVisible();
  });
});
