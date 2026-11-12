"""Fournisseur « fixture » : données DÉTERMINISTES ET FACTICES, sans réseau (tests, démonstration hors ligne).

Rien ici n'est une observation météo. Une pluie manquante tous les 17 jours permet d'exercer le contrôle
qualité. Le lot 1 ajoutera les fournisseurs réels derrière la même interface.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.schemas.weather import DailyRecord, GeocodeResult, Source

PLACES = [
    GeocodeResult(name="Dakar", country="Sénégal", admin1="Dakar", latitude=14.6937, longitude=-17.4441),
    GeocodeResult(name="Thiès", country="Sénégal", admin1="Thiès", latitude=14.791, longitude=-16.9359),
    GeocodeResult(
        name="Saint-Louis", country="Sénégal", admin1="Saint-Louis", latitude=16.0179, longitude=-16.4896
    ),
]


class FixtureProvider:
    id = "fixture"
    source = Source(
        id="fixture",
        attribution=None,
        spatial_resolution_note="Données factices de démonstration : aucune valeur réelle.",
    )

    def daily(self, latitude: float, longitude: float, start: date, end: date) -> list[DailyRecord]:
        out = []
        d = start
        while d <= end:
            k = d.toordinal()
            out.append(
                DailyRecord(
                    date=d,
                    precipitation_mm=None if k % 17 == 0 else round((k * 7 % 13) / 2, 1),
                    tmax_c=30 + (k % 5),
                    tmin_c=22 + (k % 3),
                    tmean_c=26 + (k % 3) / 2,
                    rh_mean_pct=60 + (k % 20),
                    et0_mm=4 + (k % 3) / 2,
                )
            )
            d += timedelta(days=1)
        return out

    def geocode(self, q: str, limit: int, language: str) -> list[GeocodeResult]:
        needle = q.strip().lower()
        return [p for p in PLACES if needle in p.name.lower()][:limit]
