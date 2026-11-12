import type { ReactNode } from "react";
import { userMessage } from "../errors";
import type { AsyncState } from "../useAsync";

/** États communs aux écrans de données : chargement, erreur (avec réessai), vide, succès (FE-04). */
export function Async<T>({
  state,
  onRetry,
  isEmpty,
  emptyText,
  errorTestId = "error-message",
  children,
}: {
  state: AsyncState<T>;
  onRetry: () => void;
  isEmpty?: (data: T) => boolean;
  emptyText?: string;
  errorTestId?: string;
  children: (data: T) => ReactNode;
}) {
  if (state.status === "loading")
    return (
      <p role="status" className="muted" data-testid="loading">
        Chargement…
      </p>
    );
  if (state.status === "error")
    return (
      <div role="alert" className="alert" data-testid={errorTestId}>
        <span>{userMessage(state.error)}</span>
        <button type="button" onClick={onRetry}>
          Réessayer
        </button>
      </div>
    );
  if (isEmpty?.(state.data)) return <p className="muted">{emptyText ?? "Aucune donnée."}</p>;
  return <>{children(state.data)}</>;
}
