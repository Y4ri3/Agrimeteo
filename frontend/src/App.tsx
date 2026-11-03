import { useEffect, useState } from "react";
import { ApiError, Crop, Prediction, getCrops, postPrediction } from "./api";

// SQUELETTE (lot 4) : une seule page qui prouve la chaîne front → nginx → API.
export default function App() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cropId, setCropId] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCrops()
      .then((d) => { setCrops(d.crops); setCropId(d.crops[0]?.id ?? ""); })
      .catch((e: ApiError) => setError(e.message));
  }, []);

  async function analyse() {
    setError(null);
    setResult(null);
    try { setResult(await postPrediction(cropId, 14.7, -17.4)); }
    catch (e) { setError((e as Error).message); }
  }

  return (
    <main>
      <h1>AgriMétéo</h1>
      <label>Culture{" "}
        <select data-testid="crop-select" value={cropId} onChange={(e) => setCropId(e.target.value)}>
          {crops.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}
        </select>
      </label>
      <button data-testid="analyse-btn" onClick={analyse} disabled={!cropId}>Analyser</button>
      {error && <p role="alert" data-testid="error-message">{error}</p>}
      {result && (
        <section data-testid="result">
          <div data-testid="block-meteo"><h2>Favorabilité météo</h2><p>{result.meteorological_favorability.summary}</p></div>
          <div data-testid="block-soil"><h2>Humidité du sol</h2><p>{result.soil_moisture.available ? "Estimée" : "Non disponible"}</p></div>
          <div data-testid="block-cultivability"><h2>Cultivabilité</h2><p>{result.agronomic_cultivability.reason}</p></div>
          <p data-testid="confidence">{result.confidence.basis}</p>
        </section>
      )}
    </main>
  );
}
