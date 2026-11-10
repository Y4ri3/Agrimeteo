"""Fournisseur CSV : fichier d'essai minuscule, aucun accès réseau."""

from datetime import date

import pytest

from app import providers
from app.core import errors
from app.providers.csv_file import CsvProvider

HEADER = (
    "date,localite,region,zone_agroecologique,latitude,longitude,"
    "precipitation_mm,tmin_c,tmax_c,tmean_c,rh_mean_pct,et0_mm\n"
)
ROWS = (
    "2025-10-01,Dakar,Dakar,Niayes,14.6937,-17.44406,0.0,22.0,30.0,26.0,70,5.1\n"
    "2025-10-02,Dakar,Dakar,Niayes,14.6937,-17.44406,,22.5,31.0,26.7,72,5.0\n"
    "2025-10-03,Dakar,Dakar,Niayes,14.6937,-17.44406,12.4,21.9,29.8,25.9,80,4.2\n"
    "2025-10-01,Kaolack,Kaolack,Bassin arachidier,14.15,-16.07,3.0,23.0,33.0,28.0,60,6.0\n"
)


@pytest.fixture()
def csv_provider(tmp_path):
    f = tmp_path / "meteo.csv"
    f.write_text(HEADER + ROWS, encoding="utf-8")
    return CsvProvider(str(f))


def test_nearest_place_answers_and_missing_stays_null(csv_provider):  # D-03
    records = csv_provider.daily(14.7, -17.4, date(2025, 10, 1), date(2025, 10, 3))
    assert [r.precipitation_mm for r in records] == [0.0, None, 12.4]
    assert records[2].tmax_c == 29.8 and records[2].rh_mean_pct == 80


def test_period_is_respected(csv_provider):
    assert len(csv_provider.daily(14.7, -17.4, date(2025, 10, 2), date(2025, 10, 2))) == 1


def test_far_away_has_no_data(csv_provider):
    assert csv_provider.daily(48.85, 2.35, date(2025, 10, 1), date(2025, 10, 3)) == []  # Paris


def test_geocode_ignores_accents_and_case(csv_provider):
    assert csv_provider.geocode("KAOLACK", 5, "fr")[0].admin1 == "Kaolack"
    assert csv_provider.geocode("zzz", 5, "fr") == []  # A-07


def test_missing_file_is_a_provider_error(tmp_path):  # A-05
    with pytest.raises(errors.ProviderUnavailable):
        CsvProvider(str(tmp_path / "absent.csv")).daily(0, 0, date(2025, 10, 1), date(2025, 10, 2))


def test_csv_is_selectable_and_indeterminate_outside_coverage(client, monkeypatch, csv_provider):
    monkeypatch.setitem(providers.REGISTRY, "csv", csv_provider)
    body = client.post(
        "/api/v1/predictions",
        json={
            "location": {"latitude": 14.7, "longitude": -17.4},
            "crop_id": "culture_exemple_a",
            "reference_date": "2025-10-20",
            "window_days": 14,
            "source": "csv",
        },
    ).json()
    assert body["meteorological_favorability"]["level"] == "indetermine"  # P-03 : fenêtre sans données
    assert body["data_quality"]["completeness_pct"]["precipitation_mm"] < 80
