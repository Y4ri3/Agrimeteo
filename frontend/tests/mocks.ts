import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const API = "http://api.test/api/v1";

const quality = { completeness_pct: { precipitation_mm: 94.1, tmax_c: 100, tmin_c: 100, rh_mean_pct: 100, et0_mm: 100 }, missing_days: 2, flagged_values: [] };
const source = { id: "open_meteo", attribution: "Weather data by Open-Meteo.com", license: "CC BY 4.0", retrieved_at: "2026-11-10T12:00:00Z", spatial_resolution_note: null };

export const prediction = {
  request_id: "req-1",
  analysis_window: { start_date: "2026-09-22", end_date: "2026-10-21", days: 30 },
  crop: { id: "c", label: "Culture C", rule_profile_version: "0.1.0", rule_status: "a_valider" },
  meteorological_favorability: {
    level: "favorable_sous_reserve",
    summary: "Conditions compatibles avec le profil, sous réserve.",
    criteria: [
      { id: "chaleur", label: "Chaleur extrême", status: "vigilance", blocking: true, direction: "higher_is_worse", unit: "°C", window_days: 30, value: 38.5, vigilance: 38, unfavorable: 42, explanation: "Chaleur extrême sur 30 jours : 38,5 °C, ce qui atteint ou dépasse le seuil de vigilance (38 °C)." },
      { id: "pluie", label: "Pluie cumulée", status: "ok", blocking: false, direction: "lower_is_worse", unit: "mm", window_days: 30, value: 120, vigilance: 60, unfavorable: null, explanation: "Pluie cumulée sur 30 jours : 120 mm, dans la limite acceptable pour ce profil." },
      { id: "froid", label: "Fraîcheur", status: "non_evaluable", blocking: true, direction: "lower_is_worse", unit: "°C", window_days: 30, value: null, vigilance: null, unfavorable: null, explanation: "Fraîcheur sur 30 jours : seuil non défini pour ce profil (à valider)." },
    ],
  },
  soil_moisture: { kind: "modelled_indicator", available: false, note: "Estimation de modèle, non mesurée." },
  agronomic_cultivability: { status: "non_evaluee", reason: "Aucune donnée de sol fiable." },
  indicators: { rain_sum_mm: { "7d": 12.3, "30d": 61.2 }, frost_days: 0, water_balance_mm: 12.7 },
  data_quality: quality,
  source,
  confidence: { level: "faible", basis: "Ce n'est pas une probabilité." },
  limits: ["Résolution de la maille, pas de la parcelle."],
  attribution: "Weather data by Open-Meteo.com",
};

export const errorBody = (code: string, message = "msg serveur") => ({ error: { code, message, details: null }, request_id: "req-err" });

export const handlers = [
  http.get(`${API}/crops`, () => HttpResponse.json({ crops: [{ id: "c", label: "Culture C", rule_profile_version: "0.1.0", rule_status: "a_valider", zones: "Bassin arachidier" }] })),
  http.get(`${API}/geocode`, ({ request }) => {
    const q = (new URL(request.url).searchParams.get("q") ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    return HttpResponse.json({ results: q === "thies" ? [{ name: "Thiès", country: "Sénégal", admin1: "Thiès", latitude: 14.79, longitude: -16.93 }] : [] });
  }),
  http.post(`${API}/predictions`, () => HttpResponse.json(prediction)),
  http.get(`${API}/indicators`, () => HttpResponse.json({ request_id: "r", location: { latitude: 14.7, longitude: -17.4 }, window_days: 30, source, indicators: prediction.indicators, quality })),
  http.get(`${API}/weather`, () => HttpResponse.json({
    request_id: "r", location: { latitude: 14.7, longitude: -17.4 }, source, period: { start_date: "2026-10-01", end_date: "2026-10-03" }, units: {}, quality,
    daily: [
      { date: "2026-10-01", precipitation_mm: 1.5, tmax_c: 31, tmin_c: 22, rh_mean_pct: 60, et0_mm: 4 },
      { date: "2026-10-02", precipitation_mm: null, tmax_c: 32, tmin_c: 23, rh_mean_pct: 61, et0_mm: 4.5 },
      { date: "2026-10-03", precipitation_mm: 0, tmax_c: 30, tmin_c: 21, rh_mean_pct: 62, et0_mm: 4.1 },
    ],
  })),
];

export const server = setupServer(...handlers);
