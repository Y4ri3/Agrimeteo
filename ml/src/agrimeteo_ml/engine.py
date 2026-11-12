"""Moteur de règles (cahier §7.4). Fonction pure : mêmes entrées, mêmes sorties (P-01).

Niveau global :
- indéterminé : données insuffisantes ou trop peu de critères évaluables ;
- peu favorable : au moins un critère bloquant défavorable ;
- favorable sous réserve : le reste (vigilance, non évaluable ou profil à valider) ;
- favorable : tout ok, rien de non évaluable, profil validé par une source.
Un profil « à valider » ne dépasse jamais « favorable sous réserve » (P-07). Un seuil est « franchi » dès
qu'il est atteint : valeur >= seuil pour un maximum, valeur <= seuil pour un minimum (tests aux bornes, P-02).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from agrimeteo_ml.indicators import indicator_value
from agrimeteo_ml.profiles import Criterion, Profile

ESSENTIAL = ("precipitation_mm", "tmin_c", "tmax_c")  # variables sans lesquelles rien n'est évaluable (§7.1)

BASE_LIMITS = (
    "Résolution de l'ordre de la maille du jeu de données, pas de la parcelle.",
    "Le résultat ne dit pas que le terrain est cultivable : sol, relief et pratiques ne sont pas évalués.",
)


@dataclass(frozen=True)
class CriterionResult:
    id: str
    label: str
    status: str  # ok | vigilance | defavorable | non_evaluable
    explanation: str
    blocking: bool
    direction: str
    unit: str
    window_days: int
    value: float | None
    vigilance: float | None
    unfavorable: float | None


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


def _crossed(c: Criterion, value: float, threshold: float) -> bool:
    return value <= threshold if c.direction == "lower_is_worse" else value >= threshold


def _status(c: Criterion, value: float | None) -> str:
    if value is None or (c.vigilance is None and c.unfavorable is None):
        return "non_evaluable"
    if c.unfavorable is not None and _crossed(c, value, c.unfavorable):
        return "defavorable"
    if c.vigilance is not None and _crossed(c, value, c.vigilance):
        return "vigilance"
    return "ok"


def _explain(c: Criterion, value: float | None, status: str, available_days: int) -> str:
    unit = f" {c.unit}" if c.unit else ""
    head = f"{c.label} sur {c.window_days} jours"
    if status == "non_evaluable":
        if c.vigilance is None and c.unfavorable is None:
            return f"{head} : seuil non défini pour ce profil (à valider)."
        if available_days < c.window_days:
            return f"{head} : non évaluable, la période analysée ({available_days} jours) est trop courte."
        return f"{head} : non évaluable, donnée manquante."
    shown = f"{head} : {_fmt(value)}{unit}"
    word = "est égal ou inférieur" if c.direction == "lower_is_worse" else "atteint ou dépasse"
    to = "au" if c.direction == "lower_is_worse" else "le"
    if status == "defavorable":
        return f"{shown}, ce qui {word} {to} seuil défavorable ({_fmt(c.unfavorable)}{unit})."
    if status == "vigilance":
        return f"{shown}, ce qui {word} {to} seuil de vigilance ({_fmt(c.vigilance)}{unit})."
    return f"{shown}, dans la limite acceptable pour ce profil."


def _confidence(
    level: str, profile: Profile, completeness: dict[str, float], fine: bool, enough: bool
) -> str:
    if level == "indetermine" or not enough:
        return "faible"
    points = sum(
        [all(completeness.get(v, 0) >= 95 for v in ESSENTIAL), profile.status == "valide_par_source", fine]
    )
    return ("faible", "moyenne", "moyenne", "elevee")[points]


def evaluate(
    profile: Profile,
    days: Sequence[Any],
    completeness_pct: dict[str, float],
    *,
    min_completeness: float = 90,
    min_criteria: int = 2,
    fine_resolution: bool = False,
) -> Evaluation:
    """Évalue un profil sur la série de jours de la période analysée (les plus récents en dernier)."""
    limits = list(BASE_LIMITS) + list(profile.limits)
    if profile.status == "a_valider":
        limits.append(
            f"Seuils du profil « {profile.label} » à valider : au mieux « favorable sous réserve »."
        )

    results = []
    for c in profile.criteria:
        value = indicator_value(days, c.indicator, c.window_days)
        status = _status(c, value)
        results.append(
            CriterionResult(
                id=c.id,
                label=c.label,
                status=status,
                explanation=_explain(c, value, status, len(days)),
                blocking=c.blocking,
                direction=c.direction,
                unit=c.unit,
                window_days=c.window_days,
                value=value,
                vigilance=c.vigilance,
                unfavorable=c.unfavorable,
            )
        )

    insufficient = [
        f"{v} : {completeness_pct.get(v, 0)} % de données (minimum {_fmt(min_completeness)} %)"
        for v in ESSENTIAL
        if completeness_pct.get(v, 0) < min_completeness
    ]
    status_of = {r.id: r.status for r in results}
    evaluable = sum(1 for s in status_of.values() if s != "non_evaluable")
    needed = min(min_criteria, len(results))
    blocking_bad = [r for r in results if r.blocking and r.status == "defavorable"]

    if insufficient:
        level = "indetermine"
        summary = "Résultat indéterminé : données insuffisantes (" + " ; ".join(insufficient) + ")."
    elif evaluable < max(1, needed):
        level, summary = (
            "indetermine",
            f"Résultat indéterminé : {evaluable} critère(s) évaluable(s), {needed} au minimum.",
        )
    elif blocking_bad:
        level = "peu_favorable"
        summary = "Peu favorable : " + " ; ".join(r.explanation for r in blocking_bad)
    elif all(s == "ok" for s in status_of.values()) and profile.status == "valide_par_source":
        level, summary = "favorable", f"Conditions favorables selon le profil « {profile.label} »."
    else:
        level = "favorable_sous_reserve"
        reasons = [r.explanation for r in results if r.status != "ok"]
        summary = "Conditions compatibles avec le profil, sous réserve : " + (
            " ; ".join(reasons) or "seuils du profil à valider"
        )

    enough = evaluable >= len(results) / 2
    basis = "Complétude des données, résolution spatiale, statut du profil. Ce n'est pas une probabilité."
    confidence = _confidence(level, profile, completeness_pct, fine_resolution, enough)
    return Evaluation(level, summary, tuple(results), confidence, basis, tuple(limits))
