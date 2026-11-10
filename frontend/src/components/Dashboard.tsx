import { getIndicators, getWeather, type IndicatorsResponse, type Prediction, type PredictionRequest } from "../api";
import { useAsync } from "../useAsync";
import { Async } from "./Async";
import { Chart } from "./Chart";

// Définitions du cahier des charges (§7.3).
const DEFINITIONS = [
  ["Pluie cumulée", "Précipitations cumulées sur les derniers jours de la fenêtre (3, 7, 14, 30 jours ou la fenêtre entière)."],
  ["Plus forte pluie sur 3 jours", "Cumul maximal sur 3 jours consécutifs : indique si un épisode pluvieux suffisant a eu lieu."],
  ["Jours de pluie", "Nombre de jours avec au moins 1 mm de pluie."],
  ["Plus longue période sèche", "Plus longue série de jours consécutifs avec moins de 1 mm de pluie."],
  ["Température moyenne", "Moyenne des (Tmin + Tmax) / 2 sur la fenêtre."],
  ["Jours de gel", "Nombre de jours où la température minimale est à 0 °C ou en dessous."],
  ["Amplitude thermique", "Moyenne de Tmax − Tmin."],
  ["ET0 cumulée", "Évapotranspiration de référence cumulée (FAO n° 56), si la source la fournit."],
  ["Bilan pluie − ET0", "Pluie cumulée moins ET0 : bilan simplifié de l'atmosphère, pas un bilan hydrique du sol."],
];

type Ind = IndicatorsResponse["indicators"];
const value = (v: number | null | undefined, unit: string) => (v === null || v === undefined ? "n/d" : `${v}${unit}`);

function rows(i: Ind): [string, string][] {
  return [
    ...Object.entries(i.rain_sum_mm).map(([k, v]): [string, string] => [`Pluie cumulée ${k}`, value(v, " mm")]),
    ["Plus forte pluie sur 3 jours", value(i.rain_max_3d_mm, " mm")],
    ["Jours de pluie", value(i.wet_days, "")],
    ["Plus longue période sèche", value(i.max_dry_spell_days, " jours")],
    ["Température moyenne", value(i.tmean_c, " °C")],
    ["Tmin la plus basse", value(i.tmin_min_c, " °C")],
    ["Tmax la plus haute", value(i.tmax_max_c, " °C")],
    ["Jours de gel", String(i.frost_days)],
    ["Amplitude thermique", value(i.diurnal_range_c, " °C")],
    ["ET0 cumulée", value(i.et0_sum_mm, " mm")],
    ["Bilan pluie − ET0", value(i.water_balance_mm, " mm")],
    ["Humidité de l'air", value(i.rh_mean_pct, " %")],
  ];
}

/** Tableau de bord : affiche les valeurs de GET /weather et GET /indicators, sans aucun recalcul (I-05). */
export function Dashboard({ request, result }: { request: PredictionRequest; result: Prediction }) {
  const w = result.analysis_window;
  const { latitude, longitude } = request.location;
  const key = `${latitude}|${longitude}|${w.start_date}|${w.end_date}`;
  const [weather, retryWeather] = useAsync(() => getWeather(latitude, longitude, w.start_date, w.end_date), `w${key}`);
  const [ind, retryInd] = useAsync(() => getIndicators(latitude, longitude, w.end_date, w.days), `i${key}`);

  return (
    <section aria-labelledby="t-dash">
      <h2 id="t-dash">Tableau de bord météo</h2>
      <p className="muted">du {w.start_date} au {w.end_date}</p>

      <Async state={ind} onRetry={retryInd} errorTestId="dashboard-error">
        {(d) => (
          <div className="card" data-testid="indicators">
            <h3>Indicateurs</h3>
            <dl>
              {rows(d.indicators).map(([label, v]) => (
                <div key={label}>
                  <dt>{label}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <p className="muted">Jours avec donnée manquante : {d.quality.missing_days}</p>
          </div>
        )}
      </Async>

      <Async state={weather} onRetry={retryWeather} isEmpty={(d) => d.daily.length === 0} emptyText="Aucune donnée météo sur la période." errorTestId="dashboard-weather-error">
        {(d) => {
          const dates = d.daily.map((r) => r.date);
          return (
            <>
              <Chart title="Précipitations" unit="mm" dates={dates} series={[{ name: "Pluie", kind: "bar", values: d.daily.map((r) => r.precipitation_mm ?? null) }]} />
              <Chart title="Températures" unit="°C" dates={dates} series={[
                { name: "Tmax", kind: "line", values: d.daily.map((r) => r.tmax_c ?? null) },
                { name: "Tmin", kind: "line", values: d.daily.map((r) => r.tmin_c ?? null) },
              ]} />
              <Chart title="Évapotranspiration de référence (ET0)" unit="mm" dates={dates} series={[{ name: "ET0", kind: "line", values: d.daily.map((r) => r.et0_mm ?? null) }]} />
              <p className="muted" data-testid="dashboard-source">
                {d.source.attribution ?? `Source : ${d.source.id}`}
              </p>
            </>
          );
        }}
      </Async>

      <details>
        <summary>Définition des indicateurs</summary>
        <dl>{DEFINITIONS.map(([t, d]) => <div key={t}><dt>{t}</dt><dd>{d}</dd></div>)}</dl>
      </details>
    </section>
  );
}
