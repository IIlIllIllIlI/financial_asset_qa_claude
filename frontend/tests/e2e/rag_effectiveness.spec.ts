/**
 * RAG effectiveness test — verify the LLM uses our ingested documents,
 * not just its pre-training knowledge.
 *
 * Strategy: query specific numbers from a fake financial framework document
 * that NO LLM can know from pre-training.
 */
import { test, expect, Page } from "@playwright/test";

async function gotoApp(page: Page) {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("选择一个对话或创建新对话开始")).toBeVisible({ timeout: 10000 });
}

async function createNewSession(page: Page) {
  for (let i = 0; i < 5; i++) {
    await page.getByRole("button", { name: /新对话/ }).click();
    try {
      const input = page.locator("textarea[placeholder*='输入您的问题']");
      await expect(input).toBeVisible({ timeout: 5000 });
      return input;
    } catch {
      if (i === 4) throw new Error("Failed to create session");
      await page.waitForTimeout(2000);
    }
  }
  throw new Error("Failed to create session");
}

test.describe("RAG Effectiveness", () => {
  test("retrieves specific number from ingested finance framework doc", async ({ page }) => {
    await gotoApp(page);
    const input = await createNewSession(page);

    // Query a specific metric ONLY in our fake document
    await input.fill("七因子宏观对冲框架的夏普比率是多少？");
    await input.press("Enter");

    // Verify markdown appears DURING streaming (proves incremental rendering)
    await expect(input).toBeDisabled({ timeout: 10000 });
    await expect(page.locator(".markdown-body")).toBeVisible({ timeout: 120000 });

    // Then wait for streaming to COMPLETE before reading final answer
    await expect(input).toBeEnabled({ timeout: 120000 });

    const response = await page.locator(".markdown-body").textContent();
    console.log(`Response: ${response!.length} chars`);

    // Must contain the specific number from our document (1.54 Sharpe ratio)
    expect(response).toContain("1.54");

    // Also verify the source citation points to our document
    const pageText = await page.locator("body").textContent();
    expect(pageText).toContain("seven_factor_macro_hedge");
  });

  test("retrieves framework parameters that don't exist elsewhere", async ({ page }) => {
    await gotoApp(page);
    const input = await createNewSession(page);

    // Query about the shrinkage parameter
    await input.fill("七因子宏观对冲框架的Ledoit-Wolf收缩参数是多少？");
    await input.press("Enter");

    await expect(input).toBeDisabled({ timeout: 10000 });
    await expect(page.locator(".markdown-body")).toBeVisible({ timeout: 120000 });
    await expect(input).toBeEnabled({ timeout: 120000 });

    const response = await page.locator(".markdown-body").textContent();
    // λ = 0.37 is a document-specific parameter
    expect(response).toMatch(/0\.37/);
  });

  test("intent is rag not market for financial concept queries", async ({ page }) => {
    await gotoApp(page);
    const input = await createNewSession(page);

    // This query is about a financial concept/framework, not a stock price
    await input.fill("SFMHF v4.1 和桥水全天候策略的主要区别是什么？");
    await input.press("Enter");

    await expect(input).toBeDisabled({ timeout: 10000 });
    await expect(page.locator(".markdown-body")).toBeVisible({ timeout: 120000 });
    await expect(input).toBeEnabled({ timeout: 120000 });

    const response = await page.locator(".markdown-body").textContent();
    console.log(`Response: ${response!.length} chars`);

    // Should mention key concepts from our document
    expect(response).toContain("协方差");
    expect(response).toContain("四象限");
  });
});
