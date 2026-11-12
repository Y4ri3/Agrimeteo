"""Contrôle qualité des données (D-02, D-03)."""

from datetime import date

from app.schemas.weather import DailyRecord
from app.services import quality

D = date(2026, 10, 1)


def rec(day, **kw):
    base = {
        "precipitation_mm": 1.0,
        "tmax_c": 30.0,
        "tmin_c": 20.0,
        "tmean_c": 25.0,
        "rh_mean_pct": 60.0,
        "et0_mm": 4.0,
    }
    return DailyRecord(date=date(2026, 10, day), **{**base, **kw})


def run(records, days=3):
    return quality.check(records, D, date(2026, 10, days))


def reasons(q):
    return {(f.variable, f.reason) for f in q.flagged_values}


def test_clean_series_is_complete():
    series, q = run([rec(1), rec(2), rec(3)])
    assert q.missing_days == 0 and q.flagged_values == []
    assert all(v == 100 for v in q.completeness_pct.values())
    assert len(series) == 3


def test_negative_rain_is_flagged_and_not_zeroed():  # D-02, D-03
    series, q = run([rec(1, precipitation_mm=-5), rec(2), rec(3)])
    assert ("precipitation_mm", "out_of_range") in reasons(q)
    assert series[0].precipitation_mm is None


def test_tmin_above_tmax_is_flagged():  # D-02
    series, q = run([rec(1, tmin_c=35, tmax_c=25), rec(2), rec(3)])
    assert {("tmin_c", "out_of_range"), ("tmax_c", "out_of_range")} <= reasons(q)
    assert series[0].tmin_c is None and series[0].tmax_c is None


def test_humidity_out_of_range_is_flagged():  # D-02
    _, q = run([rec(1, rh_mean_pct=140), rec(2), rec(3)])
    assert ("rh_mean_pct", "out_of_range") in reasons(q)


def test_missing_and_duplicate_dates_are_counted():  # D-03
    series, q = run([rec(1), rec(1), rec(3)])
    assert ("date", "duplicate") in reasons(q) and ("date", "missing") in reasons(q)
    assert len(series) == 3 and series[1].precipitation_mm is None
