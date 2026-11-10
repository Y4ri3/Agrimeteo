import type { Route } from "../route";

export function Header({ route }: { route: Route }) {
  return (
    <header className="site-header">
      <a className="brand" href="#/" aria-label="AgriMétéo, page d'accueil">
        <svg viewBox="0 0 24 24" width="26" height="26" aria-hidden="true">
          <path d="M12 2c3.5 4.2 6 7.3 6 10.5a6 6 0 0 1-12 0C6 9.3 8.5 6.2 12 2Z" fill="currentColor" />
        </svg>
        AgriMétéo
      </a>
      {route === "accueil" ? (
        <a className="button small" href="#/analyse">
          Vérifier pour mon champ
        </a>
      ) : (
        <a className="link" href="#/">
          À propos
        </a>
      )}
    </header>
  );
}
