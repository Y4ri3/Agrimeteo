import { expect, test } from "@playwright/test";

test("parcours nominal : trois blocs distincts (I-02, A-06)", async ({ page }) => {
  await page.goto("/#/analyse");
  await expect(page.getByTestId("analyse-btn")).toBeEnabled();
  await page.getByTestId("analyse-btn").click();
  await expect(page.getByTestId("block-meteo")).toBeVisible();
  await expect(page.getByTestId("block-soil")).toBeVisible();
  await expect(page.getByTestId("block-cultivability")).toBeVisible();
  await expect(page.getByTestId("confidence")).toContainText("pas une probabilité");
});

test("parcours nominal : limites affichées (F7, FE-03)", async ({ page }) => {
  await page.goto("/#/analyse");
  await page.getByTestId("analyse-btn").click();
  await expect(page.getByTestId("limits")).toBeVisible();
});

test("source indisponible : message clair, application encore utilisable (I-03)", async ({ page }) => {
  const pannes = "**/api/v1/predictions";
  await page.route(pannes, (r) =>
    r.fulfill({ status: 502, contentType: "application/json",
      body: JSON.stringify({ error: { code: "PROVIDER_UNAVAILABLE", message: "Source indisponible", details: null }, request_id: "x" }) }));
  await page.goto("/#/analyse");
  await expect(page.getByTestId("analyse-btn")).toBeEnabled();
  await page.getByTestId("analyse-btn").click();
  await expect(page.getByTestId("error-message")).toContainText("service de données météo est indisponible");

  await page.unroute(pannes);
  await expect(page.getByTestId("analyse-btn")).toBeEnabled();
  await page.getByTestId("analyse-btn").click();
  await expect(page.getByTestId("block-meteo")).toBeVisible();
  await expect(page.getByTestId("error-message")).toHaveCount(0);
});
