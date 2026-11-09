import { useState } from "react";
import { postPrediction, type Prediction, type PredictionRequest } from "./api";
import { AnalysisForm } from "./components/AnalysisForm";
import { Dashboard } from "./components/Dashboard";
import { ResultView } from "./components/ResultView";

type Tab = "analyse" | "resultat" | "dashboard";
const TABS: [Tab, string][] = [
  ["analyse", "Analyse"],
  ["resultat", "Résultat"],
  ["dashboard", "Tableau de bord"],
];

export default function App() {
  const [tab, setTab] = useState<Tab>("analyse");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [done, setDone] = useState<{ request: PredictionRequest; result: Prediction } | null>(null);

  async function analyse(request: PredictionRequest) {
    setBusy(true);
    setError(null);
    try {
      setDone({ request, result: await postPrediction(request) });
      setTab("resultat");
    } catch (e) {
      setError(e); // on reste sur l'écran Analyse : le formulaire reste utilisable
    } finally {
      setBusy(false);
    }
  }

  const needAnalysis = <p className="muted">Lancez d'abord une analyse depuis l'écran Analyse.</p>;

  return (
    <main>
      <h1>AgriMétéo</h1>
      <p className="muted">
        Estimation de la favorabilité météo à la mise en culture. Ce n'est pas une garantie agronomique.
      </p>
      <nav aria-label="Écrans">
        {TABS.map(([id, label]) => (
          <button key={id} type="button" aria-current={tab === id ? "page" : undefined} onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </nav>
      {tab === "analyse" && <AnalysisForm busy={busy} error={error} onSubmit={analyse} />}
      {tab === "resultat" && (done ? <ResultView result={done.result} /> : needAnalysis)}
      {tab === "dashboard" && (done ? <Dashboard request={done.request} result={done.result} /> : needAnalysis)}
    </main>
  );
}
