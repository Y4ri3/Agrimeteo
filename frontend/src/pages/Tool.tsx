import { useState } from "react";
import { postPrediction, type Prediction, type PredictionRequest } from "../api";
import { AnalysisForm } from "../components/AnalysisForm";
import { BarHeader } from "../components/Header";
import { Result } from "../components/Result";

type Done = { request: PredictionRequest; result: Prediction };

/** Deux écrans : Analyse (le formulaire) puis Résultat. Le formulaire reste monté pour garder les choix. */
export function Tool() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [done, setDone] = useState<Done | null>(null);
  const [showResult, setShowResult] = useState(false);

  async function analyse(request: PredictionRequest) {
    setBusy(true);
    setError(null);
    try {
      setDone({ request, result: await postPrediction(request) });
      setShowResult(true);
      window.scrollTo?.(0, 0);
    } catch (e) {
      setError(e); // on reste sur l'écran Analyse : le formulaire reste utilisable
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <BarHeader>
        {showResult ? (
          <button type="button" className="pill-cta" onClick={() => setShowResult(false)}>Nouvelle vérification</button>
        ) : (
          <a className="bar-link" href="#/">À propos</a>
        )}
      </BarHeader>
      <div hidden={showResult}>
        <AnalysisForm busy={busy} error={error} onSubmit={analyse} />
      </div>
      {showResult && done && <Result request={done.request} result={done.result} />}
    </>
  );
}
