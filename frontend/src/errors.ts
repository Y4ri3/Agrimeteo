import { ApiError } from "./api";

// Un message distinct par code d'erreur du contrat (FE-02). Textes du cahier des charges, §2.3.
const MESSAGES: Record<string, string> = {
  VALIDATION_ERROR: "Vérifiez les coordonnées et les dates saisies.",
  PERIOD_TOO_LONG: "La période demandée dépasse la durée maximale.",
  DATE_OUT_OF_RANGE: "Aucune donnée disponible pour cette date.",
  CROP_NOT_FOUND: "Cette culture n'existe pas.",
  PROVIDER_UNAVAILABLE: "Le service de données météo est indisponible.",
  PROVIDER_RATE_LIMITED: "Trop de demandes : réessayez dans un instant.",
  PROVIDER_TIMEOUT: "Le service de données ne répond pas.",
  NETWORK_ERROR: "Le serveur est injoignable. Vérifiez votre connexion.",
};

export function userMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const base = MESSAGES[error.code] ?? "Une erreur est survenue.";
    return error.code === "INTERNAL_ERROR" || !MESSAGES[error.code]
      ? `${base}${error.requestId ? ` (identifiant de requête : ${error.requestId})` : ""}`
      : base;
  }
  return "Une erreur est survenue.";
}
