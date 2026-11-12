import type { IndicatorsResponse, WeatherResponse } from "../api";
import type { AsyncState } from "../useAsync";
import { Async } from "./Async";
import { Chart } from "./Chart";

// Définitions du cahier des charges (§7.3).
const DEFINITIONS = [
  ["Pluie cumulée", "Précipitations cumulées sur les derniers jours de la période (3, 7, 14, 30 jours ou la période entière)."],
  ["Plus forte pluie sur 3 jours", "Cumul maximal sur 3 jours consécutifs : indique si un épisode pluvieux suffisant a eu lieu."],
  ["Jours de pluie", "Nombre de jours avec au moins 1 mm de pluie."],
  ["Plus longue période sèche", "Plus longue série de jours consécutifs avec moins de 1 mm de pluie."],
  ["Température moyenne", "Moyenne des (Tmin + Tmax) / 2 sur la période."],
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

/** Indicateurs et courbes de GET /indicators et GET /weather, affichés sans aucun recalcul (I-05). */
export function Curves({
  weather,
  indicators,
  onRetryWeather,
  onRetryIndicators,
}: {
  weather: AsyncState<WeatherResponse>;
  indicators: AsyncState<IndicatorsResponse>;
  onRetryWeather: () => void;
  onRetryIndicators: () => void;
}) {
  return (
    <div className="curves">
      <Async state={indicators} onRetry={onRetryIndicators} errorTestId="dashboard-error">
        {(d) => (
          <div data-testid="indicators">
            <h4>Indicateurs de la période</h4>
            <dl className="facts">
              {rows(d.indicators).map(([label, v]) => (
                <div key={label}>
                  <dt>{label}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <p className="muted">Jours avec une donnée manquante ou rejetée : {d.quality.missing_days}</p>
          </div>
        )}
      </Async>

      <Async state={weather} onRetry={onRetryWeather} isEmpty={(d) => d.daily.length === 0} emptyText="Aucune donnée météo sur la période." errorTestId="dashboard-weather-error">
        {(d) => {
          const dates = d.daily.map((r) => r.date);
          return (
            <>
              <Chart title="Pluie de chaque jour" unit="mm" yLabel="Pluie (mm par jour)" dates={dates}
                howToRead="Chaque barre est la pluie d'une journée. Plus la barre est haute, plus il a plu ce jour-là. Pas de barre : pas de pluie. Passez la souris sur une barre pour lire la valeur."
                series={[{ name: "Pluie du jour", kind: "bar", values: d.daily.map((r) => r.precipitation_mm ?? null) }]} />
              <Chart title="Températures de chaque jour" unit="°C" yLabel="Température (°C)" dates={dates}
                howToRead="La courbe du haut est la température la plus chaude de la journée, celle du bas la plus fraîche. Plus les courbes montent, plus il fait chaud."
                series={[
                  { name: "Température maximale (journée)", kind: "line", values: d.daily.map((r) => r.tmax_c ?? null) },
                  { name: "Température minimale (nuit)", kind: "line", values: d.daily.map((r) => r.tmin_c ?? null) },
                ]} />
              <Chart title="Eau que l'air pourrait évaporer" unit="mm" yLabel="Évaporation possible (mm par jour)" dates={dates}
                howToRead="C'est l'évapotranspiration de référence (ET0) : la quantité d'eau que le soleil et le vent peuvent évaporer en un jour. Quand elle dépasse la pluie, les sols se dessèchent."
                series={[{ name: "Évaporation possible (ET0)", kind: "line", values: d.daily.map((r) => r.et0_mm ?? null) }]} />
              <p className="muted" data-testid="dashboard-source">{d.source.attribution ?? `Source : ${d.source.id}`}</p>
            </>
          );
        }}
      </Async>

      <details className="more">
        <summary>Définition des indicateurs</summary>
        <dl className="defs">{DEFINITIONS.map(([t, d]) => <div key={t}><dt>{t}</dt><dd>{d}</dd></div>)}</dl>
      </details>
    </div>
  );
}
