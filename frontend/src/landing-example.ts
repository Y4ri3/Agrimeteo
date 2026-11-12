import type { Criterion } from "./components/Gauge";

// Exemple réel : arachide à Kaolack, 30 jours jusqu'au 20 août 2025, données Open-Meteo, profil « à valider ».
// Valeurs relevées sur la réponse de l'API ; la page d'accueil fonctionne ainsi sans l'API.
export const EXAMPLE_CRITERIA: Criterion[] = [
  { id: "secheresse", label: "Plus longue période sans pluie", status: "ok", blocking: true, direction: "higher_is_worse",
    unit: "jours", window_days: 30, value: 4, vigilance: 10, unfavorable: 20,
    explanation: "Plus longue période sans pluie sur 30 jours : 4 jours, dans la limite acceptable pour ce profil." },
  { id: "pluie_cumulee", label: "Pluie cumulée", status: "ok", blocking: false, direction: "lower_is_worse",
    unit: "mm", window_days: 30, value: 146.9, vigilance: 60, unfavorable: null,
    explanation: "Pluie cumulée sur 30 jours : 146,9 mm, dans la limite acceptable pour ce profil." },
  { id: "chaleur", label: "Chaleur extrême (jour le plus chaud)", status: "ok", blocking: true, direction: "higher_is_worse",
    unit: "°C", window_days: 30, value: 35.3, vigilance: 38, unfavorable: 42,
    explanation: "Chaleur extrême (jour le plus chaud) sur 30 jours : 35,3 °C, dans la limite acceptable pour ce profil." },
];
