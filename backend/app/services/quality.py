"""Contrôle qualité d'une série journalière (D-02, D-03, D-04).

Une valeur aberrante est signalée puis traitée comme MANQUANTE ; une valeur manquante n'est jamais remplacée
par 0.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.core import config
from app.schemas.weather import DailyRecord, FlaggedValue, Quality

VARIABLES = ["precipitation_mm", "tmax_c", "tmin_c", "rh_mean_pct", "et0_mm"]
# Variables sans lesquelles la favorabilité ne peut pas être évaluée (cahier, 7.1).
ESSENTIAL = ["precipitation_mm", "tmax_c", "tmin_c"]


def check(daily: list[DailyRecord], start: date, end: date) -> tuple[list[DailyRecord], Quality]:
    """Renvoie une série complète sur [start, end] (une ligne par jour, trous = null) et son rapport."""
    flagged: list[FlaggedValue] = []
    by_date: dict[date, DailyRecord] = {}
    for rec in daily:
        if rec.date < start or rec.date > end:
            continue
        if rec.date in by_date:
            flagged.append(FlaggedValue(date=rec.date, variable="date", reason="duplicate"))
            continue
        by_date[rec.date] = rec

    series: list[DailyRecord] = []
    d = start
    while d <= end:
        rec = by_date.get(d)
        if rec is None:
            flagged.append(FlaggedValue(date=d, variable="date", reason="missing"))
            rec = DailyRecord(date=d)
        else:
            rec = _sanitize(rec, flagged)
        series.append(rec)
        d += timedelta(days=1)

    n = len(series) or 1
    completeness = {v: round(100 * sum(getattr(r, v) is not None for r in series) / n, 1) for v in VARIABLES}
    keys = {(f.date, f.variable) for f in flagged}
    absent = {f.date for f in flagged if f.variable == "date" and f.reason == "missing"}
    for r in series:
        if r.date in absent:
            continue
        for v in VARIABLES:
            if getattr(r, v) is None and (r.date, v) not in keys:
                flagged.append(FlaggedValue(date=r.date, variable=v, reason="missing"))
    flagged.sort(key=lambda f: (f.date, f.variable))
    return series, Quality(
        completeness_pct=completeness,
        missing_days=len({f.date for f in flagged}),
        flagged_values=flagged,
    )


def _sanitize(rec: DailyRecord, flagged: list[FlaggedValue]) -> DailyRecord:
    data = rec.model_dump()

    def reject(variable: str) -> None:
        data[variable] = None
        flagged.append(FlaggedValue(date=rec.date, variable=variable, reason="out_of_range"))

    if rec.precipitation_mm is not None and rec.precipitation_mm < 0:
        reject("precipitation_mm")
    if rec.rh_mean_pct is not None and not 0 <= rec.rh_mean_pct <= 100:
        reject("rh_mean_pct")
    if rec.et0_mm is not None and rec.et0_mm < 0:
        reject("et0_mm")
    if rec.tmin_c is not None and rec.tmax_c is not None and rec.tmin_c > rec.tmax_c:
        reject("tmin_c")
        reject("tmax_c")
    return DailyRecord(**data)


def insufficient(quality: Quality) -> list[str]:
    """Variables essentielles sous le seuil de complétude configuré (vide = données suffisantes)."""
    return [
        f"{v} : {quality.completeness_pct.get(v, 0)} % de données (minimum {config.MIN_COMPLETENESS_PCT} %)"
        for v in ESSENTIAL
        if quality.completeness_pct.get(v, 0) < config.MIN_COMPLETENESS_PCT
    ]
