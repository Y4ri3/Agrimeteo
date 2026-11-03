import { expect, test } from "@playwright/test";

// Passe par nginx comme le navigateur : prouve le relais /api et le contrat sur la pile réelle.
const location = { latitude: 14.69, longitude: -17.44 };

test("smoke : le frontend et l'API répondent, une analyse aboutit (C-06)", async ({ request }) => {
  expect((await request.get("/")).ok()).toBeTruthy();

  const crops = await request.get("/api/v1/crops");
  expect(crops.ok()).toBeTruthy();
  const { crops: list } = await crops.json();
  expect(list.length).toBeGreaterThan(0);

  const analyse = await request.post("/api/v1/predictions", { data: { crop_id: list[0].id, location } });
  expect(analyse.ok()).toBeTruthy();
  const body = await analyse.json();
  expect(body.request_id).toBeTruthy();
  expect(body.meteorological_favorability).toBeTruthy();
  expect(body.soil_moisture).toBeTruthy();
  expect(body.agronomic_cultivability).toBeTruthy();
  expect(body.limits.length).toBeGreaterThan(0);
});

test("erreur : format commun avec code stable, sans trace interne (A-03)", async ({ request }) => {
  const r = await request.post("/api/v1/predictions", { data: { crop_id: "inconnue", location } });
  expect(r.status()).toBe(404);
  const body = await r.json();
  expect(body.error.code).toBe("CROP_NOT_FOUND");
  expect(body.request_id).toBeTruthy();
  expect(JSON.stringify(body)).not.toContain("Traceback");
});
