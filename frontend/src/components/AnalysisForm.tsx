import { useState, type FormEvent } from "react";
import { geocode, getCrops, type GeocodeResult, type PredictionRequest } from "../api";
import { userMessage } from "../errors";
import { useAsync } from "../useAsync";
import { Async } from "./Async";

// Zone de démonstration par défaut (cahier, 13.1) ; l'API couvre le monde entier.
const DEFAULT_PLACE = { label: "Dakar, Sénégal", latitude: 14.6937, longitude: -17.4441 };
const QUICK_PLACES = ["Dakar", "Thiès", "Kaolack", "Saint-Louis", "Ziguinchor"];
// Date d'exemple pour la démonstration : milieu de la saison des pluies 2025.
const RAINY_SEASON_EXAMPLE = "2025-08-20";

// Sans doublon : « Kaolack, Kaolack, Sénégal » devient « Kaolack, Sénégal ».
const placeLabel = (p: GeocodeResult) => [...new Set([p.name, p.admin1, p.country].filter(Boolean))].join(", ");

/** Petits pictogrammes des cultures (décoratifs). */
function CropIcon({ id }: { id: string }) {
  switch (id) {
    case "arachide":
      return <svg viewBox="0 0 40 40" aria-hidden="true"><ellipse cx="14" cy="22" rx="9" ry="12" fill="#C98A3C" /><ellipse cx="27" cy="19" rx="9" ry="12" fill="#E3A957" /></svg>;
    case "mil":
      return <svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 38V14" stroke="#7A8F3A" strokeWidth="3" /><ellipse cx="20" cy="11" rx="5" ry="10" fill="#C8A44A" /></svg>;
    case "riz":
      return <svg viewBox="0 0 40 40" aria-hidden="true"><path d="M12 38C12 24 14 14 20 4M22 38C22 26 24 16 30 8" stroke="#5E9C5A" strokeWidth="3" fill="none" /></svg>;
    case "tomate":
      return <svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="23" r="13" fill="#C8452F" /><path d="M14 11l6 4 6-4" stroke="#3E7A3C" strokeWidth="3" fill="none" /></svg>;
    default:
      return null;
  }
}

export function AnalysisForm({
  busy,
  error,
  onSubmit,
}: {
  busy: boolean;
  error: unknown;
  onSubmit: (request: PredictionRequest) => void;
}) {
  const [crops, retryCrops] = useAsync(getCrops, "crops");
  const [cropId, setCropId] = useState("");
  const [query, setQuery] = useState("");
  const [candidates, setCandidates] = useState<GeocodeResult[] | null>(null);
  const [searchError, setSearchError] = useState<unknown>(null);
  const [searching, setSearching] = useState(false);
  const [place, setPlace] = useState(DEFAULT_PLACE);
  const [referenceDate, setReferenceDate] = useState("");
  const [windowDays, setWindowDays] = useState(30);

  const selectedCrop = cropId || (crops.status === "success" ? (crops.data.crops[0]?.id ?? "") : "");
  const windowValid = Number.isInteger(windowDays) && windowDays >= 7 && windowDays <= 90;

  async function search(name: string, pickFirst = false) {
    if (name.trim().length < 2) return;
    setSearching(true);
    setSearchError(null);
    try {
      const results = (await geocode(name.trim())).results;
      if (pickFirst && results[0]) {
        choose(results[0]);
      } else {
        setCandidates(results);
      }
    } catch (err) {
      setCandidates(null);
      setSearchError(err);
    } finally {
      setSearching(false);
    }
  }

  function choose(p: GeocodeResult) {
    setPlace({ label: placeLabel(p), latitude: p.latitude, longitude: p.longitude });
    setCandidates(null);
    setQuery("");
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    onSubmit({
      crop_id: selectedCrop,
      location: { latitude: place.latitude, longitude: place.longitude, label: place.label },
      reference_date: referenceDate || undefined,
      window_days: windowDays,
    });
  }

  return (
    <div className="analyse">
      <form className="analyse-main" onSubmit={submit} aria-labelledby="t-analyse">
        <h1 id="t-analyse">Puis-je semer&nbsp;?</h1>
        <p className="lead-small">Trois choix, et vous avez la réponse.</p>

        <fieldset>
          <legend><span className="num">1.</span> Que voulez-vous semer&nbsp;?</legend>
          <Async state={crops} onRetry={retryCrops} isEmpty={(d) => d.crops.length === 0} emptyText="Aucune culture disponible." errorTestId="crops-error">
            {(data) => (
              <div className="tiles" role="radiogroup" aria-label="Culture" data-testid="crop-select">
                {data.crops.map((c) => (
                  <label key={c.id} className={`tile${selectedCrop === c.id ? " selected" : ""}`}>
                    <input type="radio" name="culture" value={c.id} checked={selectedCrop === c.id} onChange={() => setCropId(c.id)} />
                    <CropIcon id={c.id} />
                    <span className="tile-name">{c.label}{c.zones ? <small>{c.zones}</small> : null}</span>
                  </label>
                ))}
              </div>
            )}
          </Async>
        </fieldset>

        <fieldset>
          <legend><span className="num">2.</span> Où se trouve votre champ&nbsp;?</legend>
          <p className="chosen" data-testid="selected-place">Lieu choisi : <strong>{place.label}</strong></p>
          <div className="row">
            <label className="grow">
              <span className="label">Chercher un autre lieu</span>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    void search(query);
                  }
                }}
                placeholder="Nom d'une ville ou d'un village"
                maxLength={100}
              />
            </label>
            <button type="button" className="button deep" disabled={searching || query.trim().length < 2} onClick={() => void search(query)}>
              {searching ? "Recherche…" : "Rechercher"}
            </button>
          </div>
          <p className="chips" aria-label="Lieux fréquents">
            {QUICK_PLACES.map((n) => (
              <button key={n} type="button" className={`chip${place.label.startsWith(n) ? " on" : ""}`} disabled={searching} onClick={() => void search(n, true)}>
                {n}
              </button>
            ))}
          </p>
          {searchError ? <p role="alert" className="alert">{userMessage(searchError)}</p> : null}
          {candidates && candidates.length === 0 && <p className="muted">Aucun lieu trouvé. Essayez un autre nom ou l'orthographe d'une grande ville proche.</p>}
          {candidates && candidates.length > 0 && (
            <ul className="choices" aria-label="Lieux proposés">
              {candidates.map((p) => (
                <li key={`${p.latitude},${p.longitude}`}>
                  <button type="button" className="choice" onClick={() => choose(p)}>{placeLabel(p)}</button>
                </li>
              ))}
            </ul>
          )}
        </fieldset>

        <fieldset>
          <legend><span className="num">3.</span> Sur quelle période&nbsp;?</legend>
          <p className="chosen">
            {referenceDate ? `Les ${windowDays} jours jusqu'au ${new Date(`${referenceDate}T00:00:00`).toLocaleDateString("fr-FR")}` : `Les ${windowDays} derniers jours disponibles`}.
          </p>
          <details className="more">
            <summary>Changer la période</summary>
            <div className="row">
              <label>
                <span className="label">Dernier jour analysé</span>
                <input type="date" value={referenceDate} max={new Date().toISOString().slice(0, 10)} onChange={(e) => setReferenceDate(e.target.value)} />
              </label>
              <label>
                <span className="label">Nombre de jours (7 à 90)</span>
                <input type="number" min={7} max={90} value={windowDays} onChange={(e) => setWindowDays(Number(e.target.value))} />
              </label>
            </div>
            <p className="muted">
              Vide, le dernier jour est celui d'il y a deux jours (délai de publication des archives).{" "}
              <button type="button" className="link-button" onClick={() => setReferenceDate(RAINY_SEASON_EXAMPLE)}>
                Essayer avec la saison des pluies 2025
              </button>
            </p>
          </details>
          {!windowValid && <p role="alert" className="alert">Le nombre de jours doit être compris entre 7 et 90.</p>}
        </fieldset>

        <button data-testid="analyse-btn" type="submit" className="button big" disabled={!selectedCrop || !windowValid || busy || searching}>
          {busy ? "Analyse en cours…" : searching ? "Recherche du lieu…" : "Vérifier"}
        </button>
        {busy && <p role="status" className="muted">Chargement des données météo…</p>}
        {error ? <p role="alert" className="alert" data-testid="error-message">{userMessage(error)}</p> : null}
      </form>

      <aside className="analyse-aside">
        <h2>Ce que vous allez obtenir</h2>
        <p><strong>Un verdict clair.</strong> Oui, oui sous réserve, non, ou on ne peut pas conclure.</p>
        <p><strong>Les raisons.</strong> Chaque repère placé sur une échelle verte, ocre, rouge.</p>
        <p><strong>La pluie jour par jour</strong> et les températures de la période.</p>
        <p className="aside-note">Une minute, sans compte. Les données viennent d'Open-Meteo.</p>
      </aside>
    </div>
  );
}
