// Aucune URL d'API en dur (FE-05) : la cible se règle par VITE_API_BASE. Par défaut, le relais nginx (/api).
export const API_BASE: string = import.meta.env.VITE_API_BASE ?? "/api";
