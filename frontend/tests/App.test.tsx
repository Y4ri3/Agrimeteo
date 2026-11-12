import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { beforeEach, expect, test } from "vitest";
import App from "../src/App";
import { API, errorBody, server } from "./mocks";

beforeEach(() => {
  window.location.hash = "#/analyse";
});

async function analyse() {
  const user = userEvent.setup();
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("analyse-btn")).toBeEnabled());
  await user.click(screen.getByTestId("analyse-btn"));
  return user;
}

test("l'accueil montre un exemple de réponse avec ses jauges", () => {
  window.location.hash = "#/";
  render(<App />);
  expect(screen.getByText("À quoi ressemble une réponse")).toBeInTheDocument();
  expect(screen.getAllByRole("img", { name: /Limites : à surveiller/ }).length).toBeGreaterThanOrEqual(3);
  expect(screen.getByText("Quatre cultures")).toBeInTheDocument();
});

test("la page d'accueil dit à quoi sert l'outil et mène à l'application", () => {
  window.location.hash = "#/";
  render(<App />);
  expect(screen.getByRole("heading", { level: 1, name: /Puis-je semer/ })).toBeInTheDocument();
  const cta = screen.getAllByRole("link", { name: "Vérifier pour mon champ" });
  expect(cta[0]).toHaveAttribute("href", "#/analyse");
  expect(screen.getByRole("img", { name: /Pluie quotidienne à Kaolack/ })).toBeInTheDocument();
  expect(screen.getByText(/Ce que l'outil ne dit pas/)).toBeInTheDocument();
});

test("parcours nominal : culture, lieu, verdict (FE-01)", async () => {
  await analyse();
  expect(await screen.findByTestId("block-meteo")).toHaveTextContent("Oui, sous réserve");
});

test("le résultat affiche ensemble les trois notions et les limites (FE-03)", async () => {
  await analyse();
  const result = await screen.findByTestId("result");
  expect(within(result).getByTestId("block-soil")).toHaveTextContent("Non disponible");
  expect(within(result).getByTestId("block-cultivability")).toHaveTextContent("Non évalué");
  expect(within(result).getByTestId("limits")).toHaveTextContent("pas de la parcelle");
  expect(within(result).getByTestId("confidence")).toHaveTextContent("pas une probabilité");
});

test("les repères à surveiller et le statut du profil sont écrits dans le verdict", async () => {
  await analyse();
  const verdict = await screen.findByTestId("block-meteo");
  expect(verdict).toHaveTextContent("À surveiller. Chaleur extrême sur 30 jours : 38,5 °C");
  expect(verdict).toHaveTextContent("Non évaluable. Fraîcheur sur 30 jours : seuil non défini");
  expect(verdict).toHaveTextContent("encore à valider");
});

test("chaque repère a sa jauge : valeur, limites et explication", async () => {
  await analyse();
  const card = await screen.findByTestId("critere-chaleur");
  expect(within(card).getByRole("img", { name: /Chaleur extrême : 38,5 °C\. Limites : à surveiller dès 38 °C, défavorable dès 42 °C/ })).toBeInTheDocument();
  expect(card).toHaveTextContent("À surveiller");
  expect(card).toHaveTextContent("Un résultat défavorable ici suffit pour répondre non");
  expect(within(screen.getByTestId("critere-pluie")).getByRole("img", { name: /à surveiller à 60 mm ou moins/ })).toBeInTheDocument();
  expect(screen.getByTestId("critere-froid")).toHaveTextContent("Non évaluable");
  expect(within(screen.getByTestId("critere-froid")).queryByRole("img")).not.toBeInTheDocument(); // rien à dessiner sans seuil
});

test("les chiffres clés de la période viennent de l'API", async () => {
  await analyse();
  const facts = await screen.findByTestId("key-facts");
  await waitFor(() => expect(facts).toHaveTextContent("61,2 mm"));
});

test("l'attribution, la licence et la date de récupération sont affichées (FE-06)", async () => {
  await analyse();
  const text = await screen.findByTestId("attribution");
  expect(text).toHaveTextContent("Weather data by Open-Meteo.com");
  expect(text).toHaveTextContent("Licence CC BY 4.0");
  expect(text).toHaveTextContent("récupérées le 10/11/2026");
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

test("chaque culture dit où elle est cultivée", async () => {
  render(<App />);
  expect(await screen.findByText("Bassin arachidier")).toBeInTheDocument();
});

test("on peut choisir l'autre culture", async () => {
  server.use(http.get(`${API}/crops`, () => HttpResponse.json({ crops: [
    { id: "a", label: "Arachide", rule_profile_version: "1", rule_status: "a_valider", zones: "Bassin arachidier" },
    { id: "m", label: "Mil", rule_profile_version: "1", rule_status: "a_valider" },
  ] })));
  const user = userEvent.setup();
  render(<App />);
  await user.click(await screen.findByLabelText("Mil"));
  expect(screen.getByLabelText("Mil")).toBeChecked();
});

test("recherche de lieu : résultat choisi, puis liste vide sans erreur (FE-04)", async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.type(screen.getByLabelText("Chercher un autre lieu"), "thies");
  await user.click(screen.getByRole("button", { name: "Rechercher" }));
  await user.click(await screen.findByRole("button", { name: /^Thiès, Sénégal$/ }));
  expect(screen.getByTestId("selected-place")).toHaveTextContent("Thiès");

  await user.type(screen.getByLabelText("Chercher un autre lieu"), "zzzz");
  await user.click(screen.getByRole("button", { name: "Rechercher" }));
  expect(await screen.findByText(/Aucun lieu trouvé/)).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});

test("un lieu fréquent se choisit en un clic", async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.click(screen.getByRole("button", { name: "Thiès" }));
  await waitFor(() => expect(screen.getByTestId("selected-place")).toHaveTextContent("Thiès"));
});

test("une durée invalide bloque l'analyse", async () => {
  const user = userEvent.setup();
  render(<App />);
  await waitFor(() => expect(screen.getByTestId("analyse-btn")).toBeEnabled());
  await user.click(screen.getByText("Changer la période"));
  await user.clear(screen.getByLabelText(/Nombre de jours/));
  await user.type(screen.getByLabelText(/Nombre de jours/), "200");
  expect(screen.getByTestId("analyse-btn")).toBeDisabled();
});

test("la frise de pluie et les indicateurs viennent de l'API, sans recalcul (I-05)", async () => {
  await analyse();
  await screen.findByTestId("result");
  expect(await screen.findByRole("img", { name: /Pluie de chaque jour du/ })).toBeInTheDocument();
  const box = await screen.findByTestId("indicators");
  expect(box).toHaveTextContent("61.2 mm");
  expect(box).toHaveTextContent("12.7 mm");
  expect(await screen.findByTestId("dashboard-source")).toHaveTextContent("Open-Meteo");
});

test("les courbes gèrent l'erreur du fournisseur (FE-04)", async () => {
  server.use(http.get(`${API}/weather`, () => HttpResponse.json(errorBody("PROVIDER_TIMEOUT"), { status: 504 })));
  await analyse();
  await screen.findByTestId("result");
  expect(await screen.findByTestId("dashboard-weather-error")).toHaveTextContent("ne répond pas");
});
