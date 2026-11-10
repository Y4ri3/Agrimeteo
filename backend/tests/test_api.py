"""Tests du contrat : succès et chaque code d'erreur documenté (A-01 à A-08). Aucun accès réseau."""

import pytest

from app import providers
from app.core import errors
from app.providers.fixture import FixtureProvider

REF = "2026-10-21"
LOC = {"latitude": 14.7, "longitude": -17.4}
PRED = {"location": LOC, "crop_id": "test_a", "reference_date": REF}


def test_health(client):  # A-01
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ---------- /geocode et /crops (A-07) ----------
def test_geocode_finds_place(client):
    r = client.get("/api/v1/geocode", params={"q": "dak"})
    assert r.status_code == 200
    assert r.json()["results"][0]["name"] == "Dakar"


def test_geocode_empty_list_is_not_an_error(client):  # A-07
    r = client.get("/api/v1/geocode", params={"q": "zzzzzz"})
    assert r.status_code == 200
    assert r.json() == {"results": []}


@pytest.mark.parametrize("params", [{"q": "a"}, {"q": "dakar", "limit": 11}, {}])
def test_geocode_validation(client, params):  # A-03
    r = client.get("/api/v1/geocode", params=params)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_crops_listed(client):  # A-07
    assert len(client.get("/api/v1/crops").json()["crops"]) >= 1


# ---------- /weather ----------
def test_weather_success(client):
    r = client.get("/api/v1/weather", params={**LOC, "start_date": "2026-10-01", "end_date": REF})
    body = r.json()
    assert r.status_code == 200
    assert len(body["daily"]) == 21
    assert body["request_id"] and r.headers["X-Request-Id"] == body["request_id"]


def test_weather_marks_missing_values(client):  # D-03
    r = client.get("/api/v1/weather", params={**LOC, "start_date": "2026-10-01", "end_date": REF})
    body = r.json()
    missing = [d for d in body["daily"] if d["precipitation_mm"] is None]
    assert missing, "la fixture contient des trous"
    assert body["quality"]["missing_days"] == len(missing)
    assert all(f["reason"] == "missing" for f in body["quality"]["flagged_values"])


@pytest.mark.parametrize(
    ("params", "code"),
    [
        ({"latitude": 200, "longitude": 0, "start_date": REF, "end_date": REF}, "VALIDATION_ERROR"),
        ({**LOC, "start_date": REF, "end_date": "2026-10-01"}, "VALIDATION_ERROR"),
        ({**LOC, "start_date": "not-a-date", "end_date": REF}, "VALIDATION_ERROR"),
        ({**LOC, "start_date": "2024-01-01", "end_date": "2026-01-01"}, "PERIOD_TOO_LONG"),
        ({**LOC, "start_date": "2999-01-01", "end_date": "2999-01-05"}, "DATE_OUT_OF_RANGE"),
        ({**LOC, "start_date": "1800-01-01", "end_date": "1800-01-05"}, "DATE_OUT_OF_RANGE"),
        ({**LOC, "start_date": REF, "end_date": REF, "source": "inconnue"}, "VALIDATION_ERROR"),
    ],
)
def test_weather_422(client, params, code):  # A-03, A-04
    r = client.get("/api/v1/weather", params=params)
    body = r.json()
    assert r.status_code == 422
    assert body["error"]["code"] == code
    assert body["request_id"]


# ---------- /indicators ----------
def test_indicators_success(client):
    r = client.get("/api/v1/indicators", params={**LOC, "reference_date": REF, "window_days": 14})
    body = r.json()
    assert r.status_code == 200
    assert body["window_days"] == 14
    assert set(body["indicators"]["rain_sum_mm"]) == {"3d", "7d", "14d"}


@pytest.mark.parametrize("window", [6, 91])
def test_indicators_window_bounds(client, window):  # A-03
    r = client.get("/api/v1/indicators", params={**LOC, "reference_date": REF, "window_days": window})
    assert r.status_code == 422


def test_indicators_match_prediction(client):  # A-08
    ind = client.get("/api/v1/indicators", params={**LOC, "reference_date": REF}).json()["indicators"]
    assert client.post("/api/v1/predictions", json=PRED).json()["indicators"] == ind


# ---------- /predictions ----------
def test_prediction_returns_three_distinct_blocks(client):  # A-06
    r = client.post("/api/v1/predictions", json=PRED)
    body = r.json()
    assert r.status_code == 200
    assert body["meteorological_favorability"]["level"] in {
        "favorable",
        "favorable_sous_reserve",
        "peu_favorable",
        "indetermine",
    }
    assert body["soil_moisture"]["kind"] == "modelled_indicator"
    assert body["agronomic_cultivability"]["status"] == "non_evaluee"
    assert body["limits"]


def test_prediction_never_favorable_with_unvalidated_profile(client):  # P-07
    level = client.post("/api/v1/predictions", json=PRED).json()["meteorological_favorability"]["level"]
    assert level != "favorable"


def test_prediction_unknown_crop(client):  # A-04
    r = client.post("/api/v1/predictions", json={**PRED, "crop_id": "inconnue"})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CROP_NOT_FOUND"


@pytest.mark.parametrize(
    ("patch", "code"),
    [
        ({"location": {"latitude": 99, "longitude": 0}}, "VALIDATION_ERROR"),
        ({"window_days": 3}, "VALIDATION_ERROR"),
        ({"reference_date": "2999-01-01"}, "DATE_OUT_OF_RANGE"),
    ],
)
def test_prediction_422(client, patch, code):  # A-04
    r = client.post("/api/v1/predictions", json={**PRED, **patch})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == code


def test_prediction_indeterminate_when_data_insufficient(client, monkeypatch):  # D-04, P-03
    class Sparse(FixtureProvider):
        def daily(self, latitude, longitude, start, end):
            return [r for i, r in enumerate(super().daily(latitude, longitude, start, end)) if i % 2 == 0]

    monkeypatch.setitem(providers.REGISTRY, "fixture", Sparse())
    body = client.post("/api/v1/predictions", json=PRED).json()
    assert body["meteorological_favorability"]["level"] == "indetermine"
    assert "insuffisantes" in body["meteorological_favorability"]["summary"]
    assert body["data_quality"]["completeness_pct"]["precipitation_mm"] < 80


# ---------- fournisseur en panne (A-05) ----------
@pytest.mark.parametrize(
    ("error", "status", "code"),
    [
        (errors.ProviderUnavailable, 502, "PROVIDER_UNAVAILABLE"),
        (errors.ProviderRateLimited, 503, "PROVIDER_RATE_LIMITED"),
        (errors.ProviderTimeout, 504, "PROVIDER_TIMEOUT"),
    ],
)
@pytest.mark.parametrize("endpoint", ["weather", "indicators", "predictions", "geocode"])
def test_provider_failures(client, monkeypatch, error, status, code, endpoint):
    class Down(FixtureProvider):
        def daily(self, *a):
            raise error()

        def geocode(self, *a):
            raise error()

    monkeypatch.setitem(providers.REGISTRY, "fixture", Down())
    if endpoint == "predictions":
        r = client.post("/api/v1/predictions", json=PRED)
    elif endpoint == "geocode":
        r = client.get("/api/v1/geocode", params={"q": "dakar"})
    else:
        params = {**LOC, "start_date": "2026-10-01", "end_date": REF, "reference_date": REF}
        r = client.get(f"/api/v1/{endpoint}", params=params)
    body = r.json()
    assert r.status_code == status
    assert body["error"]["code"] == code
    assert "Traceback" not in r.text and body["request_id"]


def test_unexpected_error_hides_trace(client, monkeypatch):
    class Broken(FixtureProvider):
        def daily(self, *a):
            raise RuntimeError("secret interne")

    monkeypatch.setitem(providers.REGISTRY, "fixture", Broken())
    r = client.post("/api/v1/predictions", json=PRED)
    assert r.status_code == 500
    assert r.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "secret interne" not in r.text


# ---------- cache (D-06) ----------
def test_second_identical_call_is_served_from_cache(client, monkeypatch):
    calls = []

    class Counting(FixtureProvider):
        def daily(self, *a):
            calls.append(a)
            return super().daily(*a)

    monkeypatch.setitem(providers.REGISTRY, "fixture", Counting())
    params = {**LOC, "start_date": "2026-10-01", "end_date": REF}
    first = client.get("/api/v1/weather", params=params).json()["daily"]
    second = client.get("/api/v1/weather", params=params).json()["daily"]
    assert first == second
    assert len(calls) == 1


# ---------- verdicts de bout en bout (profils de test) ----------
def _weather_provider(monkeypatch, rain):
    class Fixed(FixtureProvider):
        def daily(self, latitude, longitude, start, end):
            return [
                r.model_copy(update={"precipitation_mm": rain})
                for r in super().daily(latitude, longitude, start, end)
            ]

    monkeypatch.setitem(providers.REGISTRY, "fixture", Fixed())


def _level(client, crop_id):
    body = client.post("/api/v1/predictions", json={**PRED, "crop_id": crop_id}).json()
    return body["meteorological_favorability"]["level"], body


def test_rainy_window_with_validated_profile_is_favorable(client, monkeypatch):
    _weather_provider(monkeypatch, 12.0)
    level, body = _level(client, "test_valide")
    assert level == "favorable" and body["confidence"]["level"] == "moyenne"
    assert all(c["status"] == "ok" for c in body["meteorological_favorability"]["criteria"])


def test_same_window_with_unvalidated_profile_is_capped(client, monkeypatch):  # P-07
    _weather_provider(monkeypatch, 12.0)
    assert _level(client, "test_a")[0] == "favorable_sous_reserve"


def test_dry_window_is_unfavorable_and_explained(client, monkeypatch):  # P-04, P-05
    _weather_provider(monkeypatch, 0.0)
    level, body = _level(client, "test_valide")
    assert level == "peu_favorable"
    assert "seuil défavorable franchi" in body["meteorological_favorability"]["summary"]


def test_crops_come_from_profile_files(client):
    ids = {c["id"] for c in client.get("/api/v1/crops").json()["crops"]}
    assert ids == {"test_a", "test_valide"}
