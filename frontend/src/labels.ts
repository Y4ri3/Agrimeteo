// Textes affichés pour les valeurs du contrat, en français simple.
export const LEVELS: Record<string, { title: string; tone: string }> = {
  favorable: { title: "Oui, les conditions sont bonnes", tone: "oui" },
  favorable_sous_reserve: { title: "Oui, sous réserve", tone: "reserve" },
  peu_favorable: { title: "Non, pas maintenant", tone: "non" },
  indetermine: { title: "On ne peut pas conclure", tone: "inconnu" },
};
export const STATUS: Record<string, { word: string; icon: string }> = {
  ok: { word: "Bon", icon: "✓" },
  vigilance: { word: "À surveiller", icon: "!" },
  defavorable: { word: "Défavorable", icon: "✕" },
  non_evaluable: { word: "Non évaluable", icon: "?" },
};
// Courte : « 7 août ».
export const frDay = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("fr-FR", { day: "numeric", month: "long" });
export const frDate = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
