"""D-01 : chaque fournisseur rend exactement les colonnes du schéma commun, avec les bons types."""

from datetime import date

import httpx
import pytest
from agrimeteo_ml.schema import CANONICAL_COLUMNS

from app.providers.csv_file import CsvProvider
from app.providers.fixture import FixtureProvider
from app.providers.open_meteo import OpenMeteoProvider
from app.schemas.weather import DailyRecord
from tests.test_csv import HEADER, ROWS
from tests.test_open_meteo import ARCHIVE


def _csv(tmp_path):
    f = tmp_path / "m.csv"
    f.write_text(HEADER + ROWS, encoding="utf-8")
    return CsvProvider(str(f))


def _open_meteo(_):
    return OpenMeteoProvider(
        httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=ARCHIVE)))
    )


@pytest.mark.parametrize(
    "make", [lambda _: FixtureProvider(), _open_meteo, _csv], ids=["fixture", "open_meteo", "csv"]
)
def test_every_provider_returns_the_common_schema(make, tmp_path):
    records = make(tmp_path).daily(14.7, -17.4, date(2025, 10, 1), date(2025, 10, 3))
    assert records, "le fournisseur doit rendre des jours"
    assert set(DailyRecord.model_fields) == set(CANONICAL_COLUMNS)
    for r in records:
        assert isinstance(r.date, date)
        for column in CANONICAL_COLUMNS[1:]:
            assert getattr(r, column) is None or isinstance(getattr(r, column), float | int)
