"""Fournisseur Open-Meteo, avec un transport HTTP simulé : aucun accès réseau (D-05)."""

from datetime import date

import httpx
import pytest

from app import providers
from app.core import errors
from app.providers.open_meteo import OpenMeteoProvider

ARCHIVE = {
    "daily": {
        "time": ["2025-10-01", "2025-10-02", "2025-10-03"],
        "precipitation_sum": [0.0, None, 12.4],
        "temperature_2m_min": [22.1, 22.4, 21.9],
        "temperature_2m_max": [31.0, 30.5, 29.8],
        "relative_humidity_2m_mean": [70, 72, 80],
        "et0_fao_evapotranspiration": [5.1, 5.0, 4.2],
    }
}


def provider(handler):
    return OpenMeteoProvider(httpx.Client(transport=httpx.MockTransport(handler)))


def test_daily_maps_to_common_schema_and_keeps_missing_as_null():  # D-01, D-03
    seen = {}

    def handler(request):
        seen.update(dict(request.url.params))
        return httpx.Response(200, json=ARCHIVE)

    records = provider(handler).daily(14.69, -17.44, date(2025, 10, 1), date(2025, 10, 3))
    assert [r.date for r in records] == [date(2025, 10, d) for d in (1, 2, 3)]
    assert records[1].precipitation_mm is None  # jamais remplacé par 0
    assert records[2].precipitation_mm == 12.4 and records[2].rh_mean_pct == 80 and records[2].et0_mm == 4.2
    assert records[0].tmin_c == 22.1 and records[0].tmax_c == 31.0
    assert seen["start_date"] == "2025-10-01" and "et0_fao_evapotranspiration" in seen["daily"]


def test_geocode_parses_results_and_handles_none():
    def handler(request):
        if request.url.params["name"] == "rien":
            return httpx.Response(200, json={"generationtime_ms": 0.1})  # pas de clé "results"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "name": "Kaolack",
                        "country": "Sénégal",
                        "admin1": "Kaolack",
                        "latitude": 14.15,
                        "longitude": -16.07,
                    }
                ]
            },
        )

    p = provider(handler)
    assert p.geocode("kaolack", 5, "fr")[0].name == "Kaolack"
    assert p.geocode("rien", 5, "fr") == []  # A-07


@pytest.mark.parametrize(
    ("response", "error"),
    [
        (httpx.Response(429), errors.ProviderRateLimited),
        (httpx.Response(500), errors.ProviderUnavailable),
        (httpx.Response(503), errors.ProviderUnavailable),
        (httpx.Response(200, text="pas du json"), errors.ProviderUnavailable),
        (httpx.Response(200, json={"error": True}), errors.ProviderUnavailable),
    ],
)
def test_http_failures_become_provider_errors(response, error):  # A-05
    with pytest.raises(error):
        provider(lambda request: response).daily(0, 0, date(2025, 10, 1), date(2025, 10, 3))


def test_timeout_and_network_errors():  # A-05
    def timeout(request):
        raise httpx.ReadTimeout("lent")

    def down(request):
        raise httpx.ConnectError("injoignable")

    with pytest.raises(errors.ProviderTimeout):
        provider(timeout).daily(0, 0, date(2025, 10, 1), date(2025, 10, 3))
    with pytest.raises(errors.ProviderUnavailable):
        provider(down).geocode("x", 1, "fr")


def test_open_meteo_is_selectable_through_the_api(client, monkeypatch):
    monkeypatch.setitem(
        providers.REGISTRY, "open_meteo", provider(lambda request: httpx.Response(200, json=ARCHIVE))
    )
    r = client.get(
        "/api/v1/weather",
        params={
            "latitude": 14.7,
            "longitude": -17.4,
            "start_date": "2025-10-01",
            "end_date": "2025-10-03",
            "source": "open_meteo",
        },
    )
    body = r.json()
    assert r.status_code == 200
    assert body["source"]["attribution"] == "Weather data by Open-Meteo.com"  # FE-06
    assert body["daily"][2]["precipitation_mm"] == 12.4


def test_exact_coordinates_never_reach_the_logs(client, caplog, monkeypatch):  # cahier 9.9
    import logging

    monkeypatch.setitem(
        providers.REGISTRY, "open_meteo", provider(lambda request: httpx.Response(200, json=ARCHIVE))
    )
    with caplog.at_level(logging.INFO):
        client.get(
            "/api/v1/weather",
            params={
                "latitude": 14.69371,
                "longitude": -17.44406,
                "start_date": "2025-10-01",
                "end_date": "2025-10-03",
                "source": "open_meteo",
            },
        )
    assert "14.69371" not in caplog.text and "17.44406" not in caplog.text


def test_source_keeps_license_and_retrieval_date(client, monkeypatch):  # cahier 7.2
    monkeypatch.setitem(
        providers.REGISTRY, "open_meteo", provider(lambda request: httpx.Response(200, json=ARCHIVE))
    )
    params = {
        "latitude": 1.5,
        "longitude": 2.5,
        "start_date": "2025-10-01",
        "end_date": "2025-10-03",
        "source": "open_meteo",
    }
    first = client.get("/api/v1/weather", params=params).json()["source"]
    again = client.get("/api/v1/weather", params=params).json()["source"]  # servi par le cache
    assert first["license"] == "CC BY 4.0" and first["retrieved_at"]
    assert again["retrieved_at"] and again["license"] == "CC BY 4.0"
