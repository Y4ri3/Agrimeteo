import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { expect, test } from "vitest";
import App from "../src/App";
import { API, errorBody, server } from "./mocks";

async function analyse() {
  const user = userEvent.setup();
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("analyse-btn")).toBeEnabled());
  await user.click(screen.getByTestId("analyse-btn"));
  return user;
}

test("parcours nominal : culture, zone, résultat (FE-01)", async () => {
  await analyse();
  expect(await screen.findByTestId("block-meteo")).toBeInTheDocument();
});

test("le résultat affiche ensemble les trois notions et les limites (FE-03)", async () => {
  await analyse();
  const result = await screen.findByTestId("result");
  expect(within(result).getByTestId("block-meteo")).toHaveTextContent("Indéterminé");
  expect(within(result).getByTestId("block-soil")).toHaveTextContent("Non disponible");
  expect(within(result).getByTestId("block-cultivability")).toHaveTextContent("Non évaluée");
  expect(within(result).getByTestId("limits")).toHaveTextContent("pas de la parcelle");
  expect(within(result).getByTestId("confidence")).toHaveTextContent("pas une probabilité");
});

test("l'attribution de la source est affichée (FE-06)", async () => {
  await analyse();
  expect(await screen.findByTestId("attribution")).toHaveTextContent("Weather data by Open-Meteo.com");
});

test.each([
  ["VALIDATION_ERROR", 422, "Vérifiez les coordonnées et les dates saisies."],
  ["PERIOD_TOO_LONG", 422, "La période demandée dépasse la durée maximale."],
  ["DATE_OUT_OF_RANGE", 422, "Aucune donnée disponible pour cette date."],
  ["CROP_NOT_FOUND", 404, "Cette culture n'existe pas."],
  ["PROVIDER_UNAVAILABLE", 502, "Le service de données météo est indisponible."],
  ["PROVIDER_RATE_LIMITED", 503, "Trop de demandes : réessayez dans un instant."],
  ["PROVIDER_TIMEOUT", 504, "Le service de données ne répond pas."],
  ["INTERNAL_ERROR", 500, "Une erreur est survenue. (identifiant de requête : req-err)"],
])("le code %s produit son propre message (FE-02)", async (code, status, message) => {
  server.use(http.post(`${API}/predictions`, () => HttpResponse.json(errorBody(code), { status })));
  await analyse();
  expect(await screen.findByTestId("error-message")).toHaveTextContent(message);
});

test("serveur injoignable : message clair, formulaire encore utilisable (FE-02, FE-04)", async () => {
  server.use(http.post(`${API}/predictions`, () => HttpResponse.error()));
  await analyse();
  expect(await screen.findByTestId("error-message")).toHaveTextContent("injoignable");
  expect(screen.getByTestId("analyse-btn")).toBeEnabled();
});

test("la liste des cultures gère l'erreur avec un bouton Réessayer (FE-04)", async () => {
  server.use(http.get(`${API}/crops`, () => HttpResponse.json(errorBody("PROVIDER_UNAVAILABLE"), { status: 502 })));
  const user = userEvent.setup();
  render(<App />);
  expect(await screen.findByTestId("crops-error")).toBeInTheDocument();
  server.resetHandlers();
  await user.click(screen.getByRole("button", { name: "Réessayer" }));
  expect(await screen.findByTestId("crop-select")).toBeInTheDocument();
});

test("la liste des cultures vide est expliquée (FE-04)", async () => {
  server.use(http.get(`${API}/crops`, () => HttpResponse.json({ crops: [] })));
  render(<App />);
  expect(await screen.findByText("Aucune culture disponible.")).toBeInTheDocument();
  expect(screen.getByTestId("analyse-btn")).toBeDisabled();
});

test("recherche de lieu : résultat choisi, puis liste vide sans erreur (FE-04)", async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.type(screen.getByLabelText("Rechercher un lieu"), "thies");
  await user.click(screen.getByRole("button", { name: "Rechercher" }));
  await user.click(await screen.findByRole("button", { name: /Thiès, Thiès, Sénégal/ }));
  expect(screen.getByTestId("selected-place")).toHaveTextContent("Thiès");
  expect(screen.getByLabelText("Latitude")).toHaveValue(14.79);

  await user.clear(screen.getByLabelText("Rechercher un lieu"));
  await user.type(screen.getByLabelText("Rechercher un lieu"), "zzzz");
  await user.click(screen.getByRole("button", { name: "Rechercher" }));
  expect(await screen.findByText(/Aucun lieu trouvé/)).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

test("les coordonnées invalides bloquent l'analyse", async () => {
  const user = userEvent.setup();
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("analyse-btn")).toBeEnabled());
  await user.clear(screen.getByLabelText("Latitude"));
  await user.type(screen.getByLabelText("Latitude"), "120");
  expect(screen.getByTestId("analyse-btn")).toBeDisabled();
});

test("le tableau de bord affiche les valeurs de l'API sans recalcul (I-05)", async () => {
  const user = await analyse();
  await screen.findByTestId("result");
  await user.click(screen.getByRole("button", { name: "Tableau de bord" }));
  const box = await screen.findByTestId("indicators");
  expect(box).toHaveTextContent("61.2 mm");
  expect(box).toHaveTextContent("12.7 mm");
  expect(await screen.findAllByRole("img")).toHaveLength(3);
  expect(await screen.findByTestId("dashboard-source")).toHaveTextContent("Open-Meteo");
});

test("le tableau de bord gère l'erreur du fournisseur (FE-04)", async () => {
  server.use(http.get(`${API}/weather`, () => HttpResponse.json(errorBody("PROVIDER_TIMEOUT"), { status: 504 })));
  const user = await analyse();
  await screen.findByTestId("result");
  await user.click(screen.getByRole("button", { name: "Tableau de bord" }));
  expect(await screen.findByTestId("dashboard-weather-error")).toHaveTextContent("ne répond pas");
});

test("sans analyse, résultat et tableau de bord invitent à analyser", async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole("button", { name: "Résultat" }));
  expect(screen.getByText(/Lancez d'abord une analyse/)).toBeInTheDocument();
});
