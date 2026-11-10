import { getIndicators, getWeather, type Prediction, type PredictionRequest } from "../api";
import { useAsync } from "../useAsync";
import { Curves } from "./Curves";
import { RainStrip } from "./RainStrip";

// Quatre niveaux du contrat, dits en français simple.
const LEVELS: Record<string, { title: string; tone: string }> = {
  favorable: { title: "Oui, les conditions sont bonnes", tone: "oui" },
  favorable_sous_reserve: { title: "Oui, sous réserve", tone: "reserve" },
  peu_favorable: { title: "Non, pas maintenant", tone: "non" },
  indetermine: { title: "On ne peut pas conclure", tone: "inconnu" },
};
const STATUS: Record<string, { word: string; icon: string }> = {
  ok: { word: "Respecté", icon: "✓" },
  vigilance: { word: "À surveiller", icon: "!" },
  defavorable: { word: "Défavorable", icon: "✕" },
  non_evaluable: { word: "Non évaluable", icon: "?" },
};
const CONFIDENCE: Record<string, string> = { faible: "faible", moyenne: "moyenne", elevee: "élevée" };
const VARIABLES: Record<string, string> = {
  precipitation_mm: "Précipitations",
  tmax_c: "Température maximale",
  tmin_c: "Température minimale",
  rh_mean_pct: "Humidité de l'air",
  et0_mm: "Évapotranspiration (ET0)",
};

const frDate = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });

/** Affiche le résultat tel que renvoyé par l'API : aucun calcul côté frontend (A-08, I-05). */
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

  return (
    <section className="result" data-testid="result" aria-labelledby="t-result">
      <div className={`verdict tone-${level.tone}`} data-testid="block-meteo">
        <p className="verdict-for">
          {result.crop.label} · {request.location.label || "lieu choisi"} · du {frDate(w.start_date)} au {frDate(w.end_date)}
        </p>
        <h2 id="t-result" data-testid="level">{level.title}</h2>
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

      <div className="strip-box">
        {weather.status === "success" && weather.data.daily.length > 0 ? (
          <>
            <RainStrip
              values={weather.data.daily.map((r) => r.precipitation_mm ?? null)}
              startLabel={frDate(w.start_date)}
              endLabel={frDate(w.end_date)}
              title={`Pluie de chaque jour du ${frDate(w.start_date)} au ${frDate(w.end_date)}`}
            />
            <p className="caption">Pluie de chaque jour sur la période. Un jour hachuré n'a pas de donnée.</p>
          </>
        ) : weather.status === "loading" ? (
          <p role="status" className="muted">Chargement de la pluie…</p>
        ) : null}
      </div>

      <p className="confidence" data-testid="confidence">
        Fiabilité de la réponse : <strong>{CONFIDENCE[result.confidence.level] ?? result.confidence.level}</strong>. {result.confidence.basis}
      </p>

      <div className="notions">
        <div data-testid="block-soil">
          <h3>Humidité du sol</h3>
          <p>{result.soil_moisture.available ? "Estimée par un modèle." : "Non disponible."}</p>
          <p className="muted">{result.soil_moisture.note}</p>
        </div>
        <div data-testid="block-cultivability">
          <h3>Le terrain convient-il&nbsp;?</h3>
          <p>Non évalué.</p>
          <p className="muted">{result.agronomic_cultivability.reason}</p>
        </div>
      </div>

      <div className="aknow" data-testid="limits">
        <h3>À savoir</h3>
        <ul>{result.limits.map((l) => <li key={l}>{l}</li>)}</ul>
      </div>

      <details className="more">
        <summary>Détail de chaque repère</summary>
        <ul className="criteria">
          {fav.criteria.map((c) => (
            <li key={c.id}>
              <span className={`tag s-${c.status}`}><span aria-hidden="true">{STATUS[c.status]?.icon}</span> {STATUS[c.status]?.word ?? c.status}</span> {c.explanation}
            </li>
          ))}
        </ul>
      </details>

      <details className="more" data-testid="block-quality">
        <summary>Qualité des données</summary>
        <p>{q.missing_days} jour(s) avec une donnée manquante ou rejetée.</p>
        <ul>
          {Object.entries(q.completeness_pct).map(([v, pct]) => (
            <li key={v}>{VARIABLES[v] ?? v} : {pct} % de complétude</li>
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
    </section>
  );
}
