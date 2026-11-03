from agrimeteo_ml.schema import CANONICAL_COLUMNS


def test_canonical_columns_start_with_date():
    assert CANONICAL_COLUMNS[0] == "date"
    assert len(set(CANONICAL_COLUMNS)) == len(CANONICAL_COLUMNS)
