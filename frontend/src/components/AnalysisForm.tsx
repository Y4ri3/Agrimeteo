import { useState, type FormEvent } from "react";
import { geocode, getCrops, type GeocodeResult, type PredictionRequest } from "../api";
import { userMessage } from "../errors";
import { useAsync } from "../useAsync";
import { Async } from "./Async";

// Zone de démonstration par défaut (cahier, 13.1) : l'API couvre le monde entier.
const DEFAULT_PLACE = { label: "Dakar, Sénégal", latitude: "14.6937", longitude: "-17.4441" };

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
  const [places, setPlaces] = useState<GeocodeResult[] | null>(null);
  const [placeError, setPlaceError] = useState<unknown>(null);
  const [searching, setSearching] = useState(false);
  const [place, setPlace] = useState(DEFAULT_PLACE);
  const [referenceDate, setReferenceDate] = useState("");
  const [windowDays, setWindowDays] = useState(30);

  const latitude = Number(place.latitude);
  const longitude = Number(place.longitude);
  const coordsValid =
    place.latitude !== "" && place.longitude !== "" && Math.abs(latitude) <= 90 && Math.abs(longitude) <= 180;
  const selectedCrop = cropId || (crops.status === "success" ? (crops.data.crops[0]?.id ?? "") : "");
  const windowValid = Number.isInteger(windowDays) && windowDays >= 7 && windowDays <= 90;

  async function search(e: FormEvent) {
    e.preventDefault();
    if (query.trim().length < 2) return;
    setSearching(true);
    setPlaceError(null);
    try {
      setPlaces((await geocode(query.trim())).results);
    } catch (err) {
      setPlaces(null);
      setPlaceError(err);
    } finally {
      setSearching(false);
    }
  }

  function choose(p: GeocodeResult) {
    setPlace({
      label: [p.name, p.admin1, p.country].filter(Boolean).join(", "),
      latitude: String(p.latitude),
      longitude: String(p.longitude),
    });
    setPlaces(null);
  }

  function submit(e: FormEvent) {
    e.preventDefault();
    onSubmit({
      crop_id: selectedCrop,
      location: { latitude, longitude, label: place.label },
      reference_date: referenceDate || undefined,
      window_days: windowDays,
    });
  }

  return (
    <section aria-labelledby="t-analyse">
      <h2 id="t-analyse">Analyser une parcelle</h2>
      <Async state={crops} onRetry={retryCrops} isEmpty={(d) => d.crops.length === 0} emptyText="Aucune culture disponible." errorTestId="crops-error">
        {(data) => (
          <label>
            Culture
            <select data-testid="crop-select" value={selectedCrop} onChange={(e) => setCropId(e.target.value)}>
              {data.crops.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                  {c.rule_status === "a_valider" ? " — seuils à valider" : ""}
                </option>
              ))}
            </select>
          </label>
        )}
      </Async>

      <form onSubmit={search} className="row" role="search">
        <label className="grow">
          Rechercher un lieu
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ex. Thiès" minLength={2} maxLength={100} />
        </label>
        <button type="submit" disabled={searching || query.trim().length < 2}>
          {searching ? "Recherche…" : "Rechercher"}
        </button>
      </form>
      {placeError ? (
        <p role="alert" className="alert">{userMessage(placeError)}</p>
      ) : null}
      {places && places.length === 0 && <p className="muted">Aucun lieu trouvé : saisissez les coordonnées ci-dessous.</p>}
      {places && places.length > 0 && (
        <ul className="choices" aria-label="Lieux proposés">
          {places.map((p) => (
            <li key={`${p.latitude},${p.longitude}`}>
              <button type="button" onClick={() => choose(p)}>
                {[p.name, p.admin1, p.country].filter(Boolean).join(", ")}
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={submit}>
        <p className="muted" data-testid="selected-place">Zone : {place.label || "coordonnées saisies"}</p>
        <div className="row">
          <label>
            Latitude
            <input type="number" step="any" min={-90} max={90} value={place.latitude}
              onChange={(e) => setPlace({ ...place, label: "", latitude: e.target.value })} />
          </label>
          <label>
            Longitude
            <input type="number" step="any" min={-180} max={180} value={place.longitude}
              onChange={(e) => setPlace({ ...place, label: "", longitude: e.target.value })} />
          </label>
        </div>
        <div className="row">
          <label>
            Date de référence
            <input type="date" value={referenceDate} onChange={(e) => setReferenceDate(e.target.value)} />
            <small className="muted">Vide : il y a deux jours (délai de publication des archives).</small>
          </label>
          <label>
            Durée d'analyse (jours)
            <input type="number" min={7} max={90} value={windowDays}
              onChange={(e) => setWindowDays(Number(e.target.value))} />
          </label>
        </div>
        {!coordsValid && <p className="muted">Coordonnées invalides (latitude −90 à 90, longitude −180 à 180).</p>}
        {!windowValid && <p className="muted">La durée doit être comprise entre 7 et 90 jours.</p>}
        <button data-testid="analyse-btn" type="submit" className="primary" disabled={!selectedCrop || !coordsValid || !windowValid || busy}>
          {busy ? "Analyse en cours…" : "Analyser"}
        </button>
        {busy && <p role="status" className="muted">Chargement…</p>}
        {error ? (
          <p role="alert" className="alert" data-testid="error-message">{userMessage(error)}</p>
        ) : null}
      </form>
    </section>
  );
}
