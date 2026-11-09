"""Moteur de décision PROVISOIRE (lot 2 : à remplacer par le moteur de règles du module `ml`).

Aucun seuil agronomique n'existe encore (profils « à valider ») : aucun critère n'est évaluable, donc le
niveau n'est jamais autre chose que « indéterminé » (P-03, P-07). Rien n'est inventé.
"""

from __future__ import annotations

from app.schemas.indicators import Indicators
from app.schemas.predictions import Confidence, CriterionResult, Crop, MeteoFavorability
from app.schemas.weather import Quality, Source
from app.services import quality as quality_service

BASE_LIMITS = [
    "Résolution de l'ordre de la maille du jeu de données, pas de la parcelle.",
    "Seuils du profil à valider.",
    "Le résultat ne dit pas que le terrain est cultivable.",
]


def evaluate(
    crop: Crop, indicators: Indicators, quality: Quality, source: Source
) -> tuple[MeteoFavorability, Confidence, list[str]]:
    missing = quality_service.insufficient(quality)
    limits = list(BASE_LIMITS)
    if source.id == "fixture":
        limits.insert(0, "Données factices de démonstration : aucune valeur réelle.")

    if missing:
        favorability = MeteoFavorability(
            level="indetermine",
            summary="Résultat indéterminé : données insuffisantes.",
            criteria=[
                CriterionResult(id=m.split(" : ")[0], status="non_evaluable", explanation=m) for m in missing
            ],
        )
    else:
        favorability = MeteoFavorability(
            level="indetermine",
            summary="Résultat indéterminé : les seuils de ce profil sont encore à valider.",
            criteria=[
                CriterionResult(
                    id="gel",
                    status="non_evaluable",
                    explanation=(f"{indicators.frost_days} jour(s) de gel ; seuil non défini (à valider)."),
                ),
                CriterionResult(
                    id="bilan_pluie_et0",
                    status="non_evaluable",
                    explanation="Seuil non défini pour ce profil (à valider).",
                ),
            ],
        )
    confidence = Confidence(
        level="faible",
        basis="Complétude des données, résolution spatiale, statut du profil. Ce n'est pas une probabilité.",
    )
    return favorability, confidence, limits
