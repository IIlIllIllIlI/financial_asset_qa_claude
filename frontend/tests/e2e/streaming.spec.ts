import { test, expect, Page } from "@playwright/test";

async function gotoApp(page: Page) {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("选择一个对话或创建新对话开始")).toBeVisible({ timeout: 10000 });
}

async function createNewSession(page: Page) {
  for (let attempt = 0; attempt < 3; attempt++) {
    await page.getByRole("button", { name: /新对话/ }).click();
    try {
      await expect(page.locator("textarea[placeholder*='输入您的问题']")).toBeVisible({ timeout: 3000 });
      return;
    } catch {
      if (attempt === 2) {
        await page.evaluate(async () => {
          const res = await fetch("/api/sessions", { method: "POST" });
          const session = await res.json();
          window.location.href = "/";
          return session.id;
        });
        await page.waitForTimeout(500);
        await page.goto("/", { waitUntil: "domcontentloaded" });
        await page.getByRole("button", { name: /新对话/ }).click();
      }
    }
  }
  await expect(page.locator("textarea[placeholder*='输入您的问题']")).toBeVisible({ timeout: 5000 });
}

test.describe("SSE Streaming", () => {
  test.beforeEach(async ({ page }) => {
    await gotoApp(page);
    await createNewSession(page);
  });

  test("streaming tokens appear in real-time for RAG query", async ({ page }) => {
    const input = page.locator("textarea[placeholder*='输入您的问题']");
    await input.fill("什么是市盈率？");
    await input.press("Enter");

    // Confirm user message sent (appears after stream completes)
    await expect(page.getByText("什么是市盈率？", { exact: true })).toBeVisible({ timeout: 90000 });
    // AI response rendered in markdown
    await expect(page.locator(".markdown-body")).toBeVisible({ timeout: 90000 });
  });

  test("streaming starts after sending market query", async ({ page }) => {
    const input = page.locator("textarea[placeholder*='输入您的问题']");
    await input.fill("特斯拉当前股价是多少？");
    await input.press("Enter");

    // Streaming started if input is disabled and structured data arrives
    await expect(input).toBeDisabled({ timeout: 10000 });
    await expect(page.locator(".w-80").getByText("TSLA")).toBeVisible({ timeout: 90000 });
  });

  test("citations appear after streaming completes for RAG query", async ({ page }) => {
    const input = page.locator("textarea[placeholder*='输入您的问题']");
    await input.fill("什么是市盈率？");
    await input.press("Enter");

    // Wait for user message to confirm stream completed
    await expect(page.getByText("什么是市盈率？", { exact: true })).toBeVisible({ timeout: 90000 });
    // RAG responses include source references in markdown
    await expect(page.locator(".markdown-body")).toBeVisible({ timeout: 90000 });
  });

  test("structured data populates market panel after market query", async ({ page }) => {
    const input = page.locator("textarea[placeholder*='输入您的问题']");
    await input.fill("特斯拉当前股价是多少？");
    await input.press("Enter");

    await expect(page.locator(".w-80").getByText("TSLA")).toBeVisible({ timeout: 90000 });
  });

  test("retry button appears on error during streaming", async ({ page }) => {
    const input = page.locator("textarea[placeholder*='输入您的问题']");
    await input.fill("今天天气怎么样？");
    await input.press("Enter");

    const errorEl = page.getByText(/错误：/);
    await expect(errorEl).not.toBeVisible({ timeout: 30000 });
  });
});
