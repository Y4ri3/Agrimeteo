"""Moteur de règles (cahier §7.4). Fonction pure : mêmes entrées, mêmes sorties (P-01).

Niveau global :
- indéterminé : données insuffisantes ou trop peu de critères évaluables ;
- peu favorable : au moins un critère bloquant défavorable ;
- favorable sous réserve : le reste (vigilance, non évaluable ou profil à valider) ;
- favorable : tout ok, rien de non évaluable, profil validé par une source.
Un profil « à valider » ne dépasse jamais « favorable sous réserve » (P-07).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from agrimeteo_ml.profiles import Criterion, Profile

ESSENTIAL = ("precipitation_mm", "tmin_c", "tmax_c")  # variables sans lesquelles rien n'est évaluable (§7.1)

BASE_LIMITS = (
    "Résolution de l'ordre de la maille du jeu de données, pas de la parcelle.",
    "Le résultat ne dit pas que le terrain est cultivable : sol, relief et pratiques ne sont pas évalués.",
)


@dataclass(frozen=True)
class CriterionResult:
    id: str
    status: str  # ok | vigilance | defavorable | non_evaluable
    explanation: str


@dataclass(frozen=True)
class Evaluation:
    level: str  # favorable | favorable_sous_reserve | peu_favorable | indetermine
    summary: str
    criteria: tuple[CriterionResult, ...]
    confidence_level: str  # faible | moyenne | elevee
    confidence_basis: str
    limits: tuple[str, ...]


def _fmt(value: float) -> str:
    return (str(int(value)) if float(value).is_integer() else f"{value:.1f}").replace(".", ",")


def _status(c: Criterion, value: float | None) -> str:
    if value is None or c.vigilance is None or c.unfavorable is None:
        return "non_evaluable"
    if c.direction == "lower_is_worse":  # trop bas : en dessous du seuil
        return "defavorable" if value < c.unfavorable else "vigilance" if value < c.vigilance else "ok"
    # trop haut : seuil atteint ou dépassé
    return "defavorable" if value >= c.unfavorable else "vigilance" if value >= c.vigilance else "ok"


def _explain(c: Criterion, value: float | None, status: str) -> str:
    unit = f" {c.unit}" if c.unit else ""
    if status == "non_evaluable":
        if c.vigilance is None:
            return f"{c.label} : seuil non défini pour ce profil (à valider)."
        return f"{c.label} : non évaluable, donnée insuffisante."
    shown = f"{c.label} : {_fmt(value)}{unit}"
    if status == "defavorable":
        return f"{shown}, seuil défavorable franchi ({_fmt(c.unfavorable)}{unit})."
    if status == "vigilance":
        return f"{shown}, seuil de vigilance franchi ({_fmt(c.vigilance)}{unit})."
    return f"{shown}, conforme (vigilance à {_fmt(c.vigilance)}{unit})."


def _confidence(level: str, profile: Profile, completeness: dict[str, float], fine: bool) -> tuple[str, str]:
    basis = "Complétude des données, résolution spatiale, statut du profil. Ce n'est pas une probabilité."
    if level == "indetermine":
        return "faible", basis
    points = sum(
        [
            all(completeness.get(v, 0) >= 95 for v in ESSENTIAL),
            profile.status == "valide_par_source",
            fine,
        ]
    )
    return ("faible", "moyenne", "moyenne", "elevee")[points], basis


def evaluate(
    profile: Profile,
    indicators: dict[str, Any],
    completeness_pct: dict[str, float],
    *,
    min_completeness: float = 80,
    fine_resolution: bool = False,
) -> Evaluation:
    limits = list(BASE_LIMITS) + list(profile.limits)
    if profile.status == "a_valider":
        limits.append(
            f"Seuils du profil « {profile.label} » à valider : au mieux « favorable sous réserve »."
        )

    insufficient = [
        f"{v} : {completeness_pct.get(v, 0)} % de données (minimum {_fmt(min_completeness)} %)"
        for v in ESSENTIAL
        if completeness_pct.get(v, 0) < min_completeness
    ]
    results = tuple(
        CriterionResult(c.id, s, _explain(c, indicators.get(c.indicator), s))
        for c in profile.criteria
        for s in (_status(c, indicators.get(c.indicator)),)
    )
    if insufficient:
        summary = "Résultat indéterminé : données insuffisantes (" + " ; ".join(insufficient) + ")."
        results = tuple(CriterionResult(r.id, "non_evaluable", r.explanation) for r in results)
        level = "indetermine"
    else:
        status = {r.id: r.status for r in results}
        evaluable = sum(1 for s in status.values() if s != "non_evaluable")
        blocking_bad = [c for c in profile.criteria if c.blocking and status[c.id] == "defavorable"]
        if evaluable < max(1, math.ceil(len(results) / 2)):
            level, summary = "indetermine", "Résultat indéterminé : trop peu de critères évaluables."
        elif blocking_bad:
            level = "peu_favorable"
            summary = "Peu favorable : " + " ; ".join(
                r.explanation for r in results if r.id in {c.id for c in blocking_bad}
            )
        elif all(s == "ok" for s in status.values()) and profile.status == "valide_par_source":
            level, summary = "favorable", f"Conditions favorables selon le profil « {profile.label} »."
        else:
            level = "favorable_sous_reserve"
            reasons = [r.explanation for r in results if r.status != "ok"]
            tail = " ; ".join(reasons) if reasons else "seuils du profil à valider"
            summary = "Conditions compatibles avec le profil, sous réserve : " + tail
    confidence_level, basis = _confidence(level, profile, completeness_pct, fine_resolution)
    return Evaluation(level, summary, results, confidence_level, basis, tuple(limits))
