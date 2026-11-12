import { useEffect, useRef, useState } from "react";
import { postPrediction, type Prediction, type PredictionRequest } from "../api";
import { AnalysisForm } from "../components/AnalysisForm";
import { Result } from "../components/Result";

export function Tool() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [done, setDone] = useState<{ request: PredictionRequest; result: Prediction } | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (done) resultRef.current?.scrollIntoView?.({ behavior: "smooth", block: "start" });
  }, [done]);

  async function analyse(request: PredictionRequest) {
    setBusy(true);
    setError(null);
    try {
      setDone({ request, result: await postPrediction(request) });
    } catch (e) {
      setError(e); // le formulaire reste utilisable
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="wrap tool">
      <AnalysisForm busy={busy} error={error} onSubmit={analyse} />
      <div ref={resultRef}>{done && <Result request={done.request} result={done.result} />}</div>
    </div>
  );
}
