"""Indicateurs météo et agrométéo (cahier §7.3). Fonctions pures : mêmes entrées, mêmes sorties.

Un jour est tout objet ayant les attributs du schéma commun (date, precipitation_mm, tmin_c, tmax_c,
rh_mean_pct, et0_mm). Une valeur manquante (None) n'est JAMAIS remplacée par 0 : un jour inconnu ne compte
ni comme sec ni comme pluvieux, et il interrompt les séries.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

DRY_DAY_MM = (
    1.0  # jour sec : moins de 1 mm de pluie (seuil de jour pluvieux des études sahéliennes, voir README)
)
FROST_C = 0.0  # jour de gel : température minimale à 0 °C ou en dessous
RAIN_WINDOWS = (3, 7, 14, 30)


def _known(days: Sequence[Any], attr: str) -> list[float]:
    return [v for d in days if (v := getattr(d, attr)) is not None]


def _round(value: float | None, digits: int = 1) -> float | None:
    return None if value is None else round(value, digits)


def rain_sum(days: Sequence[Any], n: int) -> float | None:
    """Cumul des n derniers jours ; seuls les jours connus comptent (None si aucun)."""
    known = _known(days[-n:], "precipitation_mm")
    return _round(sum(known)) if known else None


def rain_max_3d(days: Sequence[Any]) -> float | None:
    """Plus forte pluie cumulée sur 3 jours consécutifs entièrement connus (déclencheur de semis)."""
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


def _tmean(days: Sequence[Any]) -> float | None:
    both = [(d.tmin_c + d.tmax_c) / 2 for d in days if d.tmin_c is not None and d.tmax_c is not None]
    return _round(sum(both) / len(both)) if both else None


def _diurnal_range(days: Sequence[Any]) -> float | None:
    both = [d.tmax_c - d.tmin_c for d in days if d.tmin_c is not None and d.tmax_c is not None]
    return _round(sum(both) / len(both)) if both else None


def compute(days: Sequence[Any], window_days: int) -> dict[str, Any]:
    """Tous les indicateurs de la fenêtre (les `window_days` derniers jours de `days`)."""
    window = list(days)[-window_days:]
    sums = {f"{n}d": rain_sum(window, n) for n in RAIN_WINDOWS if n < window_days}
    sums[f"{window_days}d"] = rain_sum(window, window_days)
    et0 = [d.et0_mm for d in window]
    # ET0 n'est sommée que si elle est complète : un trou ne vaut pas 0.
    et0_sum = _round(sum(et0)) if window and None not in et0 else None
    window_rain = sums[f"{window_days}d"]
    tmins, tmaxs, rhs = _known(window, "tmin_c"), _known(window, "tmax_c"), _known(window, "rh_mean_pct")
    return {
        "rain_sum_mm": sums,
        "rain_max_3d_mm": rain_max_3d(window),
        "wet_days": wet_days(window),
        "max_dry_spell_days": max_dry_spell(window),
        "tmean_c": _tmean(window),
        "tmin_min_c": min(tmins) if tmins else None,
        "tmax_max_c": max(tmaxs) if tmaxs else None,
        "frost_days": sum(1 for v in tmins if v <= FROST_C),
        "diurnal_range_c": _diurnal_range(window),
        "et0_sum_mm": et0_sum,
        "water_balance_mm": _round(window_rain - et0_sum)
        if window_rain is not None and et0_sum is not None
        else None,
        "rh_mean_pct": _round(sum(rhs) / len(rhs)) if rhs else None,
    }
