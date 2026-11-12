"""Indicateurs météo et agrométéo (cahier §7.3). Fonctions pures.

Un jour est tout objet ayant les attributs du schéma commun (date, precipitation_mm, tmin_c, tmax_c, tmean_c,
rh_mean_pct, et0_mm). Une valeur manquante (None) n'est JAMAIS remplacée par 0 : un jour inconnu ne compte
ni comme sec ni comme pluvieux, et il interrompt les séries. Noms des indicateurs : ceux du notebook du lot 2.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

DRY_DAY_MM = 1.0  # jour sec : moins de 1 mm de pluie (jour pluvieux : au moins 1 mm)
FROST_C = 0.0  # jour de gel : température minimale à 0 °C ou en dessous
RAIN_WINDOWS = (3, 7, 14, 30)


def _known(days: Sequence[Any], attr: str) -> list[float]:
    return [v for d in days if (v := getattr(d, attr, None)) is not None]


def _round(value: float | None, digits: int = 1) -> float | None:
    return None if value is None else round(value, digits)


def rain_sum(days: Sequence[Any], n: int | None = None) -> float | None:
    """Cumul des n derniers jours (tous par défaut) ; seuls les jours connus comptent (None si aucun)."""
    known = _known(days if n is None else days[-n:], "precipitation_mm")
    return _round(sum(known)) if known else None


def rain_max_3d(days: Sequence[Any]) -> float | None:
    """Plus forte pluie cumulée sur 3 jours consécutifs entièrement connus."""
    best = None
    for i in range(len(days) - 2):
        trio = [d.precipitation_mm for d in days[i : i + 3]]
        if None not in trio:
            best = sum(trio) if best is None else max(best, sum(trio))
    return _round(best)


def wet_days(days: Sequence[Any]) -> int | None:
    known = _known(days, "precipitation_mm")
    return sum(1 for v in known if v >= DRY_DAY_MM) if known else None


def max_dry_spell(days: Sequence[Any]) -> int | None:
    """Plus longue série de jours consécutifs connus sans pluie significative (< 1 mm)."""
    if not _known(days, "precipitation_mm"):
        return None
    best = run = 0
    for d in days:
        run = run + 1 if d.precipitation_mm is not None and d.precipitation_mm < DRY_DAY_MM else 0
        best = max(best, run)
    return best


def tmean(days: Sequence[Any]) -> float | None:
    """Moyenne des températures moyennes journalières (celle de la source ; à défaut (Tmin + Tmax) / 2)."""
    values = []
    for d in days:
        v = getattr(d, "tmean_c", None)
        if v is None and d.tmin_c is not None and d.tmax_c is not None:
            v = (d.tmin_c + d.tmax_c) / 2
        if v is not None:
            values.append(v)
    return _round(sum(values) / len(values)) if values else None


def tmin_min(days: Sequence[Any]) -> float | None:
    known = _known(days, "tmin_c")
    return min(known) if known else None


def tmax_max(days: Sequence[Any]) -> float | None:
    known = _known(days, "tmax_c")
    return max(known) if known else None


def frost_days(days: Sequence[Any]) -> int | None:
    known = _known(days, "tmin_c")
    return sum(1 for v in known if v <= FROST_C) if known else None


def diurnal_range(days: Sequence[Any]) -> float | None:
    both = [d.tmax_c - d.tmin_c for d in days if d.tmin_c is not None and d.tmax_c is not None]
    return _round(sum(both) / len(both)) if both else None


def et0_sum(days: Sequence[Any]) -> float | None:
    """ET0 cumulée, seulement si elle est complète : un trou ne vaut pas 0."""
    et0 = [d.et0_mm for d in days]
    return _round(sum(et0)) if days and None not in et0 else None


def water_balance(days: Sequence[Any]) -> float | None:
    rain, et0 = rain_sum(days), et0_sum(days)
    return _round(rain - et0) if rain is not None and et0 is not None else None


def rh_mean(days: Sequence[Any]) -> float | None:
    known = _known(days, "rh_mean_pct")
    return _round(sum(known) / len(known)) if known else None


# Nom d'indicateur (utilisé par les profils YAML) -> calcul sur une fenêtre de jours.
INDICATORS: dict[str, Callable[[Sequence[Any]], float | int | None]] = {
    "rain_sum": rain_sum,
    "rain_max_3d": rain_max_3d,
    "wet_days": wet_days,
    "max_dry_spell": max_dry_spell,
    "tmean": tmean,
    "tmin_min": tmin_min,
    "tmax_max": tmax_max,
    "frost_days": frost_days,
    "diurnal_range": diurnal_range,
    "et0_sum": et0_sum,
    "water_balance": water_balance,
    "rh_mean": rh_mean,
}


def indicator_value(days: Sequence[Any], name: str, window_days: int) -> float | int | None:
    """Valeur d'un indicateur sur les `window_days` derniers jours ; None si la fenêtre est trop courte."""
    if name not in INDICATORS:
        raise ValueError(f"indicateur inconnu : {name}")
    window = list(days)[-window_days:]
    return INDICATORS[name](window) if len(window) >= window_days else None


def compute(days: Sequence[Any], window_days: int) -> dict[str, Any]:
    """Tous les indicateurs de la fenêtre (les `window_days` derniers jours), sous les noms de l'API."""
    window = list(days)[-window_days:]
    sums = {f"{n}d": rain_sum(window, n) for n in RAIN_WINDOWS if n < window_days}
    sums[f"{window_days}d"] = rain_sum(window, window_days)
    return {
        "rain_sum_mm": sums,
        "rain_max_3d_mm": rain_max_3d(window),
        "wet_days": wet_days(window),
        "max_dry_spell_days": max_dry_spell(window),
        "tmean_c": tmean(window),
        "tmin_min_c": tmin_min(window),
        "tmax_max_c": tmax_max(window),
        "frost_days": frost_days(window),
        "diurnal_range_c": diurnal_range(window),
        "et0_sum_mm": et0_sum(window),
        "water_balance_mm": water_balance(window),
        "rh_mean_pct": rh_mean(window),
    }
