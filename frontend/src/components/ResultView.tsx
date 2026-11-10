import type { Prediction } from "../api";

const LEVELS: Record<string, string> = {
  favorable: "Favorable",
  favorable_sous_reserve: "Favorable sous réserve",
  peu_favorable: "Peu favorable",
  indetermine: "Indéterminé",
};
const STATUS: Record<string, string> = {
  ok: "OK",
  vigilance: "Vigilance",
  defavorable: "Défavorable",
  non_evaluable: "Non évaluable",
};
const CONFIDENCE: Record<string, string> = { faible: "faible", moyenne: "moyenne", elevee: "élevée" };
const VARIABLES: Record<string, string> = {
  precipitation_mm: "Précipitations",
  tmax_c: "Température max.",
  tmin_c: "Température min.",
  rh_mean_pct: "Humidité de l'air",
  et0_mm: "ET0",
};

/** Affiche le résultat tel que renvoyé par l'API : aucun calcul côté frontend (A-08, I-05). */
export function ResultView({ result }: { result: Prediction }) {
  const fav = result.meteorological_favorability;
  const q = result.data_quality;
  return (
    <section data-testid="result" aria-labelledby="t-result">
      <h2 id="t-result">Résultat de l'analyse</h2>
      <p className="muted">
        {result.crop.label} · du {result.analysis_window.start_date} au {result.analysis_window.end_date} (
        {result.analysis_window.days} jours)
      </p>

      <div className="card" data-testid="block-meteo">
        <h3>Favorabilité météo</h3>
        <p>
          <span className={`badge level-${fav.level}`} data-testid="level">{LEVELS[fav.level] ?? fav.level}</span>
        </p>
        <p>{fav.summary}</p>
        <ul>
          {fav.criteria.map((c) => (
            <li key={c.id}>
              <strong>{c.id}</strong> <span className={`badge status-${c.status}`}>{STATUS[c.status] ?? c.status}</span>{" "}
              {c.explanation}
            </li>
          ))}
        </ul>
      </div>

      <div className="card" data-testid="block-soil">
        <h3>Humidité du sol (indicateur modélisé)</h3>
        <p>{result.soil_moisture.available ? "Estimée par un modèle" : "Non disponible"}</p>
        <p className="muted">{result.soil_moisture.note}</p>
      </div>

      <div className="card" data-testid="block-cultivability">
        <h3>Cultivabilité agronomique</h3>
        <p><span className="badge">Non évaluée</span></p>
        <p className="muted">{result.agronomic_cultivability.reason}</p>
      </div>

      <div className="card" data-testid="block-quality">
        <h3>Qualité des données</h3>
        <p>{q.missing_days} jour(s) avec une donnée manquante ou rejetée.</p>
        <ul>
          {Object.entries(q.completeness_pct).map(([v, pct]) => (
            <li key={v}>{VARIABLES[v] ?? v} : {pct} % de complétude</li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h3>Indice de confiance : {CONFIDENCE[result.confidence.level] ?? result.confidence.level}</h3>
        <p className="muted" data-testid="confidence">{result.confidence.basis}</p>
      </div>

      <div className="card" data-testid="limits">
        <h3>Limites</h3>
        <ul>{result.limits.map((l) => <li key={l}>{l}</li>)}</ul>
      </div>

      <p className="muted" data-testid="attribution">
        {result.attribution ?? `Source : ${result.source.id}`}
        {result.source.license ? ` · Licence ${result.source.license}` : ""}
        {result.source.retrieved_at ? ` · Données récupérées le ${new Date(result.source.retrieved_at).toLocaleDateString("fr-FR")}` : ""}
        {result.source.spatial_resolution_note ? ` — ${result.source.spatial_resolution_note}` : ""}
      </p>
    </section>
  );
}
