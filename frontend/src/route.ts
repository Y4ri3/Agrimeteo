import { useEffect, useRef, useState } from "react";

export type Route = "accueil" | "analyse";
const read = (): Route => (window.location.hash.startsWith("#/analyse") ? "analyse" : "accueil");

/** Navigation minimale par l'adresse (#/ et #/analyse) : pas de bibliothèque de routage pour deux pages. */
export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(read);
  const current = useRef(route);
  useEffect(() => {
    const onChange = () => {
      const next = read();
      // Haut de page seulement quand on change d'écran : un lien d'ancrage (#exemple) ne doit pas être annulé.
      if (next !== current.current) window.scrollTo(0, 0);
      current.current = next;
      setRoute(next);
    };
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return route;
}
