/**
 * Verify streaming tokens render through direct backend fetch.
 * The key fix: bypassing Next.js rewrites proxy which buffered SSE.
 */
import { test, expect, Page, Locator } from "@playwright/test";

async function createSessionRetry(page: Page): Promise<Locator> {
  for (let i = 0; i < 5; i++) {
    await page.getByRole("button", { name: /新对话/ }).click();
    try {
      const input = page.locator("textarea[placeholder*='输入您的问题']");
      await expect(input).toBeVisible({ timeout: 5000 });
      return input;
    } catch {
      if (i === 4) throw new Error("Failed to create session after 5 attempts");
      await page.waitForTimeout(2000);
    }
  }
  throw new Error("Failed to create session after 5 attempts");
}

test("direct fetch bypasses proxy - streaming works", async ({ page }) => {
  const logs: string[] = [];
  page.on("console", (msg) => logs.push(msg.text()));

  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("选择一个对话或创建新对话开始")).toBeVisible({ timeout: 10000 });

  const input = await createSessionRetry(page);

  await input.fill("什么是市盈率？");
  await input.press("Enter");

  // Input should be disabled while streaming
  await expect(input).toBeDisabled({ timeout: 10000 });

  // Verify markdown appears DURING streaming (before input re-enables)
  // This proves tokens are rendered incrementally, not all at once at the end
  await expect(page.locator(".markdown-body")).toBeVisible({ timeout: 120000 });
  expect(await input.isDisabled()).toBe(true);

  // Now wait for streaming to complete
  await expect(input).toBeEnabled({ timeout: 30000 });

  const markdownText = await page.locator(".markdown-body").textContent();
  expect(markdownText).toBeTruthy();
  console.log(`Response length: ${markdownText!.length} chars`);
});
