import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import App from "../src/App";

const pred = {
  request_id: "r", meteorological_favorability: { level: "indetermine", summary: "S" },
  soil_moisture: { available: false }, agronomic_cultivability: { status: "non_evaluee", reason: "R" },
  confidence: { level: "faible", basis: "B" }, limits: [],
};
const json = (b: unknown, ok = true) => Promise.resolve({ ok, status: ok ? 200 : 502, json: () => Promise.resolve(b) });

afterEach(() => vi.unstubAllGlobals());

test("affiche les trois blocs distincts après analyse", async () => {
  vi.stubGlobal("fetch", vi.fn((u: string) => u.includes("crops")
    ? json({ crops: [{ id: "c", label: "C" }] }) : json(pred)));
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("analyse-btn")).toBeEnabled());
  fireEvent.click(screen.getByTestId("analyse-btn"));
  await waitFor(() => expect(screen.getByTestId("block-cultivability")).toBeInTheDocument());
  expect(screen.getByTestId("block-meteo")).toBeInTheDocument();
  expect(screen.getByTestId("block-soil")).toBeInTheDocument();
});

test("affiche un message clair si l'API échoue", async () => {
  vi.stubGlobal("fetch", vi.fn(() => json({ error: { message: "Source indisponible" } }, false)));
  render(<App />);
  expect(await screen.findByTestId("error-message")).toHaveTextContent("Source indisponible");
});
