import { useCallback, useEffect, useState } from "react";

export type AsyncState<T> =
  | { status: "loading" }
  | { status: "error"; error: unknown }
  | { status: "success"; data: T };

/** Exécute `load` à chaque changement de `key` ; `retry` relance après une erreur. */
export function useAsync<T>(load: () => Promise<T>, key: string): [AsyncState<T>, () => void] {
  const [state, setState] = useState<AsyncState<T>>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let cancelled = false;
    setState({ status: "loading" });
    load().then(
      (data) => !cancelled && setState({ status: "success", data }),
      (error) => !cancelled && setState({ status: "error", error }),
    );
    return () => {
      cancelled = true;
    };
  }, [key, attempt]);
  return [state, useCallback(() => setAttempt((n) => n + 1), [])];
}
