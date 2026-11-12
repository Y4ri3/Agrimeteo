"""Indicateurs : valeurs attendues, valeurs manquantes jamais comptées pour 0."""

from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from agrimeteo_ml import indicator_value
from agrimeteo_ml import indicators as ind


@dataclass
class Day:
    date: date
    precipitation_mm: float | None = 0.0
    tmin_c: float | None = 20.0
    tmax_c: float | None = 30.0
    tmean_c: float | None = None
    rh_mean_pct: float | None = 60.0
    et0_mm: float | None = 5.0


def days(rain, **kw):
    start = date(2026, 1, 1)
    return [Day(start + timedelta(i), precipitation_mm=r, **kw) for i, r in enumerate(rain)]


def test_rain_sum_windows():
    d = days([1, 2, 3, 4, 5, 6, 7, 8])
    assert ind.rain_sum(d, 3) == 21 and ind.rain_sum(d, 8) == 36 and ind.rain_sum(d) == 36


def test_missing_rain_is_not_zero():
    d = days([5, None, 5])
    assert ind.rain_sum(d, 3) == 10  # somme des jours connus seulement
    assert ind.rain_max_3d(d) is None  # un jour inconnu interdit la fenêtre de 3 jours
    assert ind.rain_sum(days([None, None]), 2) is None


def test_rain_max_3d():
    assert ind.rain_max_3d(days([0, 12, 9, 0, 30, 0, 0])) == 39  # 9 + 0 + 30


def test_wet_days_and_dry_spell():
    d = days([0, 0.5, 0, 0, 3, 0, 0, 0, 0, 2])
    assert ind.wet_days(d) == 2  # 3 et 2 mm ; 0,5 mm est sec (< 1 mm)
    assert ind.max_dry_spell(d) == 4


def test_unknown_day_interrupts_dry_spell():
    assert ind.max_dry_spell(days([0, 0, None, 0, 0, 0])) == 3


def test_temperatures():
    r = ind.compute(days([0] * 10, tmin_c=10.0, tmax_c=30.0), 10)
    assert (
        r["tmean_c"] == 20 and r["diurnal_range_c"] == 20 and r["tmin_min_c"] == 10 and r["tmax_max_c"] == 30
    )
    assert r["frost_days"] == 0
    assert ind.compute(days([0] * 5, tmin_c=-1.0), 5)["frost_days"] == 5


def test_tmean_prefers_the_source_value_over_the_midpoint():
    assert ind.tmean(days([0, 0], tmin_c=20.0, tmax_c=30.0, tmean_c=24.0)) == 24  # pas (20 + 30) / 2
    assert ind.tmean(days([0, 0], tmin_c=20.0, tmax_c=30.0)) == 25  # à défaut : milieu


def test_unknown_temperature_is_not_zero_frost():
    assert ind.frost_days(days([0, 0], tmin_c=None)) is None


def test_water_balance_needs_complete_et0():
    complete = ind.compute(days([10] * 10, et0_mm=2.0), 10)
    assert complete["et0_sum_mm"] == 20 and complete["water_balance_mm"] == 80
    d = days([10] * 10, et0_mm=2.0)
    d[3].et0_mm = None
    gap = ind.compute(d, 10)
    assert gap["et0_sum_mm"] is None and gap["water_balance_mm"] is None


def test_compute_uses_only_the_window_and_is_deterministic():  # P-01
    d = days([100] * 5 + [1] * 10)
    first, second = ind.compute(d, 10), ind.compute(d, 10)
    assert first == second and first["rain_sum_mm"]["10d"] == 10
    assert set(first["rain_sum_mm"]) == {"3d", "7d", "10d"}


def test_indicator_value_by_name_and_window():
    d = days([10] * 5 + [0] * 25)
    assert indicator_value(d, "rain_sum", 30) == 50
    assert indicator_value(d, "max_dry_spell", 10) == 10  # les 10 derniers jours sont secs
    assert indicator_value(d, "rain_sum", 40) is None  # fenêtre plus longue que la période
    with pytest.raises(ValueError):
        indicator_value(d, "inconnu", 5)
