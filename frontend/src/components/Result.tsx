import { getIndicators, getWeather, type Prediction, type PredictionRequest } from "../api";
import { LEVELS, STATUS, frDate } from "../labels";
import { useAsync } from "../useAsync";
import { CriterionCard } from "./CriterionCard";
import { Curves } from "./Curves";
import { RainCurtain } from "./RainCurtain";

const CONFIDENCE: Record<string, string> = { faible: "faible", moyenne: "moyenne", elevee: "élevée" };
const VARIABLES: Record<string, string> = {
  precipitation_mm: "Pluie",
  tmax_c: "Température maximale",
  tmin_c: "Température minimale",
  tmean_c: "Température moyenne",
  rh_mean_pct: "Humidité de l'air",
  et0_mm: "Évaporation possible (ET0)",
};

/** Écran Résultat : affiche la réponse de l'API telle quelle, aucun calcul côté frontend (A-08, I-05). */
export function Result({ request, result }: { request: PredictionRequest; result: Prediction }) {
  const w = result.analysis_window;
  const { latitude, longitude } = request.location;
  const key = `${latitude}|${longitude}|${w.start_date}|${w.end_date}`;
  const [weather, retryWeather] = useAsync(() => getWeather(latitude, longitude, w.start_date, w.end_date), `w${key}`);
  const [indicators, retryIndicators] = useAsync(() => getIndicators(latitude, longitude, w.end_date, w.days), `i${key}`);

  const fav = result.meteorological_favorability;
  const level = LEVELS[fav.level] ?? { title: fav.level, tone: "inconnu" };
  const concerns = fav.criteria.filter((c) => c.status !== "ok");
  const q = result.data_quality;
  const ind = indicators.status === "success" ? indicators.data.indicators : null;
  const fact = (v: number | null | undefined, unit: string) => (v === null || v === undefined ? "n/d" : `${String(v).replace(".", ",")}${unit}`);
  const maxRain = weather.status === "success"
    ? Math.max(0, ...weather.data.daily.map((r) => r.precipitation_mm ?? 0))
    : 0;

  return (
    <section className="result" data-testid="result" aria-labelledby="t-result">
      <div className={`verdict-band tone-${level.tone}`} data-testid="block-meteo">
        <div className="band-inner">
          <p className="verdict-for">
            {result.crop.label} · {request.location.label || "lieu choisi"} · du {frDate(w.start_date)} au {frDate(w.end_date)}
          </p>
          <h1 id="t-result" data-testid="level">{level.title}</h1>
          <div className="band-row">
            <div className="band-text">
              {concerns.length === 0 && fav.criteria.length > 0 ? (
                <p>Tous les repères de la période sont respectés.</p>
              ) : (
                <ul className="reasons">
                  {concerns.map((c) => (
                    <li key={c.id}>
                      <span className="icon" aria-hidden="true">{STATUS[c.status]?.icon}</span>
                      <span><strong>{STATUS[c.status]?.word ?? c.status}.</strong> {c.explanation}</span>
                    </li>
                  ))}
                </ul>
              )}
              {fav.criteria.length === 0 && <p>{fav.summary}</p>}
              {result.crop.rule_status === "a_valider" && (
                <p className="small-note">Les repères de cette culture sont encore à valider : la réponse reste prudente.</p>
              )}
            </div>
            <p className="confidence" data-testid="confidence">
              <strong>Fiabilité de la réponse : {CONFIDENCE[result.confidence.level] ?? result.confidence.level}.</strong>{" "}
              {result.confidence.basis}
            </p>
          </div>
        </div>
      </div>

      <div className="wrap result-body">
        <section className="block" aria-labelledby="t-periode">
          <h2 id="t-periode">Ce qui s'est passé sur la période</h2>
          {ind && (
            <dl className="figures" data-testid="key-facts">
              <div><dt>Pluie tombée</dt><dd>{fact(ind.rain_sum_mm[`${w.days}d`], " mm")}</dd></div>
              <div><dt>Jours de pluie</dt><dd>{fact(ind.wet_days, "")}</dd></div>
              <div><dt>Plus longue période sans pluie</dt><dd>{fact(ind.max_dry_spell_days, " jours")}</dd></div>
              <div className="warm"><dt>Jour le plus chaud</dt><dd>{fact(ind.tmax_max_c, " °C")}</dd></div>
            </dl>
          )}
          {weather.status === "success" && weather.data.daily.length > 0 ? (
            <div className="curtain-panel">
              <RainCurtain
                values={weather.data.daily.map((r) => r.precipitation_mm ?? null)}
                height={210}
                title={`Pluie de chaque jour du ${frDate(w.start_date)} au ${frDate(w.end_date)}`}
              />
              <p className="curtain-axis"><span>{frDate(w.start_date)}</span><span>jour le plus pluvieux : {String(maxRain).replace(".", ",")} mm</span><span>{frDate(w.end_date)}</span></p>
            </div>
          ) : weather.status === "loading" ? (
            <p role="status" className="muted">Chargement de la pluie…</p>
          ) : null}
          <p className="muted">Chaque trait descend du ciel et mesure la pluie d'un jour, en millimètres. Un trait pâle et court : pas de pluie ce jour-là.</p>
        </section>

        <section className="block" aria-labelledby="t-reperes">
          <h2 id="t-reperes">Pourquoi cette réponse ? Les repères, un par un</h2>
          <p className="intro">La barre va du bon (vert) au défavorable (rouge). Le triangle montre la valeur mesurée pour votre lieu ; les traits noirs sont les limites.</p>
          <ul className="criteria">{fav.criteria.map((c) => <CriterionCard key={c.id} c={c} />)}</ul>
        </section>

        <section className="notions">
          <div className="card" data-testid="block-soil">
            <h3>Humidité du sol</h3>
            <p><strong>{result.soil_moisture.available ? "Estimée par un modèle." : "Non disponible."}</strong></p>
            <p className="muted">{result.soil_moisture.note}</p>
          </div>
          <div className="card" data-testid="block-cultivability">
            <h3>Le terrain convient-il&nbsp;?</h3>
            <p><strong>Non évalué.</strong></p>
            <p className="muted">{result.agronomic_cultivability.reason}</p>
          </div>
        </section>

        <section className="panel-dark know" data-testid="limits">
          <h2 className="h-md">À savoir</h2>
          <ul>{result.limits.map((l) => <li key={l}>{l}</li>)}</ul>
        </section>

        <details className="more" data-testid="block-quality">
          <summary>Qualité des données</summary>
          <p>{q.missing_days} jour(s) avec une donnée manquante ou rejetée.</p>
          <ul>
            {Object.entries(q.completeness_pct).map(([v, pct]) => (
              <li key={v}>{VARIABLES[v] ?? v} : {pct} % de données disponibles</li>
            ))}
          </ul>
        </details>

        <details className="more">
          <summary>Courbes et indicateurs détaillés</summary>
          <Curves weather={weather} indicators={indicators} onRetryWeather={retryWeather} onRetryIndicators={retryIndicators} />
        </details>

        <p className="muted" data-testid="attribution">
          {result.attribution ?? `Source : ${result.source.id}`}
          {result.source.license ? ` · Licence ${result.source.license}` : ""}
          {result.source.retrieved_at ? ` · Données récupérées le ${new Date(result.source.retrieved_at).toLocaleDateString("fr-FR")}` : ""}
          {result.source.spatial_resolution_note ? ` — ${result.source.spatial_resolution_note}` : ""}
        </p>
      </div>
    </section>
  );
}
