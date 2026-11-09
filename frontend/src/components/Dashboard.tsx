import { getIndicators, getWeather, type Prediction, type PredictionRequest } from "../api";
import { useAsync } from "../useAsync";
import { Async } from "./Async";
import { Chart } from "./Chart";

// Définitions du cahier des charges (§7.3).
const DEFINITIONS = [
  ["Pluie cumulée", "Précipitations cumulées sur les 7 derniers jours et sur la fenêtre."],
  ["Jours de gel", "Nombre de jours où la température minimale est à 0 °C ou en dessous."],
  ["Bilan pluie − ET0", "Pluie cumulée moins évapotranspiration de référence : bilan simplifié de l'atmosphère, pas un bilan hydrique du sol."],
];

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
              {Object.entries(d.indicators.rain_sum_mm).map(([k, v]) => (
                <div key={k}><dt>Pluie cumulée {k}</dt><dd>{v === null ? "n/d" : `${v} mm`}</dd></div>
              ))}
              <div><dt>Jours de gel</dt><dd>{d.indicators.frost_days}</dd></div>
              <div><dt>Bilan pluie − ET0</dt><dd>{d.indicators.water_balance_mm === null ? "n/d" : `${d.indicators.water_balance_mm} mm`}</dd></div>
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
