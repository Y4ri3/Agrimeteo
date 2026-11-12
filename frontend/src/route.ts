import { useEffect, useState } from "react";

export type Route = "accueil" | "analyse";
const read = (): Route => (window.location.hash.startsWith("#/analyse") ? "analyse" : "accueil");

/** Navigation minimale par l'adresse (#/ et #/analyse) : pas de bibliothèque de routage pour deux pages. */
export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(read);
  useEffect(() => {
    const onChange = () => {
      setRoute(read());
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return route;
}
