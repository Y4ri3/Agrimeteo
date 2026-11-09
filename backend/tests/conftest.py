import pytest
from fastapi.testclient import TestClient

from app import providers
from app.core import config
from app.main import app


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Aucun test ne touche au cache réel ni au réseau (cache temporaire, fournisseur fixture)."""
    monkeypatch.setattr(config, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(config, "WEATHER_PROVIDER", "fixture")
    monkeypatch.setitem(providers.REGISTRY, "fixture", providers.FixtureProvider())


@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)
