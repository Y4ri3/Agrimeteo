"""DONNÉES FACTICES du squelette (à remplacer par le lot 1 et le lot 2).

Rien ici n'est une observation météo ni un résultat agronomique. Ces fonctions
permettent seulement au frontend, à Docker, à GitHub Actions et aux tests de bout en bout
de fonctionner dès le jour 2.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.schemas.indicators import Indicators
from app.schemas.predictions import Crop
from app.schemas.weather import DailyRecord, FlaggedValue, GeocodeResult, Quality, Source

STUB_SOURCE = Source(
    id="fixture",
    attribution=None,
    spatial_resolution_note="Données factices du squelette : aucune valeur réelle.",
)

CROPS = [
    Crop(
        id="culture_exemple_a",
        label="Culture exemple A (profil de démonstration)",
        rule_profile_version="0.1.0",
        rule_status="a_valider",
    ),
]

PLACES = [
    GeocodeResult(name="Dakar", country="Sénégal", admin1="Dakar", latitude=14.6937, longitude=-17.4441),
    GeocodeResult(name="Thiès", country="Sénégal", admin1="Thiès", latitude=14.791, longitude=-16.9359),
    GeocodeResult(
        name="Saint-Louis", country="Sénégal", admin1="Saint-Louis", latitude=16.0179, longitude=-16.4896
    ),
]


def default_reference_date() -> date:
    return date.today() - timedelta(days=2)


def search_places(q: str, limit: int) -> list[GeocodeResult]:
    needle = q.strip().lower()
    return [p for p in PLACES if needle in p.name.lower()][:limit]


def daily_series(start: date, end: date) -> list[DailyRecord]:
    """Série déterministe : une pluie manquante tous les 17 jours (pour tester la qualité)."""
    out = []
    d = start
    while d <= end:
        k = d.toordinal()
        rain = None if k % 17 == 0 else round((k * 7 % 13) / 2, 1)
        out.append(
            DailyRecord(
                date=d,
                precipitation_mm=rain,
                tmax_c=30 + (k % 5),
                tmin_c=22 + (k % 3),
                rh_mean_pct=60 + (k % 20),
                et0_mm=4 + (k % 3) / 2,
            )
        )
        d += timedelta(days=1)
    return out


def quality_of(daily: list[DailyRecord]) -> Quality:
    n = len(daily) or 1
    variables = ["precipitation_mm", "tmax_c", "tmin_c", "rh_mean_pct", "et0_mm"]
    completeness = {v: round(100 * sum(getattr(r, v) is not None for r in daily) / n, 1) for v in variables}
    flagged = [
        FlaggedValue(date=r.date, variable="precipitation_mm", reason="missing")
        for r in daily
        if r.precipitation_mm is None
    ]
    return Quality(completeness_pct=completeness, missing_days=len(flagged), flagged_values=flagged)


def _rain_sum(daily: list[DailyRecord], days: int) -> float | None:
    values = [r.precipitation_mm for r in daily[-days:] if r.precipitation_mm is not None]
    return round(sum(values), 1) if values else None


def compute_indicators(reference_date: date, window_days: int) -> tuple[Indicators, Quality]:
    start = reference_date - timedelta(days=window_days - 1)
    daily = daily_series(start, reference_date)
    rain_w = _rain_sum(daily, window_days)
    et0 = round(sum(r.et0_mm or 0 for r in daily), 1)
    ind = Indicators(
        rain_sum_mm={"7d": _rain_sum(daily, 7), f"{window_days}d": rain_w},
        frost_days=sum(1 for r in daily if r.tmin_c is not None and r.tmin_c <= 0),
        water_balance_mm=None if rain_w is None else round(rain_w - et0, 1),
    )
    return ind, quality_of(daily)
