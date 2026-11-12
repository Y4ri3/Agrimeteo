import pytest
from fastapi.testclient import TestClient

from app import providers
from app.core import config
from app.main import app

PROFILE = """\
id: {id}
label: Culture de test {id}
version: 0.0.1
status: {status}
criteria:
  - id: pluie
    label: Pluie cumulée
    indicator: rain_sum
    window_days: 7
    unit: mm
    direction: lower_is_worse
    blocking: true
    thresholds: {{ vigilance: 40, unfavorable: 10 }}
    source: test
  - id: secheresse
    label: Plus longue période sans pluie
    indicator: max_dry_spell
    window_days: 7
    unit: jours
    direction: higher_is_worse
    blocking: true
    thresholds: {{ vigilance: 6, unfavorable: 7 }}
    source: test
"""


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Aucun test ne touche au cache réel, aux vrais profils ni au réseau (profils et cache temporaires)."""
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "test_a.yaml").write_text(PROFILE.format(id="test_a", status="a_valider"), encoding="utf-8")
    (rules / "test_valide.yaml").write_text(PROFILE.format(id="test_valide", status="valide_par_source"))
    monkeypatch.setattr(config, "RULES_DIR", str(rules))
    monkeypatch.setattr(config, "CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(config, "WEATHER_PROVIDER", "fixture")
    monkeypatch.setitem(providers.REGISTRY, "fixture", providers.FixtureProvider())


@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)
