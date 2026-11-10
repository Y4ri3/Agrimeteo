"""Moteur de règles : critères P-01 à P-07 du cahier (aucun accès réseau, aucune donnée réelle)."""

from pathlib import Path

import pytest
import yaml

from agrimeteo_ml import engine, load_profile, load_profiles
from agrimeteo_ml.profiles import problems

RULES = Path(__file__).resolve().parents[1] / "rules"
FULL = {"precipitation_mm": 100, "tmin_c": 100, "tmax_c": 100}


def profile(tmp_path, status="valide_par_source", criteria=None):
    criteria = criteria or [
        {
            "id": "pluie",
            "label": "Pluie",
            "indicator": "rain",
            "unit": "mm",
            "direction": "lower_is_worse",
            "blocking": True,
            "thresholds": {"vigilance": 20, "unfavorable": 10},
            "source": "s",
        },
        {
            "id": "gel",
            "label": "Gel",
            "indicator": "frost",
            "unit": "jours",
            "direction": "higher_is_worse",
            "blocking": True,
            "thresholds": {"vigilance": 1, "unfavorable": 3},
            "source": "s",
        },
    ]
    f = tmp_path / "p.yaml"
    f.write_text(
        yaml.safe_dump({"id": "p", "label": "Test", "version": "1", "status": status, "criteria": criteria})
    )
    return load_profile(f)


def run(p, rain, frost, completeness=FULL):
    return engine.evaluate(p, {"rain": rain, "frost": frost}, completeness)


def statuses(ev):
    return {c.id: c.status for c in ev.criteria}


@pytest.mark.parametrize(
    ("rain", "expected"),
    [
        (25, "ok"),
        (20, "ok"),
        (19.9, "vigilance"),
        (10, "vigilance"),
        (9.9, "defavorable"),
        (None, "non_evaluable"),
    ],
)
def test_lower_is_worse_bounds(tmp_path, rain, expected):  # P-02
    assert statuses(run(profile(tmp_path), rain, 0))["pluie"] == expected


@pytest.mark.parametrize(
    ("frost", "expected"),
    [(0, "ok"), (1, "vigilance"), (2, "vigilance"), (3, "defavorable"), (None, "non_evaluable")],
)
def test_higher_is_worse_bounds(tmp_path, frost, expected):  # P-02
    assert statuses(run(profile(tmp_path), 30, frost))["gel"] == expected


def test_same_inputs_same_output(tmp_path):  # P-01
    p = profile(tmp_path)
    assert run(p, 15, 1) == run(p, 15, 1)


def test_insufficient_data_is_indeterminate_never_favorable(tmp_path):  # P-03
    ev = run(profile(tmp_path), 30, 0, {"precipitation_mm": 40, "tmin_c": 100, "tmax_c": 100})
    assert ev.level == "indetermine" and ev.confidence_level == "faible"
    assert "insuffisantes" in ev.summary and "precipitation_mm : 40" in ev.summary


def test_too_few_evaluable_criteria_is_indeterminate(tmp_path):  # P-03
    assert run(profile(tmp_path), None, None).level == "indetermine"


def test_heavy_rain_with_frost_is_never_favorable(tmp_path):  # P-04
    ev = run(profile(tmp_path), 200, 5)
    assert ev.level == "peu_favorable" and "Gel" in ev.summary


def test_every_result_has_french_explanations_citing_criteria(tmp_path):  # P-05
    ev = run(profile(tmp_path), 15, 0)
    assert len(ev.criteria) == 2 and all(c.explanation for c in ev.criteria)
    assert "15 mm" in next(c for c in ev.criteria if c.id == "pluie").explanation
    assert "seuil de vigilance franchi (20 mm)" in ev.criteria[0].explanation


def test_unvalidated_profile_caps_at_favorable_sous_reserve(tmp_path):  # P-07
    ev = run(profile(tmp_path, status="a_valider"), 30, 0)
    assert statuses(ev) == {"pluie": "ok", "gel": "ok"} and ev.level == "favorable_sous_reserve"
    assert any("à valider" in limit for limit in ev.limits)


def test_validated_profile_all_ok_is_favorable(tmp_path):
    ev = run(profile(tmp_path), 30, 0)
    assert ev.level == "favorable" and ev.confidence_level == "moyenne"
    assert (
        engine.evaluate(
            profile(tmp_path), {"rain": 30, "frost": 0}, FULL, fine_resolution=True
        ).confidence_level
        == "elevee"
    )


def test_vigilance_gives_favorable_sous_reserve(tmp_path):
    assert run(profile(tmp_path), 15, 0).level == "favorable_sous_reserve"


def test_non_blocking_criteria_never_make_it_unfavorable(tmp_path):
    crit = [
        {
            "id": "a",
            "indicator": "rain",
            "direction": "lower_is_worse",
            "blocking": False,
            "thresholds": {"vigilance": 20, "unfavorable": 10},
            "source": "s",
        },
        {
            "id": "b",
            "indicator": "frost",
            "direction": "higher_is_worse",
            "blocking": False,
            "thresholds": {"vigilance": 1, "unfavorable": 3},
            "source": "s",
        },
    ]
    assert run(profile(tmp_path, criteria=crit), 0, 9).level == "favorable_sous_reserve"


# ----- profils du dépôt (P-06) -----
def test_repository_profiles_are_valid_and_sourced():  # P-06
    profiles = load_profiles(RULES)
    assert {"arachide", "mil"} <= set(profiles)
    for p in profiles.values():
        for c in p.criteria:
            assert c.source and c.vigilance is not None, f"{p.id}/{c.id} sans source ou sans seuil"


@pytest.mark.parametrize(
    ("patch", "message"),
    [
        ({"status": "valide"}, "status invalide"),
        (
            {
                "criteria": [
                    {
                        "id": "x",
                        "indicator": "i",
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
                        "indicator": "i",
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
                        "indicator": "i",
                        "direction": "lower_is_worse",
                        "thresholds": {"vigilance": 5},
                        "source": "s",
                    }
                ]
            },
            "ensemble",
        ),
        (
            {
                "status": "valide_par_source",
                "criteria": [
                    {
                        "id": "x",
                        "indicator": "i",
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
                "indicator": "i",
                "direction": "lower_is_worse",
                "thresholds": {"vigilance": 5, "unfavorable": 1},
                "source": "s",
            }
        ],
    }
    assert any(message in p for p in problems({**base, **patch}))
