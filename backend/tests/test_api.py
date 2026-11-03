"""Tests du contrat (A-01, A-03, A-06, A-07, A-08). Ils vérifient le comportement visible, pas le stub."""

REF = "2026-10-21"
LOC = {"latitude": 14.7, "longitude": -17.4}


def test_health(client):  # A-01
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_validation_error_format(client):  # A-03
    r = client.get(
        "/api/v1/weather", params={"latitude": 200, "longitude": 0, "start_date": REF, "end_date": REF}
    )
    body = r.json()
    assert r.status_code == 422
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["request_id"]


def test_period_too_long(client):  # A-03
    r = client.get("/api/v1/weather", params={**LOC, "start_date": "2024-01-01", "end_date": "2026-01-01"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "PERIOD_TOO_LONG"


def test_weather_marks_missing_values(client):
    r = client.get("/api/v1/weather", params={**LOC, "start_date": "2026-10-01", "end_date": REF})
    q = r.json()["quality"]
    assert r.status_code == 200
    assert q["missing_days"] == len(q["flagged_values"])  # une valeur manquante reste null, jamais 0


def test_geocode_empty_list_is_not_an_error(client):  # A-07
    r = client.get("/api/v1/geocode", params={"q": "zzzzzz"})
    assert r.status_code == 200
    assert r.json() == {"results": []}


def test_crops_listed(client):  # A-07
    assert len(client.get("/api/v1/crops").json()["crops"]) >= 1


def test_prediction_returns_three_distinct_blocks(client):  # A-06
    r = client.post(
        "/api/v1/predictions", json={"location": LOC, "crop_id": "culture_exemple_a", "reference_date": REF}
    )
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


def test_prediction_unknown_crop(client):
    r = client.post("/api/v1/predictions", json={"location": LOC, "crop_id": "inconnue"})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CROP_NOT_FOUND"


def test_indicators_match_prediction(client):  # A-08
    ind = client.get("/api/v1/indicators", params={**LOC, "reference_date": REF}).json()["indicators"]
    pred = client.post(
        "/api/v1/predictions", json={"location": LOC, "crop_id": "culture_exemple_a", "reference_date": REF}
    ).json()["indicators"]
    assert ind == pred
