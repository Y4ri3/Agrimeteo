"""Moteur de règles : critères P-01 à P-07 du cahier (aucun accès réseau, aucune donnée réelle)."""

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

from agrimeteo_ml import engine, load_profile, load_profiles
from agrimeteo_ml.profiles import problems

RULES = Path(__file__).resolve().parents[1] / "rules"
FULL = {"precipitation_mm": 100, "tmin_c": 100, "tmax_c": 100}


@dataclass
class Day:
    date: date
    precipitation_mm: float | None
    tmin_c: float | None = 22.0
    tmax_c: float | None = 33.0
    tmean_c: float | None = 27.0
    rh_mean_pct: float | None = 60.0
    et0_mm: float | None = 5.0


def month(rain_total=120.0, dry_spell=4, tmax=33.0, tmin=22.0, n=30):
    """30 jours : `dry_spell` jours secs, puis la pluie répartie à parts égales (comme le notebook)."""
    share = rain_total / (n - dry_spell)
    return [
        Day(date(2026, 1, 1) + timedelta(i), 0.0 if i < dry_spell else share, tmin_c=tmin, tmax_c=tmax)
        for i in range(n)
    ]


CRITERIA = [
    {
        "id": "chaleur",
        "label": "Chaleur",
        "indicator": "tmax_max",
        "unit": "°C",
        "direction": "higher_is_worse",
        "blocking": True,
        "thresholds": {"vigilance": 38, "unfavorable": 42},
        "source": "s",
    },
    {
        "id": "secheresse",
        "label": "Sécheresse",
        "indicator": "max_dry_spell",
        "unit": "jours",
        "direction": "higher_is_worse",
        "blocking": True,
        "thresholds": {"vigilance": 10, "unfavorable": 20},
        "source": "s",
    },
    {
        "id": "pluie",
        "label": "Pluie",
        "indicator": "rain_sum",
        "unit": "mm",
        "direction": "lower_is_worse",
        "blocking": False,
        "thresholds": {"vigilance": 60, "unfavorable": None},
        "source": "s",
    },
]


def profile(tmp_path, status="valide_par_source", criteria=None):
    f = tmp_path / "p.yaml"
    f.write_text(
        yaml.safe_dump(
            {"id": "p", "label": "Test", "version": "1", "status": status, "criteria": criteria or CRITERIA}
        )
    )
    return load_profile(f)


def run(p, days, completeness=FULL, **kw):
    return engine.evaluate(p, days, completeness, **kw)


def statuses(ev):
    return {c.id: c.status for c in ev.criteria}


def test_scenarios_of_the_lot_2_notebook(tmp_path):  # P-01 à P-04, scénarios du notebook
    p = profile(tmp_path)
    good = run(p, month(120, 4, 33.0))
    assert good.level == "favorable" and statuses(good) == {
        "chaleur": "ok",
        "secheresse": "ok",
        "pluie": "ok",
    }
    assert run(p, month(40, 4, 33.0)).level == "favorable_sous_reserve"  # vigilance non bloquante
    assert (
        run(p, month(300, 2, 44.0)).level == "peu_favorable"
    )  # chaleur extrême jamais compensée par la pluie


@pytest.mark.parametrize(
    ("tmax", "expected"), [(37.9, "ok"), (38.0, "vigilance"), (41.9, "vigilance"), (42.0, "defavorable")]
)
def test_higher_is_worse_bounds_are_reached_not_exceeded(tmp_path, tmax, expected):  # P-02
    assert statuses(run(profile(tmp_path), month(tmax=tmax)))["chaleur"] == expected


@pytest.mark.parametrize(("rain", "expected"), [(60.1, "ok"), (60.0, "vigilance"), (0.0, "vigilance")])
def test_lower_is_worse_bounds_are_reached_not_exceeded(tmp_path, rain, expected):  # P-02
    assert statuses(run(profile(tmp_path), month(rain_total=rain)))["pluie"] == expected


def test_one_sided_thresholds(tmp_path):
    crit = [
        {
            "id": "gel",
            "indicator": "frost_days",
            "direction": "higher_is_worse",
            "blocking": True,
            "thresholds": {"vigilance": None, "unfavorable": 1},
            "source": "s",
        },
        {
            "id": "pluie",
            "indicator": "rain_sum",
            "direction": "lower_is_worse",
            "blocking": False,
            "thresholds": {"vigilance": 60, "unfavorable": None},
            "source": "s",
        },
    ]
    p = profile(tmp_path, criteria=crit)
    assert statuses(run(p, month(tmin=0.0)))["gel"] == "defavorable"
    assert statuses(run(p, month(tmin=5.0)))["gel"] == "ok"
    assert run(p, month(tmin=0.0)).level == "peu_favorable"


def test_same_inputs_same_output(tmp_path):  # P-01
    p = profile(tmp_path)
    assert run(p, month(40, 12)) == run(p, month(40, 12))


def test_insufficient_data_is_indeterminate_never_favorable(tmp_path):  # P-03
    ev = run(profile(tmp_path), month(), {"precipitation_mm": 40, "tmin_c": 100, "tmax_c": 100})
    assert ev.level == "indetermine" and ev.confidence_level == "faible"
    assert "insuffisantes" in ev.summary and "precipitation_mm : 40" in ev.summary


def test_completeness_threshold_is_configurable_and_default_90(tmp_path):  # D-04
    almost = {"precipitation_mm": 89, "tmin_c": 100, "tmax_c": 100}
    assert run(profile(tmp_path), month(), almost).level == "indetermine"
    assert run(profile(tmp_path), month(), almost, min_completeness=80).level != "indetermine"


def test_too_few_evaluable_criteria_is_indeterminate(tmp_path):  # P-03
    p = profile(tmp_path)
    assert run(p, []).level == "indetermine"  # aucune fenêtre complète : rien n'est évaluable
    assert all(s == "non_evaluable" for s in statuses(run(p, [])).values())


def test_window_shorter_than_the_criterion_is_not_evaluable(tmp_path):
    ev = run(profile(tmp_path), month(n=30)[-10:])
    assert set(statuses(ev).values()) == {"non_evaluable"} and "trop courte" in ev.criteria[0].explanation


def test_heavy_rain_with_frost_is_never_favorable(tmp_path):  # P-04
    crit = CRITERIA + [
        {
            "id": "gel",
            "label": "Gel",
            "indicator": "frost_days",
            "direction": "higher_is_worse",
            "blocking": True,
            "thresholds": {"vigilance": None, "unfavorable": 1},
            "source": "s",
        }
    ]
    ev = run(profile(tmp_path, criteria=crit), month(rain_total=500, tmin=-2.0))
    assert ev.level == "peu_favorable" and "Gel" in ev.summary


def test_every_result_has_french_explanations_citing_criteria(tmp_path):  # P-05
    ev = run(profile(tmp_path), month(300, 2, 44.0))
    assert all(len(c.explanation) > 10 for c in ev.criteria)
    chaleur = next(c for c in ev.criteria if c.id == "chaleur")
    assert "44 °C" in chaleur.explanation and "seuil défavorable (42 °C)" in chaleur.explanation


def test_results_carry_what_the_interface_needs_to_draw_a_gauge(tmp_path):
    c = next(c for c in run(profile(tmp_path), month(300, 2, 44.0)).criteria if c.id == "chaleur")
    assert (c.value, c.vigilance, c.unfavorable, c.unit, c.window_days) == (44.0, 38, 42, "°C", 30)
    assert c.direction == "higher_is_worse" and c.blocking


def test_unvalidated_profile_caps_at_favorable_sous_reserve(tmp_path):  # P-07
    ev = run(profile(tmp_path, status="a_valider"), month())
    assert set(statuses(ev).values()) == {"ok"} and ev.level == "favorable_sous_reserve"
    assert any("à valider" in limit for limit in ev.limits)


def test_confidence_levels(tmp_path):
    p = profile(tmp_path)
    assert run(p, month()).confidence_level == "moyenne"
    assert run(p, month(), fine_resolution=True).confidence_level == "elevee"
    unvalidated, so_so = (
        profile(tmp_path, status="a_valider"),
        {"precipitation_mm": 92, "tmin_c": 100, "tmax_c": 100},
    )
    assert run(unvalidated, month()).confidence_level == "moyenne"  # bonne complétude
    assert (
        run(unvalidated, month(), so_so).confidence_level == "faible"
    )  # profil à valider et données moyennes


# ----- profils du dépôt (P-06) -----
def test_repository_profiles_are_the_notebook_ones_and_sourced():  # P-06
    profiles = load_profiles(RULES)
    assert set(profiles) == {"tomate", "riz", "arachide", "mil"}
    for p in profiles.values():
        assert p.status == "a_valider"
        for c in p.criteria:
            assert c.source and (c.vigilance is not None or c.unfavorable is not None), f"{p.id}/{c.id}"


@pytest.mark.parametrize("crop", ["tomate", "riz", "arachide", "mil"])
def test_repository_profiles_run_end_to_end_and_stay_cautious(crop):  # P-07
    ev = run(load_profiles(RULES)[crop], month(120, 4, 33.0, tmin=22.0))
    assert ev.level in {"favorable_sous_reserve", "peu_favorable"} and ev.level != "favorable"


@pytest.mark.parametrize(
    ("patch", "message"),
    [
        ({"status": "valide"}, "status invalide"),
        (
            {
                "criteria": [
                    {
                        "id": "x",
                        "indicator": "rain_sum",
                        "direction": "lower_is_worse",
                        "thresholds": {"vigilance": 5, "unfavorable": 1},
                    }
                ]
            },
            "sans source",
        ),
        (
            {
                "criteria": [
                    {
                        "id": "x",
                        "indicator": "rain_sum",
                        "direction": "lower_is_worse",
                        "thresholds": {"vigilance": 1, "unfavorable": 5},
                        "source": "s",
                    }
                ]
            },
            "incohérents",
        ),
        (
            {
                "criteria": [
                    {
                        "id": "x",
                        "indicator": "inconnu",
                        "direction": "lower_is_worse",
                        "thresholds": {"vigilance": 5},
                        "source": "s",
                    }
                ]
            },
            "indicateur inconnu",
        ),
        (
            {
                "status": "valide_par_source",
                "criteria": [
                    {
                        "id": "x",
                        "indicator": "rain_sum",
                        "direction": "lower_is_worse",
                        "thresholds": {"vigilance": None, "unfavorable": None},
                    }
                ],
            },
            "exige",
        ),
    ],
)
def test_invalid_profiles_are_rejected(patch, message):  # P-06
    base = {
        "id": "p",
        "label": "P",
        "version": "1",
        "status": "a_valider",
        "criteria": [
            {
                "id": "x",
                "indicator": "rain_sum",
                "direction": "lower_is_worse",
                "thresholds": {"vigilance": 5, "unfavorable": 1},
                "source": "s",
            }
        ],
    }
    assert any(message in p for p in problems({**base, **patch}))
