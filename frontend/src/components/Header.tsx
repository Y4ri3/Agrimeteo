import type { ReactNode } from "react";

export function Brand() {
  return (
    <a className="brand" href="#/" aria-label="AgriMétéo, page d'accueil">
      <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">
        <path d="M12 2c3.5 4.2 6 7.3 6 10.5a6 6 0 0 1-12 0C6 9.3 8.5 6.2 12 2Z" fill="currentColor" />
      </svg>
      <span>AgriMétéo</span>
    </a>
  );
}

/** Barre bleue des écrans Analyse et Résultat. */
export function BarHeader({ children }: { children?: ReactNode }) {
  return (
    <header className="bar-header">
      <Brand />
      {children}
    </header>
  );
}
